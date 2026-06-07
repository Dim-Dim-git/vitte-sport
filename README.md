# Спортивный портал МУИВ

Веб-сайт для автоматизации записи и учёта посещаемости спортивных секций Московского университета им. С.Ю. Витте.

## Технологии

- Python 3.10
- Django 5.2.14
- SQLite (разработка) / PostgreSQL (продакшн)
- openpyxl 3.1
- Pillow 12.2.0

## Установка и запуск

### 1. Клонировать репозиторий

```
git clone https://github.com/Dim-Dim-git/vitte-sport.git
cd vitte-sport
```

### 2. Создать виртуальное окружение

```
python -m venv venv
venv\Scripts\activate
```

### 3. Установить зависимости

```
pip install -r requirements.txt
```

### 4. Применить миграции

```
python manage.py migrate
```

### 5. Запустить сервер

```
python manage.py runserver
```

Сайт доступен по адресу: http://127.0.0.1:8000

## Учётные данные пользователей

Логин / Пароль / Роль

student / student / Студент

coach / coach / Тренер

portal_admin / portal_admin / Администратор портала

admin / admin / Django Admin

## Основные команды

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Ссылки

- Репозиторий: https://github.com/Dim-Dim-git/vitte-sport
- Сайт на хостинге: https://vitte-sport.onrender.com

## Особенности хостинга

Сайт размещён на бесплатном тарифе. При отсутствии активности более 15 минут сервис засыпает.
При первом обращении после паузы сайт просыпается в течение 30-60 секунд — это нормально, просто подождите.