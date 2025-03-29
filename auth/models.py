from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from utils.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(100))
    full_name = Column(String(255))
    is_authorized = Column(Boolean, default=False)

    # Додано зв’язок
    test_sessions = relationship("UserTestSession", back_populates="user")