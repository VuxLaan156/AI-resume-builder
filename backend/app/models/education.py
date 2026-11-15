from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Education(Base):
    __tablename__ = "education"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    institution: Mapped[str] = mapped_column(Text)
    degree: Mapped[str] = mapped_column(Text)
    graduation_date: Mapped[date | None]
