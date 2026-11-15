from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import delete, select, update

from ..models.certifications import Certification
from ..schemas.certifications import CertificationCreate, CertificationRead, CertificationUpdate
from .dependencies import DatabaseSession
from .profiles import CurrentUser, find_profile

router = APIRouter(prefix="/profiles/me/certifications", tags=["certifications"])


@router.get("", response_model=list[CertificationRead])
def list_certifications(session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        select(Certification)
        .where(Certification.profile_id == profile.id)
        .order_by(Certification.name, Certification.id)
    )
    return session.scalars(statement).all()


@router.post("", response_model=CertificationRead, status_code=201)
def create_certification(data: CertificationCreate, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    entry = Certification(profile_id=profile.id, **data.model_dump())
    session.add(entry)
    session.flush()
    result = CertificationRead.model_validate(entry)
    session.commit()
    return result


@router.patch("/{certification_id}", response_model=CertificationRead)
def update_certification(
    certification_id: UUID, data: CertificationUpdate, session: DatabaseSession, user: CurrentUser
):
    profile = find_profile(session, user)
    owned_entry = (Certification.profile_id == profile.id, Certification.id == certification_id)
    changes = data.model_dump(exclude_unset=True)
    if changes:
        statement = update(Certification).where(*owned_entry).values(**changes).returning(Certification)
    else:
        statement = select(Certification).where(*owned_entry)

    entry = session.scalar(statement)
    if entry is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    result = CertificationRead.model_validate(entry)
    if changes:
        session.commit()
    return result


@router.delete("/{certification_id}", status_code=204)
def delete_certification(certification_id: UUID, session: DatabaseSession, user: CurrentUser):
    profile = find_profile(session, user)
    statement = (
        delete(Certification)
        .where(Certification.profile_id == profile.id, Certification.id == certification_id)
        .returning(Certification.id)
    )
    if session.scalar(statement) is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    session.commit()
    return Response(status_code=204)
