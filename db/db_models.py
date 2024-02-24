import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine(os.getenv('DATABASE_URL'), echo=True)

Base = declarative_base()


# Define User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(500), nullable=False)
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    open_ai_id = Column(String(100))
    status = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="files")


class Difficulty(PyEnum):  # FIXME: Cannot configure it properly, will fix later
    easy = 1
    medium = 2
    hard = 3


class Question(Base):
    __tablename__ = "generated_questions"
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    difficulty = Column(String(50))
    answer_description = Column(String(500))
    source_page = Column(String(500))  # New field to store source page reference
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True)
    key = Column(String(50))  # To store the option key like 'a', 'b', etc.
    value = Column(String(500))  # To store the option text
    is_correct = Column(Boolean)
    question_id = Column(Integer, ForeignKey("generated_questions.id"))
    question = relationship("Question", back_populates="options")


def initiate_database():
    Base.metadata.create_all(engine)
