from pydantic import BaseModel, field_validator
from typing import List, Optional, Union
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int = -1
    username: str
    email: str
    createdAt: str = None
    lastModified: str = None

    @field_validator('createdAt', 'lastModified', mode='before')
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class DiaryCreate(BaseModel):
    userId: int
    date: str
    rawInput: Union[str, List[str]]
    content: str = None
    imgUrl: str = None


class RAGQuery(BaseModel):
    userId: int
    query: str


class RAGResponse(BaseModel):
    userId: int
    query: str
    answer: str = None


class DiaryResponse(BaseModel):
    id: int = -1
    userId: int
    date: str
    rawInput: Union[str, List[str]]
    content: Optional[str] = None
    imgUrl: Optional[str] = None
    createdAt: str = None
    lastModified: str = None
    isValid: bool = False

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
