from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.schemas.upload import TextInput, ProcessedInput
from app.core.pii import remove_pii, has_pii
from app.services.auth_service import get_current_user
import pdfplumber
import docx
import io

router = APIRouter(prefix="/input", tags=["Input"])

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

@router.post("/text", response_model=ProcessedInput)
def process_text(data: TextInput, current_user=Depends(get_current_user)):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    pii_found = has_pii(data.text)
    cleaned_text = remove_pii(data.text)
    return ProcessedInput(
        original_length=len(data.text),
        processed_text=cleaned_text,
        pii_detected=pii_found,
        input_type="text"
    )

@router.post("/document", response_model=ProcessedInput)
async def process_document(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    allowed_types = ["application/pdf", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds the 20 MB limit")
    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
        input_type = "pdf"
    else:
        text = extract_text_from_docx(file_bytes)
        input_type = "docx"
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    pii_found = has_pii(text)
    cleaned_text = remove_pii(text)
    return ProcessedInput(
        original_length=len(text),
        processed_text=cleaned_text,
        pii_detected=pii_found,
        input_type=input_type
    )