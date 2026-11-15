from pathlib import Path
from .pdf_extraction import PdfExtractor

pdf = Path(r"C:\Users\Lan\Downloads\DangVuLan_OnlineCodingContestManagement.pdf")
pages = PdfExtractor().extract(pdf.read_bytes())

assert pages, "No pages returned"
assert any(page.text.strip() for page in pages), "No selectable text extracted"

for page in pages:
    print(f"Page {page.page_number}: {page.text.strip()[:120]!r}")

