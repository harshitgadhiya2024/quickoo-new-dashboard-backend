from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.file import FileUploadResponse
from app.services.s3_service import upload_file_to_s3

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    try:
        return await upload_file_to_s3(
            file_name=file.filename or "upload.bin",
            content_type=file.content_type or "application/octet-stream",
            file_bytes=file_bytes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(exc)}",
        ) from exc
