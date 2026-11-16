from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

import pymupdf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import select

from ..models.documents import Document
from ..schemas.documents import ChunkRead, DocumentCategory, DocumentRead, DocumentSearch
from ..services.extractors import EXTRACTORS
from ..services.rag.pipeline import hybrid_search, index_document
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


@router.post("/{document_id}/index", response_model=DocumentRead)
def index_uploaded_document(
    document_id: UUID, session: DatabaseSession, user: CurrentUser
) -> DocumentRead:
    document = session.scalar(
        select(Document)
        .where(Document.id == document_id, Document.user_id == user.id)
        .with_for_update()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.processing_status != "completed":
        source = (UPLOAD_DIRECTORY / document.file_path).resolve()
        if source.parent != UPLOAD_DIRECTORY.resolve() or not source.is_file():
            raise HTTPException(status_code=404, detail="Document file not found")
        try:
            index_document(session, document, source)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Document could not be indexed") from exc
    result = DocumentRead.model_validate(document)
    session.commit()
    return result


@router.post("/search", response_model=list[ChunkRead])
def search_documents(data: DocumentSearch, session: DatabaseSession, user: CurrentUser):
    return hybrid_search(session, user.id, data.query, category=data.category)
