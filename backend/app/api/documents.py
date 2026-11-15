from pathlib import Path
from typing import Annotated
from uuid import uuid4

import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models.documents import Document
from ..schemas.documents import DocumentCategory, DocumentRead
from ..services.extractors import EXTRACTORS
from .dependencies import DatabaseSession
from .profiles import CurrentUser

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIRECTORY = Path(__file__).resolve().parents[2] / "uploads"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def validate_pdf(data: bytes) -> None:
    if b"%PDF-" not in data[:1024]:
        raise HTTPException(status_code=422, detail="Invalid PDF")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            if pdf.needs_pass or pdf.page_count == 0:
                raise HTTPException(
                    status_code=422, detail="Upload an unlocked PDF with at least one page"
                )
    except (pymupdf.FileDataError, pymupdf.EmptyFileError) as exc:
        raise HTTPException(status_code=422, detail="Invalid PDF") from exc


@router.post("", response_model=DocumentRead, status_code=201)
def upload_document(
    file: Annotated[UploadFile, File()],
    session: DatabaseSession,
    user: CurrentUser,
    category: Annotated[DocumentCategory, Form()] = "personal",
) -> DocumentRead:
    file_name = (file.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    extension = Path(file_name).suffix.lower()
    if extension not in EXTRACTORS:
        supported = ", ".join(EXTRACTORS)
        raise HTTPException(status_code=415, detail=f"Supported file types: {supported}")
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File must be 10 MiB or smaller")

    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File must be 10 MiB or smaller")
    if not data:
        raise HTTPException(status_code=422, detail="File is empty")
    if extension == ".pdf":
        validate_pdf(data)

    document_id = uuid4()
    storage_key = f"{document_id}{extension}"
    path = UPLOAD_DIRECTORY / storage_key
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = path.open("xb")
    try:
        with destination:
            destination.write(data)

        document = Document(
            id=document_id,
            user_id=user.id,
            category=category,
            file_name=file_name,
            file_path=storage_key,
        )
        session.add(document)
        session.flush()
        result = DocumentRead.model_validate(document)
        session.commit()
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return result
