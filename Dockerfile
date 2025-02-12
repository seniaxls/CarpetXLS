# Используем официальный образ Python
FROM python:3.13-bullseye

# Устанавливаем рабочую директорию
WORKDIR /app

RUN pip install --upgrade pip

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Создание директорий для статических файлов и медиафайлов
RUN mkdir -p /app/static_cdn /app/media

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска Gunicorn (заменяет runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "carpetxls.wsgi:application"]