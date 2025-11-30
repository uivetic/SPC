"""User models"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None

