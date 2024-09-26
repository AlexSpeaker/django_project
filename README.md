# Интернет магазин
___
## Создание и активация виртуального окружения
- sudo apt install python3-virtualenv
- virtualenv venv
- source venv/bin/activate
___
## Установка зависимостей
- Необходимо установить библиотеку **Poetry**: **pip install poetry**
- И выполняем установку всех зависимостей в проекте командой: **poetry install**
___
## Применяем миграции
- **python manage.py migrate**

## Создание суперпользователя (администратора)
- Переходим в корень нашего проекта. Далее переходим в папку **mysite** и выполняем команду: **python manage.py createsuperuser**
___
## Запуск проекта
- В папке **mysite** выполняем команду: **python manage.py runserver**
- Вход в админку **http:/.../admin**
