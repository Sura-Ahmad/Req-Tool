import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models.domain import Domain
from app.core.knowledge_base import register_and_load, list_kb_files, delete_kb_file, _kb_path
from app.core.audit import log_action

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def list_files() -> list:
    return list_kb_files()


async def upload_file(
    file: UploadFile,
    domain: str,
    country: str,
    admin_id,
    db: Session,
    request,
) -> dict:
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File must not exceed 50 MB.")

    domain = domain.strip()
    country = country.strip().upper()
    if not domain or not country:
        raise HTTPException(status_code=400, detail="domain and country are required.")

    if not db.query(Domain).filter(Domain.country == country).first():
        raise HTTPException(
            status_code=400,
            detail=f"Country code '{country}' does not match any existing domain. Add a domain for this country first.",
        )

    if not db.query(Domain).filter(Domain.country == country, Domain.name == domain).first():
        raise HTTPException(
            status_code=400,
            detail=f"Domain '{domain}' does not exist for country '{country}'.",
        )

    safe_domain = domain.lower().replace(" ", "_")
    filename = f"{safe_domain}_{country.lower()}.pdf"
    os.makedirs(_kb_path(), exist_ok=True)
    file_path = os.path.join(_kb_path(), filename)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        entry = register_and_load(
            file_path=file_path,
            domain=domain,
            country=country,
            original_name=file.filename or filename,
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to index PDF: {e}")

    log_action(
        db=db,
        user_id=admin_id,
        action="upload_kb_file",
        entity_type="knowledge_base",
        entity_id=entry["id"],
        details={"domain": domain, "country": country, "chunks": entry["chunks"]},
        request=request,
    )
    return entry


def delete_file(entry_id: str, admin_id, db: Session, request) -> dict:
    try:
        deleted = delete_kb_file(entry_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete from knowledge base: {e}")
    if not deleted:
        raise HTTPException(status_code=404, detail="Knowledge-base entry not found.")

    log_action(
        db=db,
        user_id=admin_id,
        action="delete_kb_file",
        entity_type="knowledge_base",
        entity_id=entry_id,
        details={"deleted_entry": entry_id},
        request=request,
    )
    return {"message": f"Knowledge-base entry '{entry_id}' deleted successfully."}
