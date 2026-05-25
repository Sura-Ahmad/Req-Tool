import io
import pdfplumber
import docx
from fastapi import HTTPException, UploadFile

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


def process_pii(text: str) -> tuple:
    from app.core.pii import has_pii, remove_pii
    return has_pii(text), remove_pii(text)


async def extract_document(file: UploadFile) -> tuple:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the 20 MB limit")
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
        input_type = "pdf"
    else:
        text = extract_text_from_docx(file_bytes)
        input_type = "docx"
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    return text, input_type
