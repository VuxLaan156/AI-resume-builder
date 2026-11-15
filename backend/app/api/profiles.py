from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models.profile import Profile, User
from ..schemas.profiles import ProfileCreate, ProfileRead, ProfileUpdate
from .dependencies import DatabaseSession, get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])

CurrentUser = Annotated[User, Depends(get_current_user)]


def find_profile(session: Session, user: User) -> Profile:
    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/me", response_model=ProfileRead, status_code=201)
def create_profile(
    data: ProfileCreate, session: DatabaseSession, user: CurrentUser
) -> ProfileRead:
    statement = (
        insert(Profile)
        .values(user_id=user.id, **data.model_dump())
        .on_conflict_do_nothing(index_elements=[Profile.user_id])
        .returning(Profile)
    )
    profile = session.scalars(statement).one_or_none()
    if profile is None:
        raise HTTPException(status_code=409, detail="Profile already exists")

    result = ProfileRead.model_validate(profile)
    session.commit()
    return result


@router.get("/me", response_model=ProfileRead)
def read_profile(session: DatabaseSession, user: CurrentUser) -> Profile:
    return find_profile(session, user)


@router.patch("/me", response_model=ProfileRead)
def update_profile(
    data: ProfileUpdate, session: DatabaseSession, user: CurrentUser
) -> ProfileRead:
    profile = find_profile(session, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    result = ProfileRead.model_validate(profile)
    session.commit()
    return result


@router.delete("/me", status_code=204)
def delete_profile(session: DatabaseSession, user: CurrentUser) -> Response:
    session.delete(find_profile(session, user))
    session.commit()
    return Response(status_code=204)
