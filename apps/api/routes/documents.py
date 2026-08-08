import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from apps.api.dependencies import get_db_session, get_document_service
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from sqlalchemy.orm import Session
from src.documents.schemas import DocumentStatusResponse, DocumentUploadResponse
from src.documents.service import DocumentService
from src.shared.exceptions import UnsupportedFileTypeError

router = APIRouter()

# TODO: replace with tenant resolved from auth once AUTH_ENABLED is wired up.
DEFAULT_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile,
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    contents = await file.read()
    try:
        document = service.upload(
            tenant_id=DEFAULT_TENANT_ID,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            fileobj=io.BytesIO(contents),
            size_bytes=len(contents),
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DocumentUploadResponse(document_id=document.id, status=document.status)


@router.get("/documents/{document_id}", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: uuid.UUID,
    session: Session = Depends(get_db_session),
) -> DocumentStatusResponse:
    repository = SqlDocumentRepository(session)
    document = repository.get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")

    return DocumentStatusResponse(
        document_id=document.id,
        file_name=document.filename,
        status=document.status,
    )
