import os
import random
from decimal import Decimal
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carpetxls.settings')  # Замените на ваш путь к файлу настроек
# Инициализируем Django
django.setup()

# Импортируем необходимые модели и другие зависимости
from django.contrib.auth.models import User
from clients.models import Client
from orders.models import Order, Product, ProductAdd, ProductOrder, Stage, SecondProductOrder, SecondProduct

# Функция для генерации случайного числа с плавающей точкой
def random_decimal(min_val, max_val, decimal_places=2):
    return Decimal(str(round(random.uniform(min_val, max_val), decimal_places)))

# Функция для выбора случайного элемента из списка
def random_choice(seq):
    if seq:
        return random.choice(seq)
    return None

# Функция для генерации случайной даты за последние 3 месяца
def random_date_last_3_months():
    now = timezone.now()
    start_date = now - timedelta(days=90)  # 3 месяца назад
    random_days = random.randint(0, (now - start_date).days)
    return start_date + timedelta(days=random_days)

# Генерация данных для модели Order
def create_orders(num_orders=10):
    clients = list(Client.objects.all())
    products = list(Product.objects.all())
    product_adds = list(ProductAdd.objects.all())
    stages = list(Stage.objects.all())
    second_products = list(SecondProduct.objects.all())

    for _ in range(num_orders):
        # Выбираем случайного клиента
        client = random_choice(clients)
        if not client:
            raise ValueError("Нет доступных клиентов в базе данных.")

        # Проверяем, что клиент не создавал заказы за последние 5 минут
        recent_orders = Order.objects.filter(
            client=client,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        if recent_orders:
            print(f"Пропускаем создание заказа для клиента {client} из-за временного ограничения.")
            continue

        # Создаем заказ
        try:
            order = Order.objects.create(
                client=client,
                target_date=None,  # Можно задать случайную дату или оставить пустым
                comment="",
                check_call=random.choice([True, False]),
                stage=random_choice(stages),
                create_date=random_date_last_3_months()  # Случайная дата за последние 3 месяца
            )
        except ValidationError as e:
            print(f"Ошибка при создании заказа: {e}")
            continue

        # Определяем количество ProductOrder для данного заказа (от 1 до 5)
        num_product_orders = random.randint(1, 5)
        for _ in range(num_product_orders):
            # Выбираем случайный продукт
            product = random_choice(products)
            # Задаем случайные размеры width и height
            width = random_decimal(1.0, 3.0)
            height = random_decimal(1.0, 3.0)
            # Создаем объект ProductOrder
            product_order = ProductOrder.objects.create(
                order_id=order,
                product=product,
                width=width,
                height=height,
                overlock=0,
                allowance=0,
                comment=""
            )
            # Выбираем от 0 до 2 случайных доп. услуг
            num_product_adds = random.randint(0, 2)
            selected_product_adds = random.sample(product_adds, num_product_adds) if num_product_adds > 0 else []
            set_product_add(product_order, selected_product_adds)
            # В 10% случаев задаем поле overlock
            if random.random() < 0.1:
                product_order.overlock = random_decimal(100, 500)
                product_order.save()
            # В 10% случаев задаем поле allowance
            if random.random() < 0.1:
                product_order.allowance = random_decimal(50, 500)
                product_order.save()

        # Добавляем случайное количество вторичных продуктов (от 0 до 2)
        num_second_product_orders = random.randint(0, 2)
        for _ in range(num_second_product_orders):
            second_product = random_choice(second_products)
            second_amount = random_decimal(1.0, 10.0)
            SecondProductOrder.objects.create(
                order_id=order,
                product=second_product,
                second_amount=second_amount
            )

        # Пересчитываем сумму заказа, вызывая сигнал pre_save
        order.save()

# Функция для установки доп. услуг в ProductOrder
def set_product_add(instance, product_add_list):
    if instance.pk is None:
        # Если объект еще не сохранен, временно храним связанные объекты
        instance._temp_product_add = product_add_list
    else:
        # Если объект уже сохранен, можно сразу установить связи Many-to-Many
        instance.product_add.set(product_add_list)
        instance.update_message()  # Пересчитываем стоимость и обновляем сообщение
        instance.save()

if __name__ == "__main__":
    # Убедитесь, что у вас есть данные в базе данных для Client, Product, ProductAdd, Stage и SecondProduct
    create_orders(num_orders=30)  # Например, создаем 812 заказов