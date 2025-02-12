from django.contrib.auth.models import User
from django.utils.timezone import now
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Shift, PaymentMethod, Receipt, Refund, CashExpense
from orders.models import Order, Stage
from clients.models import Client

class ShiftModelTest(TestCase):
    def setUp(self):
        # Создаем тестовые данные перед каждым тестом
        self.open_shift = Shift.objects.create(status='open', initial_cash=1000)

    def test_create_open_shift(self):
        """Тест создания открытой смены."""
        shift = Shift.objects.create(status='open', initial_cash=500)
        self.assertEqual(shift.status, 'open')
        self.assertEqual(shift.initial_cash, 500)
        self.assertIsNone(shift.closing_time)
        self.assertIsNone(shift.final_cash)

    def test_only_one_open_shift_allowed(self):
        """Тест, что может быть только одна открытая смена."""
        new_shift = Shift(status='open', initial_cash=200)
        with self.assertRaises(ValidationError):
            new_shift.full_clean()

    def test_close_shift(self):
        """Тест закрытия смены."""
        self.open_shift.status = 'closed'
        self.open_shift.save()
        self.assertIsNotNone(self.open_shift.closing_time)
        self.assertEqual(self.open_shift.final_cash, self.open_shift.total_cash)

    def test_initial_cash_from_previous_shift(self):
        """Тест автоматического заполнения начальной суммы из предыдущей закрытой смены."""
        first_shift = self.open_shift
        first_shift.total_cash = 1500
        first_shift.save()
        first_shift.status = 'closed'
        first_shift.final_cash = 1500
        first_shift.closing_time = now()
        first_shift.save()
        new_shift = Shift.objects.create(status='open')
        self.assertEqual(new_shift.initial_cash, 1500)
        self.assertEqual(new_shift.total_cash, 1500)

    def test_initial_cash_without_previous_shift(self):
        """Тест начальной суммы без предыдущей смены."""
        shift = Shift.objects.create(status='open')
        self.assertEqual(shift.initial_cash, 0)
        self.assertEqual(shift.total_cash, 0)

    def test_validation_on_creating_closed_shift(self):
        """Тест, что нельзя создать новую смену со статусом 'closed'."""
        shift = Shift(status='closed', initial_cash=300)
        with self.assertRaises(ValidationError):
            shift.full_clean()

    def test_reopening_closed_shift(self):
        """Тест, что нельзя изменить закрытую смену на открытую."""
        self.open_shift.status = 'closed'
        self.open_shift.save()
        reopened_shift = Shift.objects.get(id=self.open_shift.id)
        reopened_shift.status = 'open'
        with self.assertRaises(ValidationError):
            reopened_shift.full_clean()

    def test_update_total_expenses(self):
        """Тест обновления total_expenses при добавлении расхода."""
        self.open_shift.total_cash = 100
        self.open_shift.save()
        user = User.objects.create_user(username='testuser')
        expense = self.open_shift.cash_expenses.create(user=user, amount=50)
        self.open_shift.refresh_from_db()
        self.assertEqual(self.open_shift.total_expenses, 50)
        self.assertEqual(self.open_shift.total_cash, 50)

    def test_insufficient_funds_for_expense(self):
        """Тест, что нельзя создать расход, если недостаточно средств."""
        self.open_shift.total_cash = 40
        self.open_shift.save()
        user = User.objects.create_user(username='testuser')
        with self.assertRaises(ValidationError) as context:
            self.open_shift.cash_expenses.create(user=user, amount=50)
        self.assertIn("Недостаточно наличных средств в смене для данного расхода.", str(context.exception))


