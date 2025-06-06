# 🏢 Booking System

A modern booking system with an availability calendar and notifications.

## 🚀 Technologies

- **FastAPI** - modern web framework for Python
- **PostgreSQL** - reliable relational database
- **Redis** - caching and broker for Celery
- **RabbitMQ** - message queue
- **Celery** - background task processing
- **Docker** - containerization
- **Alembic** - database migrations

## 📋 Features

### 🔐 Authentication

- User registration and authorization
- JWT tokens for security
- Protected endpoints

### 📅 Booking

- Create, view, and cancel bookings
- Check resource availability
- Availability calendar with caching

### 🔔 Notifications

- Email booking confirmations
- Reminders for upcoming meetings
- Automatic cleanup of expired bookings

### 🎯 Administration

- Resource management
- Booking statistics
- System monitoring

## 🛠 Installation and Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/RONEW2J/FastAPI_Booking_system
cd booking_system
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env file with your settings
```

3. **Launch the system:**

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Installation

1. **Start services:**

```bash
docker-compose up -d
```

2. **Run migrations:**

```bash
docker-compose exec app alembic upgrade head
```

3. **Check status:**

```bash
docker-compose ps
```

## 🌐 API Endpoints

### Authentication

- `POST /auth/register` - Registration
- `POST /auth/token` - Get token

### Resources

- `GET /resources/` - List resources
- `POST /resources/` - Create resource

### Bookings

- `GET /bookings/` - My bookings
- `POST /bookings/` - Create booking
- `GET /bookings/{id}` - Booking details
- `DELETE /bookings/{id}` - Cancel booking

### Calendar

- `GET /calendar/{resource_id}` - Resource calendar
- `GET /calendar/{resource_id}/availability` - Check availability

### Administration

- `GET /admin/bookings/` - All bookings
- `GET /admin/stats/` - Statistics

## 🧪 Testing

Run the test script:

```bash
python scripts/test_api.py
```

## 📚 Documentation

After system launch, interactive documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Monitoring

### Web Interfaces

- **RabbitMQ Management**: http://localhost:15672
- **Application**: http://localhost:8000

### Logs

```bash
# Application logs
docker-compose logs -f app

# Celery logs
docker-compose logs -f celery_worker

# All services logs
docker-compose logs -f
```

## ⚙️ Configuration

Main settings in `.env` file:

```env
# Database
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

## 🔄 Architecture

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

## 🤝 Development

### Adding New Celery Tasks

1. Create a task in `app/tasks/`:

```python
@celery_app.task
def my_task(param):
    # Task logic
    return "Result"
```

2. Import in `celery_app.py`:

```python
celery_app.conf.update(
    include=["app.tasks.my_tasks"]
)
```

### Adding New Endpoints

1. Create schemas in `app/schemas/`
2. Add models in `app/models/`
3. Implement logic in `app/services/`
4. Add endpoints in `app/main.py`

## 📝 License

MIT License

## 🆘 Support

If you have questions or issues:

1. Check logs: `docker-compose logs`
2. Ensure all services are running: `docker-compose ps`
3. Verify settings in `.env` file
4. Create an issue in the repository
