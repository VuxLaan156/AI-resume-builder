from contextlib import contextmanager
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from psycopg.errors import CheckViolation
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from ..models.experience import Experience
from ..schemas.experience import ExperienceCreate, ExperienceRead, ExperienceUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile

router = APIRouter(prefix="/profiles/me/experience", tags=["experience"])


@contextmanager
def validate_dates():
    try:
        yield
    except IntegrityError as exc:
        if isinstance(exc.orig, CheckViolation) and exc.orig.diag.table_name == "work_experiences":
            raise HTTPException(
                status_code=422, detail="end_date must be on or after start_date"
            ) from exc
        raise


@router.get("", response_model=list[ExperienceRead])
def list_experience(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        select(Experience)
        .where(Experience.profile_id == profile.id)
        .order_by(Experience.start_date.desc(), Experience.id)
    )
    return session.scalars(statement).all()


@router.post("", response_model=ExperienceRead, status_code=201)
def create_experience(data: ExperienceCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    entry = Experience(profile_id=profile.id, **data.model_dump())
    session.add(entry)
    with validate_dates():
        session.flush()
    result = ExperienceRead.model_validate(entry)
    session.commit()
    return result


@router.patch("/{experience_id}", response_model=ExperienceRead)
def update_experience(
    experience_id: UUID, data: ExperienceUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    owned_entry = (Experience.profile_id == profile.id, Experience.id == experience_id)
    changes = data.model_dump(exclude_unset=True)
    if changes:
        statement = update(Experience).where(*owned_entry).values(**changes).returning(Experience)
    else:
        statement = select(Experience).where(*owned_entry)

    with validate_dates():
        entry = session.scalar(statement)
    if entry is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    result = ExperienceRead.model_validate(entry)
    if changes:
        session.commit()
    return result


@router.delete("/{experience_id}", status_code=204)
def delete_experience(experience_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Experience)
        .where(Experience.profile_id == profile.id, Experience.id == experience_id)
        .returning(Experience.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    session.commit()
    return Response(status_code=204)
