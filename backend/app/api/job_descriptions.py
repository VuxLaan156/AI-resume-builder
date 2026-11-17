from zipfile import BadZipFile

import requests
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..models.documents import Document
from ..schemas.job_descriptions import JDAnalysis, JDAnalysisRequest
from ..services.DocumentExtractor import TextBlock
from ..services.jd_analyzer import analyze_jd
from ..services.rag.document_loader import load_document
from .dependencies import DatabaseSession
from .documents import UPLOAD_DIRECTORY
from .profiles import CurrentUser

router = APIRouter(prefix="/job-descriptions", tags=["job descriptions"])


@router.post("/analyze", response_model=JDAnalysis)
def analyze_job_description(
    data: JDAnalysisRequest, session: DatabaseSession, user: CurrentUser
) -> JDAnalysis:
    if data.text is not None:
        blocks = [TextBlock(data.text)]
    else:
        document = session.scalar(
            select(Document).where(
                Document.id == data.document_id,
                Document.user_id == user.id,
                Document.category == "job_description",
            )
        )
        if document is None:
            raise HTTPException(status_code=404, detail="Job description document not found")

        source = (UPLOAD_DIRECTORY / document.file_path).resolve()
        if source.parent != UPLOAD_DIRECTORY.resolve() or not source.is_file():
            raise HTTPException(status_code=404, detail="Document file not found")
        try:
            blocks = load_document(source)
        except (OSError, ValueError, RuntimeError, BadZipFile, KeyError) as exc:
            raise HTTPException(status_code=422, detail="Document could not be read") from exc

    if not any(block.text.strip() for block in blocks):
        raise HTTPException(status_code=422, detail="The job description has no extractable text")
    try:
        return analyze_jd(blocks)
    except requests.Timeout as exc:
        raise HTTPException(status_code=504, detail="JD analyzer timed out") from exc
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(status_code=502, detail="JD analyzer could not return a validated result") from exc
