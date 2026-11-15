from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_session
from .models.profile import Profile

app = FastAPI(title = "AI resume builder", description = "AI resume builder is a web application that allows users to create professional resumes using artificial intelligence. The application uses natural language processing and machine learning algorithms to analyze user input and generate a customized resume that highlights the user's skills and experience.", version = "1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Welcome to the AI resume builder API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check(session: Annotated[Session, Depends(get_session)]):
    try:
        session.execute(select(Profile).limit(1))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}
