from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader


def extract_pdf_text(uploaded_file: BinaryIO) -> str:
    """Extract text from a Streamlit uploaded PDF using pypdf."""
    data = uploaded_file.read()
    if not data:
        raise ValueError("The uploaded file is empty.")

    reader = PdfReader(BytesIO(data))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ValueError("Encrypted PDFs are not supported in this first version.") from exc

    pages = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            pages.append(f"\n--- Page {index} ---\n{text.strip()}")

    return "\n".join(pages).strip()


def validate_pdf_text(text: str, min_chars: int = 200) -> None:
    """Fail early when a PDF is scanned or too sparse for useful LLM analysis."""
    if not text:
        raise ValueError(
            "No readable text was found. Try a text-based PDF instead of a scanned image PDF."
        )

    if len(text) < min_chars:
        raise ValueError(
            "The PDF text is too short for a useful study plan. Upload more complete material."
        )
