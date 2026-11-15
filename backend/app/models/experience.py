from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Experience(Base):
    __tablename__ = "work_experiences"
    __table_args__ = (CheckConstraint("end_date >= start_date"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    job_title: Mapped[str] = mapped_column(Text)
    company_name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date]
    end_date: Mapped[date | None]
