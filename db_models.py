from enum import Enum
from typing import List
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine("postgresql://educai:educai@localhost:5432"
                       "/educdb", echo=True)


class Base(DeclarativeBase):
    pass


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Question(Base):
    __tablename__ = "generated_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    difficulty: Mapped[str]
    answer_description: Mapped[str] = mapped_column(String(500))
    options: Mapped[List["Option"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "options"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool]
    question_id: Mapped[int] = mapped_column(ForeignKey("generated_questions.id"))
    question: Mapped["Question"] = relationship(back_populates="options")


#Base.metadata.create_all(engine)