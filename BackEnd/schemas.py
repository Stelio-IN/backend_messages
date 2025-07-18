from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    phone: constr(min_length=10, max_length=15)

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageCreate(BaseModel):
    receiver_phone: str
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    sender_username: str
    receiver_username: str
    sender_phone: Optional[str] = None
    receiver_phone: Optional[str] = None
    is_fraudulent: bool = False
    fraud_probability: float = 0.0

    class Config:
        from_attributes = True