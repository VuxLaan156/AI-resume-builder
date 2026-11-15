from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from psycopg.errors import UniqueViolation
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from ..models.skill import Skill
from ..schemas.skill import SkillCreate, SkillRead, SkillUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile
router = APIRouter(prefix="/profiles/me/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
def list_skills(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = select(Skill).where(Skill.profile_id == profile.id).order_by(Skill.skill_name)
    return session.scalars(statement).all()


@router.post("", response_model=SkillRead, status_code=201)
def create_skill(data: SkillCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        insert(Skill)
        .values(profile_id=profile.id, **data.model_dump())
        .on_conflict_do_nothing(index_elements=[Skill.profile_id, Skill.skill_name])
        .returning(Skill)
    )
    skill = session.scalars(statement).one_or_none()
    if skill is None:
        raise HTTPException(status_code=409, detail="Skill already exists")
    result = SkillRead.model_validate(skill)
    session.commit()
    return result


@router.patch("/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: UUID, data: SkillUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    changes = data.model_dump(exclude_unset=True)
    owned_skill = (Skill.profile_id == profile.id, Skill.id == skill_id)
    try:
        if changes:
            statement = update(Skill).where(*owned_skill).values(**changes).returning(Skill)
            skill = session.scalars(statement).one_or_none()
        else:
            skill = session.scalar(select(Skill).where(*owned_skill))
        if skill is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        result = SkillRead.model_validate(skill)
        if changes:
            session.commit()
    except IntegrityError as exc:
        session.rollback()
        if isinstance(exc.orig, UniqueViolation):
            raise HTTPException(status_code=409, detail="Skill already exists") from exc
        raise
    return result


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Skill)
        .where(Skill.profile_id == profile.id, Skill.id == skill_id)
        .returning(Skill.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.commit()
    return Response(status_code=204)
