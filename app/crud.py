from sqlalchemy.orm import Session
from app import models, schemas

def create_quiz(db: Session, quiz: schemas.QuizCreate):
    db_quiz = models.Quiz(title=quiz.title)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    for question in quiz.questions:
        db_question = models.Question(text=question.text, audio=question.audio, quiz_id=db_quiz.id)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        for choice in question.choices:
            db_choice = models.Choice(text=choice.text, question_id=db_question.id)
            db.add(db_choice)
            db.commit()
    return db_quiz

def get_quiz(db: Session, quiz_id: int):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

def submit_quiz(db: Session, quiz_id: int, answers: list):
    quiz = get_quiz(db, quiz_id)
    correct_answers = 0
    for idx, question in enumerate(quiz.questions):
        if idx < len(answers) and answers[idx] == question.choices[0].text:
            correct_answers += 1
    return correct_answers
