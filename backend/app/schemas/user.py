from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import List

class ProductivityScore(BaseModel):
    exercise: int = 0
    study: int = 0
    meditation: int = 0
    hobby: int = 0
    rest_time: int = 0


class ProductivityResponse(BaseModel):
    message: str
    overall_score: float
    details: ProductivityScore

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    productivity: Optional[ProductivityScore] = None

class UserOut(BaseModel):    # UserOut is used 
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"