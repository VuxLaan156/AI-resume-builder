from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

DocumentCategory = Literal["personal", "job_description"]
ProcessingStatus = Literal["pending", "processing", "completed", "failed"]


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    category: DocumentCategory
    processing_status: ProcessingStatus
    uploaded_at: datetime
