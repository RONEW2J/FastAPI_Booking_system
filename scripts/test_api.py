import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_booking_system():
    """Тестирует основные функции системы бронирования"""
    
    print("1. Регистрация пользователя...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Пользователь зарегистрирован")
    else:
        print(f"❌ Ошибка регистрации: {response.text}")
        return
    
    print("\n2. Авторизация...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Авторизация успешна")
    else:
        print(f"❌ Ошибка авторизации: {response.text}")
        return
    
    print("\n3. Создание ресурса...")
    resource_data = {
        "name": "Конференц-зал А",
        "description": "Зал для встреч на 10 человек",
        "capacity": 10
    }
    
    response = requests.post(f"{BASE_URL}/resources/", json=resource_data, headers=headers)
    if response.status_code == 200:
        resource_id = response.json()["id"]
        print(f"✅ Ресурс создан с ID: {resource_id}")
    else:
        print(f"❌ Ошибка создания ресурса: {response.text}")
        return
    
    print("\n4. Получение списка ресурсов...")
    response = requests.get(f"{BASE_URL}/resources/")
    if response.status_code == 200:
        resources = response.json()
        print(f"✅ Найдено ресурсов: {len(resources)}")
    else:
        print(f"❌ Ошибка получения ресурсов: {response.text}")
    
    print("\n5. Создание бронирования...")
    start_time = datetime.now() + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)
    
    booking_data = {
        "resource_id": resource_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "notes": "Тестовая встреча"
    }
    
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
    if response.status_code == 200:
        booking_id = response.json()["id"]
        print(f"✅ Бронирование создано с ID: {booking_id}")
    else:
        print(f"❌ Ошибка создания бронирования: {response.text}")
        return
    
    print("\n6. Получение списка бронирований...")
    response = requests.get(f"{BASE_URL}/bookings/", headers=headers)
    if response.status_code == 200:
        bookings = response.json()
        print(f"✅ Найдено бронирований: {len(bookings)}")
    else:
        print(f"❌ Ошибка получения бронирований: {response.text}")
    
    print("\n7. Проверка доступности...")
    check_start = start_time + timedelta(minutes=30)
    check_end = check_start + timedelta(hours=1)
    
    params = {
        "start_time": check_start.isoformat(),
        "end_time": check_end.isoformat()
    }
    
    response = requests.get(f"{BASE_URL}/calendar/{resource_id}/availability", params=params)
    if response.status_code == 200:
        availability = response.json()
        print(f"✅ Доступность проверена: {availability}")
    else:
        print(f"❌ Ошибка проверки доступности: {response.text}")
    
    print("\n8. Получение календаря...")
    calendar_start = datetime.now()
    calendar_end = calendar_start + timedelta(days=7)
    
    params = {
        "start_date": calendar_start.isoformat(),
        "end_date": calendar_end.isoformat()
    }
    
    response = requests.get(f"{BASE_URL}/calendar/{resource_id}", params=params)
    if response.status_code == 200:
        calendar_data = response.json()
        print(f"✅ Календарь получен: {len(calendar_data['bookings'])} бронирований")
    else:
        print(f"❌ Ошибка получения календаря: {response.text}")
    
    print("\n🎉 Все тесты завершены!")

if __name__ == "__main__":
    test_booking_system()