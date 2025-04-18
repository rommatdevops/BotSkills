from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from utils.base import Base

class TestCategory(Base):
    __tablename__ = 'test_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tests = relationship("Test", back_populates="category")

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('test_categories.id'))
    difficulty_level = Column(Integer)
    description = Column(Text)
    category = relationship("TestCategory", back_populates="tests")
    questions = relationship("Question", back_populates="test")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    question_text = Column(Text, nullable=False)
    explanation = Column(Text)
    test = relationship("Test", back_populates="questions")
    answers = relationship("Answer", back_populates="question")  # ← додано цей рядок

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question = relationship("Question", back_populates="answers")  # ← і цей рядок додано

class UserTestSession(Base):
    __tablename__ = 'user_test_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    score = Column(Integer)
    is_passed = Column(Boolean)

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('user_test_sessions.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answers.id'))
    is_correct = Column(Boolean)
