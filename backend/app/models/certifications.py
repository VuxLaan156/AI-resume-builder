from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(Text)
    issuing_body: Mapped[str] = mapped_column(Text)
    issue_date: Mapped[date | None]
