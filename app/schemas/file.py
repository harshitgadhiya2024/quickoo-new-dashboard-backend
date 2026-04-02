from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_name: str
    object_key: str
    content_type: str
    size: int
    file_url: str
