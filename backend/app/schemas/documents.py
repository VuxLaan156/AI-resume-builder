from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

DocumentCategory = Literal["personal", "job_description"]
ProcessingStatus = Literal["pending", "processing", "completed", "failed"]


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    category: DocumentCategory
    processing_status: ProcessingStatus
    uploaded_at: datetime


class DocumentSearch(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    category: DocumentCategory | None = None


class ChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: int | None
