from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(150), unique=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    is_authorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
