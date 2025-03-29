# auth/auth.py
from utils.database import SessionLocal
from auth.models import User
from sqlalchemy import text

def register_user(telegram_id, username, full_name):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            is_authorized=False
        )
        session.add(user)
        session.commit()
    session.close()

def authorize_user(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.is_authorized = True
        session.commit()
    session.close()

def check_authorization(telegram_id):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    session.close()
    return user.is_authorized if user else False
