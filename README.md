# LMS Project

Обучающая платформа (курсы, уроки, подписки, платежи через Stripe) на Django REST Framework + Celery + PostgreSQL + Redis.

## Стек

- Python 3.13 + Poetry
- Django 5.x + DRF + SimpleJWT + drf-spectacular
- PostgreSQL 16
- Redis + Celery (worker + beat)
- Stripe
- Gunicorn + Nginx
- Docker + Docker Compose
- GitHub Actions (CI)

---

## Быстрый старт (локально / Docker)

```bash
# 1. Клонировать
git clone <your-repo-url>
cd lms_project

# 2. Создать .env из шаблона
cp .env.example .env
# Отредактировать .env (секреты, пароли, Stripe-ключ и т.д.)

# 3. Запуск
docker compose up -d --build

# 4. Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# 5. Документация API
http://127.0.0.1/api/docs/
```

---

## Переменные окружения

См. `.env.example`. Основные:

| Переменная | Описание |
|------------|----------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Список хостов через запятую |
| `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` | PostgreSQL |
| `STRIPE_API_KEY` | Ключ Stripe |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Redis |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Почта |

**Никогда не коммитьте `.env`!**

---

## Структура

```
lms_project/
├── config/          # settings, urls, celery, wsgi
├── lms/             # курсы, уроки, подписки, платежи
├── users/           # пользователи + JWT
├── .github/workflows/ci-cd.yml
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example
├── pyproject.toml
└── manage.py
```

---

## Деплой на сервер (кратко)

1. На сервере установить Docker + Docker Compose.
2. Настроить SSH-ключ (без пароля).
3. Закрыть порты 5432, 6379, 8000 — открыть только 80/443.
4. Склонировать репозиторий в `/opt/lms_project`.
5. Создать `.env` на сервере.
6. `docker compose up -d --build`.
7. В GitHub → Settings → Secrets добавить:
   - `SERVER_HOST`
   - `SERVER_USER`
   - `SSH_PRIVATE_KEY`
8. Раскомментировать job `deploy` в `.github/workflows/ci-cd.yml`.

Авто-перезапуск контейнеров обеспечивается `restart: always`.

---

## CI/CD

При каждом push/PR запускаются тесты.  
После успешного прохождения тестов на `main` можно деплоить (см. workflow).

---

## Полезные команды

```bash
# Логи
docker compose logs -f web
docker compose logs -f celery-worker

# Миграции
docker compose exec web python manage.py migrate

# Тесты
docker compose exec web python manage.py test

# Shell
docker compose exec web python manage.py shell
```
