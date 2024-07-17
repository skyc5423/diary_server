from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())
    lastModified = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    diaries = relationship("Diary", back_populates="user")


class Diary(Base):
    __tablename__ = "diary"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    rawInput = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    imgUrl = Column(String(255), nullable=True)
    createdAt = Column(TIMESTAMP, server_default=func.current_timestamp())
    lastModified = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="diaries")
