from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..models.profile import Profile

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Welcome to the AI resume builder API!"}


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.get("/ready")
def readiness_check(session: Annotated[Session, Depends(get_session)]):
    try:
        session.execute(select(Profile).limit(1))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}
