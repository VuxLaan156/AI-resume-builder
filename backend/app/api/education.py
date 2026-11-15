from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import delete, select, update

from ..models.education import Education
from ..schemas.education import EducationCreate, EducationRead, EducationUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile

router = APIRouter(prefix="/profiles/me/education", tags=["education"])


@router.get("", response_model=list[EducationRead])
def list_education(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        select(Education)
        .where(Education.profile_id == profile.id)
        .order_by(Education.institution, Education.id)
    )
    return session.scalars(statement).all()


@router.post("", response_model=EducationRead, status_code=201)
def create_education(data: EducationCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    entry = Education(profile_id=profile.id, **data.model_dump())
    session.add(entry)
    session.flush()
    result = EducationRead.model_validate(entry)
    session.commit()
    return result


@router.patch("/{education_id}", response_model=EducationRead)
def update_education(
    education_id: UUID, data: EducationUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    owned_entry = (Education.profile_id == profile.id, Education.id == education_id)
    changes = data.model_dump(exclude_unset=True)
    if changes:
        statement = update(Education).where(*owned_entry).values(**changes).returning(Education)
    else:
        statement = select(Education).where(*owned_entry)

    entry = session.scalar(statement)
    if entry is None:
        raise HTTPException(status_code=404, detail="Education not found")
    result = EducationRead.model_validate(entry)
    if changes:
        session.commit()
    return result


@router.delete("/{education_id}", status_code=204)
def delete_education(education_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Education)
        .where(Education.profile_id == profile.id, Education.id == education_id)
        .returning(Education.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Education not found")
    session.commit()
    return Response(status_code=204)
