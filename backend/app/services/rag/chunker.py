from pathlib import Path

from backend.app.services.DocumentExtractor import TextBlock

def chunk_text(
        text: str,
        chunk_size: int = 800,
        overlap: int = 100
) -> list[str]:
    """
    Split text into overlapping character chunks.
    Example:
        text = "ABCDEFGHIJ"
        chunk_size = 4
        overlap = 1

    Expected:
        ["ABCD", "DEFG", "GHIJ"]
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap < 0:
        raise ValueError("overlap must be a non-negative integer.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")
    step_size = chunk_size - overlap
    chunks = []
    for i in range(0, len(text), step_size):
        chunk = text[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
        if i + chunk_size >= len(text):
            break
    return chunks
def chunk_blocks(blocks: list[TextBlock]) -> list[TextBlock]:
    return [
        TextBlock(text=chunk, page_number=block.page_number)
        for block in blocks
        if block.text.strip()
        for chunk in chunk_text(block.text)
    ]
