from typing import List, Optional
from pydantic import BaseModel

class ChoiceBase(BaseModel):
    text: str

class ChoiceCreate(ChoiceBase):
    pass

class Choice(ChoiceBase):
    id: int

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    text: str
    audio: Optional[str] = None

class QuestionCreate(QuestionBase):
    choices: List[ChoiceCreate]

class Question(QuestionBase):
    id: int
    choices: List[Choice]

    class Config:
        orm_mode = True

class QuizBase(BaseModel):
    title: str

class QuizCreate(QuizBase):
    questions: List[QuestionCreate]

class Quiz(QuizBase):
    id: int
    questions: List[Question]

    class Config:
        orm_mode = True
