import os
import django
from faker import Faker

# Убедитесь, что вы находитесь в правильном окружении Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carpetxls.settings')
django.setup()

from clients.models import Client  # Замените 'your_app_name' на имя вашего приложения

def create_clients(num_clients=10):
    fake = Faker('ru_RU')  # Используем русский язык для генерации данных

    for _ in range(num_clients):
        phone_number = f"+79{fake.msisdn()[4:]}"  # Генерация номера телефона в формате +79001234567
        fio = fake.name()
        comment = fake.text(max_nb_chars=100)
        city = "г Воронеж"
        street = fake.street_name()
        home = str(fake.building_number())
        apartment = str(fake.building_number()) if fake.boolean() else None
        entrance = str(fake.random_int(min=1, max=10)) if fake.boolean() else None
        organization = fake.boolean()

        client = Client(
            phone_number=phone_number,
            fio=fio,
            comment=comment,
            city=city,
            street=street,
            home=home,
            apartment=apartment,
            entrance=entrance,
            organization=organization
        )
        client.save()

if __name__ == '__main__':
    print("Заполняем базу данных клиентами...")
    create_clients(100)  # Количество клиентов для создания
    print("База данных заполнена.")