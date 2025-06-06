from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, engine
from app.core.config import settings
from app.models import booking as models
from app.schemas import booking as schemas
from app.services.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.services.booking import BookingService
from app.tasks.notification_tasks import send_booking_confirmation_email
from app.tasks.booking_tasks import confirm_booking


# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Система бронирования с календарем и уведомлениями",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === AUTH ENDPOINTS ===
@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем существование пользователя
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Создаем пользователя
    hashed_password = get_password_hash(user_data.password)
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# === RESOURCE ENDPOINTS ===
@app.post("/resources/", response_model=schemas.ResourceResponse)
def create_resource(
    resource_data: schemas.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    resource = models.Resource(**resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

@app.get("/resources/", response_model=List[schemas.ResourceResponse])
def get_resources(db: Session = Depends(get_db)):
    return db.query(models.Resource).filter(models.Resource.is_active == True).all()

# === BOOKING ENDPOINTS ===
@app.post("/bookings/", response_model=schemas.BookingResponse)
async def create_booking(
    booking_data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking_service = BookingService(db)
    booking = await booking_service.create_booking(current_user.id, booking_data)
    
    # Отправляем задачу на подтверждение и уведомление
    send_booking_confirmation_email.delay(booking.id)
    confirm_booking.apply_async(args=[booking.id], countdown=60)  # подтверждаем через минуту
    
    return booking

@app.get("/bookings/", response_model=List[schemas.BookingResponse])
def get_user_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()

@app.get("/bookings/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking

@app.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Отменяем бронирование
    booking.status = "cancelled"
    db.commit()
    
    return {"detail": "Booking cancelled successfully"}

# === CALENDAR ENDPOINTS ===
@app.get("/calendar/{resource_id}")
async def get_calendar(
    resource_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    calendar_data = await booking_service.get_calendar(resource_id, start_date, end_date)
    return calendar_data

@app.get("/calendar/{resource_id}/availability")
async def check_availability(
    resource_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    booking_service = BookingService(db)
    is_available = await booking_service.check_availability(resource_id, start_time, end_time)
    return {"available": is_available}

# === ADMIN ENDPOINTS ===
@app.get("/admin/bookings/", response_model=List[schemas.BookingResponse])
def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # В реальном проекте добавить проверку прав администратора
    return db.query(models.Booking).offset(skip).limit(limit).all()

@app.get("/admin/stats/")
def get_booking_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_bookings = db.query(models.Booking).count()
    confirmed_bookings = db.query(models.Booking).filter(models.Booking.status == "confirmed").count()
    pending_bookings = db.query(models.Booking).filter(models.Booking.status == "pending").count()
    cancelled_bookings = db.query(models.Booking).filter(models.Booking.status == "cancelled").count()
    
    return {
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "pending_bookings": pending_bookings,
        "cancelled_bookings": cancelled_bookings
    }

# === HEALTH CHECK ===
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
