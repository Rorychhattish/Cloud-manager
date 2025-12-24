from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileMetadata(BaseModel):
    """Pydantic model for file metadata."""
    
    id: str
    filename: str
    description: Optional[str] = None
    blob_url: str
    upload_time: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "file-123",
                "filename": "document.pdf",
                "description": "Important document",
                "blob_url": "https://storage.azure.com/container/file-123",
                "upload_time": "2025-12-24T10:30:00Z"
            }
        }
