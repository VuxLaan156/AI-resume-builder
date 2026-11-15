from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import delete, select, update

from ..models.projects import Project
from ..schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile

router = APIRouter(prefix="/profiles/me/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        select(Project)
        .where(Project.profile_id == profile.id)
        .order_by(Project.project_name, Project.id)
    )
    return session.scalars(statement).all()


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(data: ProjectCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    project = Project(profile_id=profile.id, **data.model_dump())
    session.add(project)
    session.flush()
    result = ProjectRead.model_validate(project)
    session.commit()
    return result


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID, data: ProjectUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    owned_project = (Project.profile_id == profile.id, Project.id == project_id)
    changes = data.model_dump(exclude_unset=True)
    if changes:
        statement = update(Project).where(*owned_project).values(**changes).returning(Project)
    else:
        statement = select(Project).where(*owned_project)

    project = session.scalar(statement)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    result = ProjectRead.model_validate(project)
    if changes:
        session.commit()
    return result


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Project)
        .where(Project.profile_id == profile.id, Project.id == project_id)
        .returning(Project.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    session.commit()
    return Response(status_code=204)