class ReceiptModelTest(TestCase):
    def setUp(self):
        # Создаем необходимые объекты перед каждым тестом
        self.user = User.objects.create_user(username='testuser')
        self.open_shift = Shift.objects.create(status='open', initial_cash=1000)
        self.client = Client.objects.create(phone_number='+79991234567', fio='Test Client')
        self.valid_stage = Stage.objects.create(name="Valid Stage", group_stage=7)
        self.invalid_stage = Stage.objects.create(name="Invalid Stage", group_stage=6)

    def test_create_receipt_with_valid_order_stage(self):
        """Тест создания чека для заказа с допустимым статусом."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        self.assertEqual(receipt.amount, 500)
        self.assertEqual(receipt.shift.total_cash, 1500)  # 1000 начальных + 500 из чека
        self.assertEqual(receipt.shift.total_sales, 500)

    def test_create_receipt_with_invalid_order_stage(self):
        """Тест, что нельзя создать чек для заказа с недопустимым статусом."""
        order = Order.objects.create(stage=self.invalid_stage, client=self.client, order_sum=500)
        with self.assertRaises(ValidationError):
            Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)

    def test_create_receipt_without_open_shift(self):
        """Тест, что нельзя создать чек без открытой смены."""
        self.open_shift.status = 'closed'
        self.open_shift.save()
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        with self.assertRaises(ValidationError):
            Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)

    def test_edit_receipt(self):
        """Тест, что нельзя редактировать существующий чек."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        receipt.amount = 600
        with self.assertRaises(ValidationError):
            receipt.save()

    def test_receipt_amount_from_order_sum(self):
        """Тест автоматического заполнения суммы чека из заказа."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=750)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        self.assertEqual(receipt.amount, 750)

    def test_receipt_auto_assigns_open_shift(self):
        """Тест автоматического привязывания открытой смены к чеку."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        self.assertIsNotNone(receipt.shift)
        self.assertEqual(receipt.shift.status, 'open')

    def test_receipt_updates_shift_totals(self):
        """Тест обновления total_sales и total_cash в смене после создания чека."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=300)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        self.open_shift.refresh_from_db()  # Обновляем объект смены из базы данных
        self.assertEqual(self.open_shift.total_sales, 300)  # Проверяем total_sales
        self.assertEqual(self.open_shift.total_cash, 1300)  # 1000 начальных + 300 из чека

    def test_receipt_creation_fails_if_no_open_shift_exists(self):
        """Тест, что создание чека невозможно, если нет открытой смены."""
        self.open_shift.status = 'closed'
        self.open_shift.save()
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        with self.assertRaises(ValidationError):
            Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)

    def test_receipt_cannot_be_created_for_refunded_order(self):
        """Тест, что нельзя создать новый чек для заказа, по которому уже есть возврат."""
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)
        Refund.objects.create(receipt=receipt, amount=500)
        with self.assertRaises(ValidationError):
            Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)


class RefundModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.open_shift = Shift.objects.create(status='open', initial_cash=1000)
        self.client = Client.objects.create(phone_number='+79991234567', fio='Test Client')
        self.valid_stage = Stage.objects.create(name="Valid Stage", group_stage=7)
        self.order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        self.receipt = Receipt.objects.create(order=self.order, payment_method=PaymentMethod.CASH)

    def test_create_refund_with_sufficient_funds(self):
        """Тест успешного создания возврата при достаточном количестве средств."""
        # Создаем заказ и чек
        order = Order.objects.create(stage=self.valid_stage, client=self.client, order_sum=500)
        receipt = Receipt.objects.create(order=order, payment_method=PaymentMethod.CASH)

        # Проверяем начальный баланс смены
        self.assertEqual(self.open_shift.total_cash, 1500)  # 1000 начальных + 500 из чека

        # Создаем возврат
        refund = Refund.objects.create(receipt=receipt, amount=300)

        # Проверяем обновленный баланс смены
        self.open_shift.refresh_from_db()  # Обновляем объект смены из базы данных
        self.assertEqual(self.open_shift.total_cash, 700)  # 1500 - 300 = 1200
        self.assertEqual(self.open_shift.total_refunds, 300)

    def test_create_refund_with_insufficient_funds(self):
        """Тест, что нельзя сделать возврат, если недостаточно средств."""
        # Установка начального баланса смены
        self.open_shift.total_cash = 400
        self.open_shift.save()

        # Убедимся, что метод оплаты чека - наличные
        self.receipt.payment_method = PaymentMethod.CASH
        self.receipt.save()

        # Попытка создания возврата с суммой, превышающей наличные средства
        with self.assertRaises(ValidationError) as context:
            Refund.objects.create(receipt=self.receipt, amount=500)

        # Проверка текста ошибки
        self.assertIn(
            "Недостаточно наличных средств в смене для данного возврата.",
            str(context.exception)
        )

    def test_create_refund_for_closed_shift(self):
        """Тест, что нельзя сделать возврат для закрытой смены."""
        self.open_shift.status = 'closed'
        self.open_shift.save()

        # Ensure the receipt's shift is updated
        self.receipt.shift.refresh_from_db()
        self.assertEqual(self.receipt.shift.status, 'closed')

        refund = Refund(receipt=self.receipt, amount=200)
        with self.assertRaises(ValidationError):
            refund.full_clean()

    def test_refund_updates_non_cash_balance(self):
        """Тест обновления баланса безналичных средств при возврате."""
        self.receipt.payment_method = PaymentMethod.CARD
        self.receipt.save()
        refund = Refund.objects.create(receipt=self.receipt, amount=200)
        self.assertEqual(refund.shift.total_non_cash, 0)  # Начальный баланс безналичных был 0


class CashExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.open_shift = Shift.objects.create(status='open', initial_cash=1000)

    def test_create_cash_expense(self):
        """Тест создания расхода."""
        expense = CashExpense.objects.create(user=self.user, shift=self.open_shift, amount=300)
        self.assertEqual(expense.shift.total_cash, 700)
        self.assertEqual(expense.shift.total_expenses, 300)

    def test_create_cash_expense_with_negative_amount(self):
        """Тест, что нельзя создать расход с отрицательной суммой."""
        with self.assertRaises(ValidationError):
            CashExpense.objects.create(user=self.user, shift=self.open_shift, amount=-100)

    def test_create_cash_expense_with_insufficient_funds(self):
        """Тест, что нельзя создать расход, если недостаточно средств."""
        self.open_shift.total_cash = 200
        self.open_shift.save()
        with self.assertRaises(ValidationError):
            CashExpense.objects.create(user=self.user, shift=self.open_shift, amount=300)

    def test_create_cash_expense_for_closed_shift(self):
        """Тест, что нельзя создать расход для закрытой смены."""
        self.open_shift.status = 'closed'
        self.open_shift.save()
        with self.assertRaises(ValidationError):
            CashExpense.objects.create(user=self.user, shift=self.open_shift, amount=300)

    def test_edit_cash_expense(self):
        """Тест, что нельзя редактировать существующий расход."""
        expense = CashExpense.objects.create(user=self.user, shift=self.open_shift, amount=300)
        expense.amount = 400
        with self.assertRaises(ValidationError):
            expense.save()