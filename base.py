from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class DiaryCreate(BaseModel):
    userId: int
    date: str
    rawInput: str = None
    content: str = None
    imgUrl: str = None


class DiaryResponse(BaseModel):
    id: int
    userId: int
    date: str
    rawInput: Optional[str] = None
    content: Optional[str] = None
    imgUrl: Optional[str] = None
    createdAt: str
    lastModified: str

    @field_validator('date', mode='before')
    def convert_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    @field_validator('createdAt', 'lastModified', mode='before')
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
