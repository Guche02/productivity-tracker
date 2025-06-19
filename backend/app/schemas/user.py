from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date

class ProductivityScore(BaseModel):
    exercise: float = Field(0, ge=0, le=5)
    study: float = Field(0, ge=0, le=5)
    meditation: float = Field(0, ge=0, le=5)
    hobby: float = Field(0, ge=0, le=5)
    rest_time: float = Field(0, ge=0, le=5)

class DatedProductivityScore(ProductivityScore):
    date: date

    class Config:
        orm_mode = True

class ProductivityResponse(BaseModel):
    message: str
    exercise: Optional[float] = None
    study: Optional[float] = None
    meditation: Optional[float] = None
    hobby: Optional[float] = None
    rest_time: Optional[float] = None
    overall: Optional[float] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str

class UserOut(BaseModel):  
    id: str
    email: EmailStr
    created_at: datetime
    productivity: List[DatedProductivityScore] = []  

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