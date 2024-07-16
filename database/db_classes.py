from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    createdAt = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    lastModified = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")

    diaries = relationship("Diary", back_populates="user")


class Diary(Base):
    __tablename__ = "diary"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    rawInput = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    imgUrl = Column(String(255), nullable=True)
    createdAt = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    lastModified = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")

    user = relationship("User", back_populates="diaries")
