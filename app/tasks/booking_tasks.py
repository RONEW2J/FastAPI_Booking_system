from celery import current_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.booking import Booking
from .celery_app import celery_app

@celery_app.task
def cleanup_expired_bookings():
    """Очищает просроченные брони со статусом pending"""
    db = SessionLocal()
    try:
        expiry_time = datetime.utcnow() - timedelta(minutes=30)
        expired_bookings = db.query(Booking).filter(
            Booking.status == "pending",
            Booking.created_at < expiry_time
        ).all()
        
        for booking in expired_bookings:
            booking.status = "cancelled"
        
        db.commit()
        return f"Cancelled {len(expired_bookings)} expired bookings"
    
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@celery_app.task
def confirm_booking(booking_id: int):
    """Подтверждает бронирование"""
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking and booking.status == "pending":
            booking.status = "confirmed"
            db.commit()
            return f"Booking {booking_id} confirmed"
        return f"Booking {booking_id} not found or already processed"
    
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()