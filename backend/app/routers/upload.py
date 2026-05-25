from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from app.schemas.upload import TextInput, ProcessedInput
from app.services.auth_service import get_current_user
from app.services import file_service
from app.core.limiter import limiter

router = APIRouter(prefix="/input", tags=["Input"])


@router.post("/text", response_model=ProcessedInput)
@limiter.limit("20/minute")
def process_text(request: Request, data: TextInput, current_user=Depends(get_current_user)):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    pii_found, cleaned_text = file_service.process_pii(data.text)
    return ProcessedInput(
        original_length=len(data.text),
        processed_text=cleaned_text,
        pii_detected=pii_found,
        input_type="text",
    )


@router.post("/document", response_model=ProcessedInput)
@limiter.limit("5/minute")
async def process_document(request: Request, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    text, input_type = await file_service.extract_document(file)
    pii_found, cleaned_text = file_service.process_pii(text)
    return ProcessedInput(
        original_length=len(text),
        processed_text=cleaned_text,
        pii_detected=pii_found,
        input_type=input_type,
    )
