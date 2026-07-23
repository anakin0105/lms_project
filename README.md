# LMS Project

## Запуск через Docker

```bash
# 1. Клонируй репозиторий
git clone ...

# 2. Создай .env (скопируй из .env.example или отредактируй существующий)
cp .env.example .env

# 3. Запуск
docker-compose up -d --build

# 4. Применить миграции
docker-compose exec web poetry run python manage.py migrate

# 5. Создать суперпользователя
docker-compose exec web poetry run python manage.py createsuperuser

# 6. Открыть
http://127.0.0.1:8000/api/docs/