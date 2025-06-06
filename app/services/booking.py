from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from ..models.booking import Booking, Resource, User
from ..schemas.booking import BookingCreate
from ..core.redis_client import get_redis
import json

class BookingService:
    def __init__(self, db: Session):
        self.db = db
    
    async def check_availability(self, resource_id: int, start_time: datetime, end_time: datetime, exclude_booking_id: int = None):
        """Проверяет доступность ресурса на указанное время"""
        query = self.db.query(Booking).filter(
            and_(
                Booking.resource_id == resource_id,
                Booking.status.in_(["pending", "confirmed"]),
                or_(
                    and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                    and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                    and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        conflicts = query.all()
        return len(conflicts) == 0
    
    async def create_booking(self, user_id: int, booking_data: BookingCreate):
        """Создает новое бронирование"""
        resource = self.db.query(Resource).filter(Resource.id == booking_data.resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        is_available = await self.check_availability(
            booking_data.resource_id,
            booking_data.start_time,
            booking_data.end_time
        )
        
        if not is_available:
            raise HTTPException(
                status_code=409,
                detail="Resource is not available for the requested time slot"
            )
        
        # Создаем бронирование
        booking = Booking(
            user_id=user_id,
            resource_id=booking_data.resource_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            notes=booking_data.notes,
            status="pending"
        )
        
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        
        # Очищаем кеш календаря
        await self.clear_calendar_cache(booking_data.resource_id)
        
        return booking
    
    async def get_calendar(self, resource_id: int, start_date: datetime, end_date: datetime):
        """Получает календарь занятости с кешированием"""
        redis = await get_redis()
        cache_key = f"calendar:{resource_id}:{start_date.date()}:{end_date.date()}"
        
        # Проверяем кеш
        cached_data = await redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        bookings = self.db.query(Booking).filter(
            and_(
                Booking.resource_id == resource_id,
                Booking.status.in_(["pending", "confirmed"]),
                Booking.start_time <= end_date,
                Booking.end_time >= start_date
            )
        ).all()
        
        calendar_data = {
            "resource_id": resource_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "bookings": [
                {
                    "id": booking.id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat(),
                    "status": booking.status,
                    "user_id": booking.user_id
                }
                for booking in bookings
            ]
        }
        
        await redis.setex(cache_key, 300, json.dumps(calendar_data))
        
        return calendar_data
    
    async def clear_calendar_cache(self, resource_id: int):
        """Очищает кеш календаря для ресурса"""
        redis = await get_redis()
        pattern = f"calendar:{resource_id}:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)