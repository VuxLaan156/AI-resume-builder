import pymupdf

from .DocumentExtractor import DocumentExtractor, TextBlock

class PdfExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> list[TextBlock]:
        with pymupdf.open(stream=data, filetype="pdf") as document:
            return [
                TextBlock(text=page.get_text(), page_number=number)
                for number, page in enumerate(document, start=1)
            ]
