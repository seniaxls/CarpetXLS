from django.test import TestCase
from clients.models import Client
from django.core.exceptions import ValidationError

class ClientModelTest(TestCase):
    def setUp(self):
        # Создаем тестового клиента для использования в тестах
        self.client_data = {
            'phone_number': '+79123456789',
            'fio': 'Иванов Иван Иванович',
            'city': 'г Воронеж',
            'street': 'Ленина',
            'home': '10',
            'apartment': '5',
            'entrance': '2',
            'comment': 'Тестовый комментарий'
        }

    def test_create_client(self):
        """Тестирование создания клиента."""
        client = Client.objects.create(**self.client_data)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(client.phone_number, '+79123456789')
        self.assertEqual(client.fio, 'Иванов Иван Иванович')

    def test_phone_number_validation_valid(self):
        """Тестирование валидации корректного номера телефона."""
        client = Client(phone_number='+79123456789', fio='Иванов Иван Иванович')
        client.full_clean()  # Проверяем, что не возникает ошибок валидации

    def test_phone_number_validation_invalid(self):
        """Тестирование валидации некорректного номера телефона."""
        client = Client(phone_number='invalid_phone', fio='Иванов Иван Иванович')
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_phone_number_uniqueness(self):
        """Тестирование уникальности номера телефона."""
        Client.objects.create(phone_number='+79123456789', fio='Иванов Иван Иванович')
        with self.assertRaises(ValidationError):
            client = Client(phone_number='+79123456789', fio='Петров Петр Петрович')
            client.full_clean()

    def test_address_generation_full(self):
        """Тестирование автоматической генерации поля address с полным набором данных."""
        client = Client.objects.create(**self.client_data)
        expected_address = "г Воронеж, Ленина, 10, кв 5, под 2"
        self.assertEqual(client.address, expected_address)

    def test_address_generation_partial(self):
        """Тестирование автоматической генерации поля address с частичным набором данных."""
        client_data = {
            'phone_number': '+79123456789',
            'fio': 'Иванов Иван Иванович',
            'city': 'г Воронеж',
            'street': 'Ленина',
            'home': '10'
        }
        client = Client.objects.create(**client_data)
        expected_address = "г Воронеж, Ленина, 10"
        self.assertEqual(client.address, expected_address)

    def test_address_update_on_save(self):
        """Тестирование обновления адреса при изменении данных."""
        client = Client.objects.create(**self.client_data)
        client.city = 'г Москва'
        client.street = 'Арбат'
        client.home = '15'
        client.apartment = '10'
        client.entrance = '3'
        client.save()
        expected_address = "г Москва, Арбат, 15, кв 10, под 3"
        self.assertEqual(client.address, expected_address)

    def test_optional_fields(self):
        """Тестирование работы с необязательными полями."""
        client = Client.objects.create(
            phone_number='+79123456789',
            fio='Иванов Иван Иванович',
            city='г Воронеж',
            street='Ленина',
            home='10'
        )
        expected_address = "г Воронеж, Ленина, 10"
        self.assertEqual(client.address, expected_address)

    def test_str_representation(self):
        """Тестирование строкового представления объекта."""
        client = Client.objects.create(**self.client_data)
        self.assertEqual(str(client), 'Иванов Иван Иванович')