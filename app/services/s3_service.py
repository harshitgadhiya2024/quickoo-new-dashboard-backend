from uuid import uuid4

import aioboto3

from app.core.config import get_settings
from app.schemas.file import FileUploadResponse


async def upload_file_to_s3(file_name: str, content_type: str, file_bytes: bytes) -> FileUploadResponse:
    settings = get_settings()
    safe_content_type = content_type or "application/octet-stream"
    object_key = f"uploads/{uuid4()}-{file_name}"

    session = aioboto3.Session()
    async with session.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    ) as s3_client:
        await s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Body=file_bytes,
            ContentType=safe_content_type,
        )

    file_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{object_key}"

    return FileUploadResponse(
        file_name=file_name,
        object_key=object_key,
        content_type=safe_content_type,
        size=len(file_bytes),
        file_url=file_url,
    )
