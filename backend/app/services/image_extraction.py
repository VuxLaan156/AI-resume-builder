import pymupdf

from .DocumentExtractor import DocumentExtractor, TextBlock


class ImageExtractor(DocumentExtractor):
    def __init__(self, language: str = "eng+vie", tessdata: str | None = None):
        self.language = language
        self.tessdata = tessdata

    def extract(self, data: bytes) -> list[TextBlock]:
        image = pymupdf.Pixmap(data)
        if image.alpha:
            with pymupdf.open() as canvas:
                page = canvas.new_page(width=image.width, height=image.height)
                page.insert_image(page.rect, pixmap=image)
                image = page.get_pixmap()
        elif image.colorspace != pymupdf.csRGB:
            image = pymupdf.Pixmap(pymupdf.csRGB, image)

        searchable_pdf = image.pdfocr_tobytes(
            language=self.language, tessdata=self.tessdata
        )
        with pymupdf.open(stream=searchable_pdf, filetype="pdf") as document:
            text = document[0].get_text().strip()
        return [TextBlock(text)] if text else []
