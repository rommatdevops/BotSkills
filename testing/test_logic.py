from utils.database import SessionLocal
from .models import TestCategory, Test, Question, Answer
from sqlalchemy.orm import joinedload
import random
from sqlalchemy import func

def get_test_categories():
    session = SessionLocal()
    categories = session.query(TestCategory).all()
    session.close()
    return categories

def get_random_question(test_id):
    session = SessionLocal()
    question = (session.query(Question)
                .options(joinedload(Question.answers))
                .filter(Question.test_id == test_id)
                .order_by(func.rand())
                .first())
    session.close()
    return question
