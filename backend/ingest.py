from typing import Tuple
from io import BytesIO
import pdfplumber
from docx import Document

PAGE_MARK = "\n\n===PAGE===\n\n"
RAW_SIZE_CAP = 5_000_000      # ~5 MB
CHAR_CAP = 60_000             # hard cap to protect runtime
DEFAULT_MAX_PAGES = 20

def extract_text(file, max_pages: int = DEFAULT_MAX_PAGES, max_chars: int = CHAR_CAP) -> Tuple[str, str]:
    name = (file.filename or "").lower()
    raw = file.file.read() or b""

    if len(raw) > RAW_SIZE_CAP:
        raw = raw[:RAW_SIZE_CAP]

    if name.endswith(".pdf"):
        text = _pdf_text(raw, max_pages)
        return text[:max_chars], "pdf"
    if name.endswith(".docx"):
        text = _docx_text(raw)
        return text[:max_chars], "docx"
    # txt fallback
    return raw.decode("utf-8", errors="ignore")[:max_chars], "txt"

def _pdf_text(raw: bytes, max_pages: int) -> str:
    out = []
    with pdfplumber.open(BytesIO(raw)) as pdf:
        pages = min(len(pdf.pages), max_pages)
        for i in range(pages):
            # pdfplumber returns None on image-only pages (no OCR here by design)
            out.append(pdf.pages[i].extract_text() or "")
            if i < pages - 1:
                out.append(PAGE_MARK)
    return "\n".join(out).strip()

def _docx_text(raw: bytes) -> str:
    doc = Document(BytesIO(raw))
    return "\n".join(p.text for p in doc.paragraphs)
