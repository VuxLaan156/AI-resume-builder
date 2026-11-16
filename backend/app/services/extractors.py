from .DocumentExtractor import DocumentExtractor
from .doc_extraction import DocExtractor
from .docx_extraction import DocxExtractor
from .image_extraction import ImageExtractor
from .pdf_extraction import PdfExtractor
from .txt_extraction import TxtExtractor

EXTRACTORS: dict[str, type[DocumentExtractor]] = {
    ".pdf": PdfExtractor,
    ".txt": TxtExtractor,
    ".doc": DocExtractor,
    ".docx": DocxExtractor,
    ".png": ImageExtractor,
    ".jpg": ImageExtractor,
    ".jpeg": ImageExtractor,
}
