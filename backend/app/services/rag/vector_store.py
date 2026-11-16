import os
from functools import cache
from pathlib import Path
from uuid import UUID

from dotenv import dotenv_values
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

COLLECTION = "resume_chunks_multilingual_minilm"
VECTOR_SIZE = 384


@cache
def get_vector_store() -> QdrantClient:
    env_file = Path(__file__).resolve().parents[4] / "infrastructure/.env"
    settings = {**dotenv_values(env_file), **os.environ}
    port = settings.get("QDRANT_HTTP_PORT") or "16333"
    url = settings.get("QDRANT_URL") or f"http://127.0.0.1:{port}"
    return QdrantClient(url=url, api_key=settings.get("QDRANT_API_KEY"))


def store_points(points: list[models.PointStruct]) -> None:
    client = get_vector_store()
    if not client.collection_exists(COLLECTION):
        try:
            client.create_collection(
                COLLECTION,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE, distance=models.Distance.COSINE
                ),
            )
        except UnexpectedResponse as exc:
            if exc.status_code != 409 or not client.collection_exists(COLLECTION):
                raise
    client.upload_points(COLLECTION, points, wait=True)


def search_point_ids(
    vector: list[float], user_id: UUID, point_ids: list[UUID], limit: int
) -> list[str]:
    if not point_ids:
        return []
    client = get_vector_store()
    if not client.collection_exists(COLLECTION):
        return []
    response = client.query_points(
        COLLECTION,
        query=vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id", match=models.MatchValue(value=str(user_id))
                ),
                models.HasIdCondition(has_id=[str(point_id) for point_id in point_ids]),
            ]
        ),
        limit=limit,
        with_payload=False,
    )
    return [str(point.id) for point in response.points]
