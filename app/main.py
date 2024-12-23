from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, Base, SessionLocal
from typing import List
from TTS.api import TTS
from fastapi.responses import FileResponse
import os

# Initialize the database
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load a TTS model (using default pretrained model for simplicity)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

@app.post("/create-quiz", response_model=schemas.Quiz)
def create_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db)):
    """
    Create a new quiz. Automatically generate audio for questions without audio.
    """
    for question in quiz.questions:
        if not question.audio:  # No audio uploaded
            try:
                output_path = os.path.join("app/audio", f"{question.text[:10]}_audio.mp3")
                tts.tts_to_file(text=question.text, file_path=output_path)
                question.audio = f"/audio/{os.path.basename(output_path)}"  # Set the audio URL
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating audio for question '{question.text}': {str(e)}"
                )

    return crud.create_quiz(db=db, quiz=quiz)

@app.get("/quiz/{quiz_id}", response_model=schemas.Quiz)
def read_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.post("/submit-quiz/{quiz_id}")
def submit_quiz(quiz_id: int, answers: List[str], db: Session = Depends(get_db)):
    score = crud.submit_quiz(db, quiz_id, answers)
    return {"score": score}

@app.post("/generate-tts")
def generate_tts(text: str):
    """
    Generate TTS audio for the given text and save it as an MP3 file.
    """
    try:
        output_dir = "app/audio"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "question_audio.mp3")

        # Generate audio
        tts.tts_to_file(text=text, file_path=output_path)

        return {"audio_url": f"/audio/question_audio.mp3"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating TTS audio for text: {text[:30]}... : {str(e)}"
        )

@app.get("/audio/{filename}")
def serve_audio(filename: str):
    """
    Serve generated audio files.
    """
    file_path = os.path.join("app/audio", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
