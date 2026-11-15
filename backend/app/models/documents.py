from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.session import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("category IN ('personal', 'job_description')"),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')"
        ),
        UniqueConstraint("user_id", "id", "category"),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    processing_status: Mapped[str] = mapped_column(Text, server_default="pending")
    processing_error: Mapped[str | None] = mapped_column(Text)
