from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("profile_id", "skill_name"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE")
    )
    skill_name: Mapped[str] = mapped_column(Text)
    proficiency: Mapped[str | None] = mapped_column(Text)