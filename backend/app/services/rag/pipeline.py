from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

from qdrant_client.models import PointStruct
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...models.documents import Document, DocumentChunk
from ..DocumentExtractor import TextBlock
from .chunker import chunk_blocks
from .document_loader import load_document
from .embedder import get_embedder
from .retriever import lexical_indices, rerank_chunks
from .vector_store import search_point_ids, store_points


@dataclass(frozen=True, kw_only=True)
class SearchChunk(TextBlock):
    chunk_id: UUID
    document_id: UUID


def index_document(session: Session, document: Document, source: Path) -> None:
    chunks = [chunk for chunk in chunk_blocks(load_document(source)) if chunk.text.strip()]
    if not chunks:
        raise ValueError("No text could be extracted from this document")

    vectors = get_embedder().embed_documents([chunk.text for chunk in chunks])
    points = []
    for order, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        point_id = uuid5(document.id, str(order))
        session.add(
            DocumentChunk(
                id=point_id,
                document_id=document.id,
                chunk_order=order,
                chunk_content=chunk.text,
                page_number=chunk.page_number,
                qdrant_point_id=point_id,
            )
        )
        points.append(
            PointStruct(
                id=str(point_id),
                vector=vector,
                payload={
                    "user_id": str(document.user_id),
                    "document_id": str(document.id),
                    "page_number": chunk.page_number,
                },
            )
        )
    session.flush()
    store_points(points)
    document.processing_status = "completed"
    document.processing_error = None


def hybrid_search(
    session: Session, user_id: UUID, query: str, *, category: str | None = None
) -> list[SearchChunk]:
    statement = (
        select(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.user_id == user_id, Document.processing_status == "completed")
        .order_by(DocumentChunk.document_id, DocumentChunk.chunk_order)
    )
    if category is not None:
        statement = statement.where(Document.category == category)
    rows = session.scalars(statement).all()
    if not rows:
        return []

    chunks = [
        SearchChunk(
            chunk_id=row.id,
            document_id=row.document_id,
            text=row.chunk_content,
            page_number=row.page_number,
        )
        for row in rows
    ]
    lexical = [chunks[index] for index in lexical_indices(query, chunks, 20)]
    by_point_id = {
        str(row.qdrant_point_id): chunk
        for row, chunk in zip(rows, chunks, strict=True)
        if row.qdrant_point_id is not None
    }
    semantic = []
    if by_point_id:
        point_ids = search_point_ids(
            get_embedder().embed_query(query),
            user_id,
            [UUID(point_id) for point_id in by_point_id],
            limit=20,
        )
        semantic = [by_point_id[point_id] for point_id in point_ids if point_id in by_point_id]

    return rank_hybrid(query, lexical, semantic)


def rank_hybrid(
    query: str, lexical: list[SearchChunk], semantic: list[SearchChunk]
) -> list[SearchChunk]:
    scores: dict[UUID, float] = defaultdict(float)
    candidates: dict[UUID, SearchChunk] = {}
    for ranking in (lexical, semantic):
        for position, chunk in enumerate(ranking, start=1):
            scores[chunk.chunk_id] += 1 / (60 + position)
            candidates[chunk.chunk_id] = chunk
    fused = sorted(candidates.values(), key=lambda chunk: scores[chunk.chunk_id], reverse=True)
    return rerank_chunks(query, fused[:20], 5)
