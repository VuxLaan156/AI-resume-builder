"""Compare retrieval methods on the five JD PDFs in this directory."""

import argparse
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from backend.app.services.rag.chunker import chunk_blocks
from backend.app.services.rag.document_loader import load_document
from backend.app.services.rag.embedder import get_embedder
from backend.app.services.rag.pipeline import SearchChunk, rank_hybrid
from backend.app.services.rag.retriever import lexical_indices
from backend.app.services.rag.vector_store import VECTOR_SIZE

# Each case lists (page, source quote) pairs for facts the answer should cover.
CASES = [
    (1, "skills", "Which programming libraries and data tools should the AI & Machine Learning Engineer know?",
     [(1, "PyTorch, TensorFlow, Scikit-learn"), (1, "SQL/NoSQL")]),
    (1, "requirements", "What academic background and production experience does the AI & Machine Learning Engineer need?",
     [(1, "Tốt nghiệp Đại học trở lên"), (1, "phát triển và triển khai các mô hình")]),
    (2, "skills", "Generative AI & LLM Engineer cần biết những framework và cơ sở dữ liệu vector nào?",
     [(1, "LangChain, LlamaIndex"), (1, "Qdrant, Milvus, Pinecone")]),
    (2, "requirements", "What backend development and document processing experience is expected of the Generative AI & LLM Engineer?",
     [(1, "backend/API bất đồng bộ"), (1, "xử lý dữ liệu đa định dạng")]),
    (3, "skills", "Which vision libraries and model evaluation metrics should the Computer Vision Engineer know?",
     [(1, "OpenCV, PyTorch, Torchvision"), (1, "mAP, IoU, MOTA")]),
    (3, "requirements", "Computer Vision Engineer cần học ngành nào và có kinh nghiệm thực tế với những khó khăn nào của dữ liệu ảnh?",
     [(1, "Khoa học Máy tính, Kỹ thuật Điện tử Viễn thông"), (1, "ánh sáng yếu")]),
    (4, "skills", "Which infrastructure-as-code and observability tools are listed for the MLOps & AI Infrastructure Engineer?",
     [(1, "Terraform hoặc Ansible"), (1, "Prometheus, Grafana, OpenTelemetry")]),
    (4, "requirements", "What background and hands-on cloud or container experience is expected of the MLOps & AI Infrastructure Engineer?",
     [(1, "DevOps, Cloud Infrastructure hoặc MLOps"), (1, "Docker, Kubernetes và ít nhất một nền tảng đám mây")]),
    (5, "skills", "Senior AI Research Engineer cần biết những kỹ năng toán học và công cụ lập trình nào?",
     [(1, "tối ưu hóa phi tuyến"), (1, "Python và PyTorch")]),
    (5, "requirements", "What degree or equivalent experience and evidence of research impact are required of the Senior AI Research Engineer?",
     [(1, "Bằng Thạc sĩ hoặc Tiến sĩ"), (1, "kinh nghiệm nghiên cứu ứng dụng tương đương"),
      (1, "dự án mã nguồn mở có tầm ảnh hưởng hoặc công bố khoa học")]),
]


def load_corpus(directory: Path):
    chunks = []
    document_ids = {}
    for number in sorted({case[0] for case in CASES}):
        sources = sorted(directory.glob(f"JD {number} - *.pdf"))
        if len(sources) != 1:
            raise ValueError(f"Expected exactly one JD {number} PDF in {directory}")
        source = sources[0]
        document_id = uuid5(NAMESPACE_URL, source.name)
        document_ids[number] = document_id
        for order, block in enumerate(chunk_blocks(load_document(source))):
            chunks.append(
                SearchChunk(
                    chunk_id=uuid5(document_id, str(order)),
                    document_id=document_id,
                    text=block.text,
                    page_number=block.page_number,
                )
            )
    return chunks, document_ids


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def evaluate(directory: Path, lexical_only: bool) -> None:
    chunks, document_ids = load_corpus(directory)
    cases = []
    for number, topic, query, evidence in CASES:
        labels = {}
        for page, quote in evidence:
            matching = {
                chunk.chunk_id
                for chunk in chunks
                if chunk.document_id == document_ids[number]
                and chunk.page_number == page
                and normalize(quote) in normalize(chunk.text)
            }
            if not matching:
                raise ValueError(f"Evidence quote missing for JD {number}, page {page}: {quote!r}")
            labels[quote] = matching
        cases.append((number, topic, query, labels))

    methods = ["BM25"] if lexical_only else ["BM25", "Semantic", "Hybrid + rerank"]
    results = {method: [] for method in methods}
    by_id = {str(chunk.chunk_id): chunk for chunk in chunks}
    if not lexical_only:
        print("Embedding the evaluation corpus...", flush=True)
    qdrant = QdrantClient(":memory:") if not lexical_only else None
    try:
        if qdrant is not None:
            embedder = get_embedder()
            vectors = embedder.embed_documents([chunk.text for chunk in chunks])
            qdrant.create_collection(
                "evaluation",
                vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
            )
            qdrant.upsert(
                "evaluation",
                points=[
                    models.PointStruct(id=str(chunk.chunk_id), vector=vector)
                    for chunk, vector in zip(chunks, vectors, strict=True)
                ],
            )

        print(f"{len(cases)} queries | {len(chunks)} chunks | {len(document_ids)} JDs")
        for number, topic, query, labels in cases:
            lexical = [chunks[index] for index in lexical_indices(query, chunks, 20)]
            rankings = {"BM25": lexical}
            if qdrant is not None:
                points = qdrant.query_points(
                    "evaluation", query=embedder.embed_query(query), limit=20
                ).points
                semantic = [by_id[str(point.id)] for point in points]
                rankings["Semantic"] = semantic
                rankings["Hybrid + rerank"] = rank_hybrid(query, lexical, semantic)

            print(f"\nJD {number} | {topic} | {query}")
            for method, ranking in rankings.items():
                ranked_ids = [chunk.chunk_id for chunk in ranking[:5]]
                relevant = set().union(*labels.values())
                rank = next(
                    (i for i, chunk_id in enumerate(ranked_ids, 1) if chunk_id in relevant),
                    None,
                )
                missed = [quote for quote, ids in labels.items() if ids.isdisjoint(ranked_ids)]
                found = len(labels) - len(missed)
                results[method].append((topic, rank, found, len(labels)))
                print(f"  {method:16} first={rank or 'miss'} | evidence={found}/{len(labels)}")
                if missed:
                    print(f"    Missing evidence: {'; '.join(missed)}")

        for group in ("skills", "requirements", "overall"):
            print(f"\n{group.title()}")
            for method, records in results.items():
                scores = [record for record in records if group in (record[0], "overall")]
                hits = sum(rank is not None for _, rank, _, _ in scores)
                mrr = sum(1 / rank for _, rank, _, _ in scores if rank is not None) / len(scores)
                evidence = sum(found for _, _, found, _ in scores)
                total = sum(expected for _, _, _, expected in scores)
                print(
                    f"  {method:16} Hit@5 {hits}/{len(scores)} | MRR@5 {mrr:.3f}"
                    f" | Evidence recall@5 {evidence}/{total} ({evidence / total:.0%})"
                )
    finally:
        if qdrant is not None:
            qdrant.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).parent)
    parser.add_argument("--lexical-only", action="store_true", help="Run BM25 without loading models.")
    args = parser.parse_args()
    evaluate(args.directory, args.lexical_only)
