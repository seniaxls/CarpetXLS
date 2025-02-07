from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import site as admin_site
from .models import (
    Order, ProductOrder, SecondProductOrder, Product, SecondProduct, Stage, Client
)

class OrderAdminTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)

        # Создаем тестовые данные
        self.stage, _ = Stage.objects.get_or_create(
            name="Лид", defaults={"group_stage": 1, "super_stage": False}
        )
        self.client_obj = Client.objects.create(
            phone_number="+79001234567",
            fio="Иван Иванов",
            comment="Тестовый клиент"
        )
        self.order = Order.objects.create(
            order_number="12345",
            stage=self.stage,
            client=self.client_obj,
            user=self.user,
            comment="Тестовый заказ"
        )
        self.product = Product.objects.create(
            product_name="Короткий ворс",
            product_unit=None,
            product_price=150
        )
        self.second_product = SecondProduct.objects.create(
            product_name="Стирка пледа",
            product_unit=None,
            product_price=100
        )

        # Получаем зарегистрированный админ-класс для модели Order
        self.admin = admin_site._registry[Order]

    def tearDown(self):
        # Очищаем базу данных после каждого теста
        ProductOrder.objects.all().delete()
        SecondProductOrder.objects.all().delete()
        Order.objects.all().delete()
        Client.objects.all().delete()
        Stage.objects.all().delete()

    def test_save_formset_with_product_order(self):
        data = {
            "productorder_set-TOTAL_FORMS": "1",
            "productorder_set-INITIAL_FORMS": "0",
            "productorder_set-0-order_id": self.order.id,
            "productorder_set-0-product": self.product.id,
            "productorder_set-0-width": 2.5,
            "productorder_set-0-height": 3.0,
            "productorder_set-0-comment": "Тестовый комментарий",
        }
        url = reverse("admin:orders_order_change", args=[self.order.id])
        request = RequestFactory().post(url, data=data)
        request.user = self.user

        formsets_with_inlines = list(self.admin.get_formsets_with_inlines(request))
        formset = formsets_with_inlines[0][0](data, instance=self.order)  # Первый inline - ProductOrder
        self.admin.save_formset(request, None, formset, change=True)

        product_order = ProductOrder.objects.first()
        self.assertEqual(product_order.history.first().history_user, self.user)

    def test_save_formset_with_second_product_order(self):
        data = {
            "secondproductorder_set-TOTAL_FORMS": "1",
            "secondproductorder_set-INITIAL_FORMS": "0",
            "secondproductorder_set-0-order_id": self.order.id,
            "secondproductorder_set-0-product": self.second_product.id,
            "secondproductorder_set-0-second_amount": 5.0,
        }
        url = reverse("admin:orders_order_change", args=[self.order.id])
        request = RequestFactory().post(url, data=data)
        request.user = self.user

        formsets_with_inlines = list(self.admin.get_formsets_with_inlines(request))
        formset = formsets_with_inlines[1][0](data, instance=self.order)  # Второй inline - SecondProductOrder
        self.admin.save_formset(request, None, formset, change=True)

        second_product_order = SecondProductOrder.objects.first()
        self.assertEqual(second_product_order.history.first().history_user, self.user)

    def test_history_user_not_set_for_non_historical_models(self):
        data = {
            "client-TOTAL_FORMS": "1",
            "client-INITIAL_FORMS": "0",
            "client-0-phone_number": "+79001234567",
            "client-0-fio": "Петр Петров",
            "client-0-comment": "Тестовый клиент",
        }
        url = reverse("admin:orders_order_change", args=[self.order.id])
        request = RequestFactory().post(url, data=data)
        request.user = self.user

        formsets_with_inlines = list(self.admin.get_formsets_with_inlines(request))
        formset = formsets_with_inlines[2][0](data, instance=self.order)
        self.admin.save_formset(request, None, formset, change=True)

        client = Client.objects.first()
        self.assertFalse(hasattr(client, 'history'))

    def test_save_formset_with_multiple_instances(self):
        data = {
            "productorder_set-TOTAL_FORMS": "2",
            "productorder_set-INITIAL_FORMS": "0",
            "productorder_set-0-order_id": self.order.id,
            "productorder_set-0-product": self.product.id,
            "productorder_set-0-width": 2.5,
            "productorder_set-0-height": 3.0,
            "productorder_set-0-comment": "Тестовый комментарий",
            "productorder_set-1-order_id": self.order.id,
            "productorder_set-1-product": self.product.id,
            "productorder_set-1-width": 4.0,
            "productorder_set-1-height": 5.0,
            "productorder_set-1-comment": "Второй тестовый комментарий",
        }
        url = reverse("admin:orders_order_change", args=[self.order.id])
        request = RequestFactory().post(url, data=data)
        request.user = self.user

        formsets_with_inlines = list(self.admin.get_formsets_with_inlines(request))
        formset = formsets_with_inlines[0][0](data, instance=self.order)
        self.admin.save_formset(request, None, formset, change=True)

        for product_order in ProductOrder.objects.all():
            self.assertEqual(product_order.history.first().history_user, self.user)