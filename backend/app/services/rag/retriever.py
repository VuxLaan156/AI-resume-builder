import re
from collections.abc import Sequence
from functools import cache
from unicodedata import normalize

from rank_bm25 import BM25Plus
from sentence_transformers import CrossEncoder

from ..DocumentExtractor import TextBlock

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", normalize("NFC", text).casefold())

@cache
def _get_reranker() -> CrossEncoder:
    return CrossEncoder("BAAI/bge-reranker-v2-m3")

def retrieve_chunks(
    query: str,
    chunks: Sequence[TextBlock],
    *,
    candidate_k: int = 20,
    top_k: int = 5,
) -> list[TextBlock]:
    """Rerank lexical matches from chunks already scoped to the current user."""
    if not 0 < top_k <= candidate_k:
        raise ValueError("Expected 0 < top_k <= candidate_k")

    query_tokens = _tokenize(query)
    if not query_tokens or not chunks:
        return []

    corpus = [_tokenize(chunk.text) for chunk in chunks]
    query_terms = set(query_tokens)
    matching_indices = [
        index for index, tokens in enumerate(corpus)
        if not query_terms.isdisjoint(tokens)
    ]
    if not matching_indices:
        return []

    scores = BM25Plus(corpus).get_scores(query_tokens)
    matching_indices.sort(key=lambda index: scores[index], reverse=True)
    candidates = [chunks[index] for index in matching_indices[:candidate_k]]
    ranking = _get_reranker().rank(
        query, [chunk.text for chunk in candidates], top_k=top_k
    )
    return [candidates[result["corpus_id"]] for result in ranking]
