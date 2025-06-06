import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..core.config import settings
from ..models.booking import Booking, User
from .celery_app import celery_app

@celery_app.task
def send_booking_confirmation_email(booking_id: int):
    """Отправляет email подтверждения бронирования"""
    if not settings.smtp_user or not settings.smtp_password:
        return "Email settings not configured"
    
    db = SessionLocal()
    try:
        booking = db.query(Booking).join(User).filter(Booking.id == booking_id).first()
        if not booking:
            return f"Booking {booking_id} not found"
        
        msg = MIMEMultipart()
        msg['From'] = settings.smtp_user
        msg['To'] = booking.user.email
        msg['Subject'] = f"Booking Confirmation - {settings.app_name}"
        
        body = f"""
        Dear {booking.user.username},
        
        Your booking has been confirmed!
        
        Details:
        - Resource: {booking.resource.name}
        - Date: {booking.start_time.strftime('%Y-%m-%d')}
        - Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}
        - Status: {booking.status}
        
        Thank you for using {settings.app_name}!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        server.quit()
        
        return f"Confirmation email sent to {booking.user.email}"
    
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    finally:
        db.close()

@celery_app.task
def send_booking_reminders():
    """Отправляет напоминания о предстоящих бронированиях"""
    db = SessionLocal()
    try:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        upcoming_bookings = db.query(Booking).join(User).filter(
            Booking.status == "confirmed",
            Booking.start_time >= start_of_day,
            Booking.start_time <= end_of_day
        ).all()
        
        sent_count = 0
        for booking in upcoming_bookings:
            try:
                send_reminder_email.delay(booking.id)
                sent_count += 1
            except Exception as e:
                print(f"Failed to queue reminder for booking {booking.id}: {e}")
        
        return f"Queued {sent_count} reminder emails"
    
    except Exception as e:
        return f"Failed to process reminders: {str(e)}"
    finally:
        db.close()

@celery_app.task
def send_reminder_email(booking_id: int):
    """Отправляет напоминание о бронировании"""
    if not settings.smtp_user or not settings.smtp_password:
        return "Email settings not configured"
    
    db = SessionLocal()
    try:
        booking = db.query(Booking).join(User).filter(Booking.id == booking_id).first()
        if not booking:
            return f"Booking {booking_id} not found"
        
        msg = MIMEMultipart()
        msg['From'] = settings.smtp_user
        msg['To'] = booking.user.email
        msg['Subject'] = f"Booking Reminder - {settings.app_name}"
        
        body = f"""
        Dear {booking.user.username},
        
        This is a reminder about your upcoming booking:
        
        - Resource: {booking.resource.name}
        - Date: {booking.start_time.strftime('%Y-%m-%d')}
        - Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}
        
        Don't forget about your appointment!
        
        Best regards,
        {settings.app_name} Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        server.quit()
        
        return f"Reminder email sent to {booking.user.email}"
    
    except Exception as e:
        return f"Failed to send reminder: {str(e)}"
    finally:
        db.close()
