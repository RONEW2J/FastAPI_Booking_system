#!/bin/bash

# Настройка и запуск системы бронирования

echo "🚀 Setting up Booking System..."

# Создаем директории
mkdir -p app/{core,models,schemas,api,services,tasks,utils}
mkdir -p alembic/versions

# Копируем .env файл
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please update it with your settings."
fi

# Запускаем Docker Compose
echo "🐳 Starting Docker services..."
docker-compose up -d

# Ждем запуска сервисов
echo "⏳ Waiting for services to start..."
sleep 30

# Инициализируем миграции
echo "🗄️ Initializing database migrations..."
docker-compose exec app alembic init alembic
docker-compose exec app alembic revision --autogenerate -m "Initial migration"
docker-compose exec app alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "🌐 FastAPI: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🐰 RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo ""
echo "To check logs:"
echo "  docker-compose logs -f app"
echo "  docker-compose logs -f celery_worker"
