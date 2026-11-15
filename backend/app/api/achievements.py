from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import delete, select, update

from ..models.achievements import Achievement
from ..schemas.achievements import AchievementCreate, AchievementRead, AchievementUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile

router = APIRouter(prefix="/profiles/me/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementRead])
def list_achievements(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        select(Achievement)
        .where(Achievement.profile_id == profile.id)
        .order_by(Achievement.title, Achievement.id)
    )
    return session.scalars(statement).all()


@router.post("", response_model=AchievementRead, status_code=201)
def create_achievement(data: AchievementCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    entry = Achievement(profile_id=profile.id, **data.model_dump())
    session.add(entry)
    session.flush()
    result = AchievementRead.model_validate(entry)
    session.commit()
    return result


@router.patch("/{achievement_id}", response_model=AchievementRead)
def update_achievement(
    achievement_id: UUID, data: AchievementUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    owned_entry = (Achievement.profile_id == profile.id, Achievement.id == achievement_id)
    changes = data.model_dump(exclude_unset=True)
    if changes:
        statement = update(Achievement).where(*owned_entry).values(**changes).returning(Achievement)
    else:
        statement = select(Achievement).where(*owned_entry)

    entry = session.scalar(statement)
    if entry is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    result = AchievementRead.model_validate(entry)
    if changes:
        session.commit()
    return result


@router.delete("/{achievement_id}", status_code=204)
def delete_achievement(achievement_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Achievement)
        .where(Achievement.profile_id == profile.id, Achievement.id == achievement_id)
        .returning(Achievement.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    session.commit()
    return Response(status_code=204)
