# 🏢 Booking System

Современная система бронирования с календарем занятости и уведомлениями.

## 🚀 Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **PostgreSQL** - надежная реляционная база данных
- **Redis** - кеширование и брокер для Celery
- **RabbitMQ** - очередь сообщений
- **Celery** - обработка фоновых задач
- **Docker** - контейнеризация
- **Alembic** - миграции базы данных

## 📋 Возможности

### 🔐 Аутентификация

- Регистрация и авторизация пользователей
- JWT токены для безопасности
- Защищенные эндпоинты

### 📅 Бронирование

- Создание, просмотр и отмена бронирований
- Проверка доступности ресурсов
- Календарь занятости с кешированием

### 🔔 Уведомления

- Email-подтверждения бронирований
- Напоминания о предстоящих встречах
- Автоматическая очистка просроченных броней

### 🎯 Администрирование

- Управление ресурсами
- Статистика бронирований
- Мониторинг системы

## 🛠 Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Быстрый старт

1. **Клонируйте репозиторий:**

```bash
git clone <repository-url>
cd booking_system
```

2. **Настройте окружение:**

```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите систему:**

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Ручная установка

1. **Запустите сервисы:**

```bash
docker-compose up -d
```

2. **Выполните миграции:**

```bash
docker-compose exec app alembic upgrade head
```

3. **Проверьте статус:**

```bash
docker-compose ps
```

## 🌐 Эндпоинты API

### Аутентификация

- `POST /auth/register` - Регистрация
- `POST /auth/token` - Получение токена

### Ресурсы

- `GET /resources/` - Список ресурсов
- `POST /resources/` - Создание ресурса

### Бронирования

- `GET /bookings/` - Мои бронирования
- `POST /bookings/` - Создать бронирование
- `GET /bookings/{id}` - Детали бронирования
- `DELETE /bookings/{id}` - Отменить бронирование

### Календарь

- `GET /calendar/{resource_id}` - Календарь ресурса
- `GET /calendar/{resource_id}/availability` - Проверка доступности

### Администрирование

- `GET /admin/bookings/` - Все бронирования
- `GET /admin/stats/` - Статистика

## 🧪 Тестирование

Запустите тестовый скрипт:

```bash
python scripts/test_api.py
```

## 📚 Документация

После запуска системы доступна интерактивная документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Мониторинг

### Веб-интерфейсы

- **RabbitMQ Management**: http://localhost:15672
- **Приложение**: http://localhost:8000

### Логи

```bash
# Логи приложения
docker-compose logs -f app

# Логи Celery
docker-compose logs -f celery_worker

# Логи всех сервисов
docker-compose logs -f
```

## ⚙️ Конфигурация

Основные настройки в файле `.env`:

```env
# База данных
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@localhost:5672/

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🔄 Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │      Redis      │
│                 │────│                 │    │                 │
│   REST API      │    │   Users         │    │   Cache         │
│   Auth          │    │   Resources     │    │   Sessions      │
│   Validation    │    │   Bookings      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │              ┌─────────────────┐            │
         └──────────────│    RabbitMQ     │────────────┘
                        │                 │
                        │  Task Queue     │
                        │                 │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Celery      │
                        │                 │
                        │  Background     │
                        │  Tasks          │
                        │  Notifications  │
                        └─────────────────┘
```

## 🤝 Разработка

### Добавление новых задач Celery

1. Создайте задачу в `app/tasks/`:

```python
@celery_app.task
def my_task(param):
    # Логика задачи
    return "Result"
```

2. Импортируйте в `celery_app.py`:

```python
celery_app.conf.update(
    include=["app.tasks.my_tasks"]
)
```

### Добавление новых эндпоинтов

1. Создайте схемы в `app/schemas/`
2. Добавьте модели в `app/models/`
3. Реализуйте логику в `app/services/`
4. Добавьте эндпоинты в `app/main.py`

## 📝 Лицензия

MIT License

## 🆘 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что все сервисы запущены: `docker-compose ps`
3. Проверьте настройки в `.env` файле
4. Создайте issue в репозитории
