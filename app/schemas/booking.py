from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Resource schemas
class ResourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: int = 1

class ResourceCreate(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Booking schemas
class BookingBase(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    user: UserResponse
    resource: ResourceResponse
    
    class Config:
        from_attributes = True

class BookingList(BaseModel):
    bookings: List[BookingResponse]
    total: int

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
