from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.blob import upload_file, delete_file
from app.db import get_cosmos_container
from app.models import FileMetadata

router = APIRouter(prefix="/api", tags=["files"])


@router.post("/upload")
async def upload(file: UploadFile = File(...), description: str = Form("")):
    """
    Upload a file and store metadata in Cosmos DB.
    
    Args:
        file: File to upload
        description: Optional file description
        
    Returns:
        FileMetadata: Metadata of the uploaded file
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Generate unique ID and blob name
        file_id = str(uuid.uuid4())
        blob_name = f"{file_id}/{file.filename}"
        
        # Upload to blob storage
        blob_url = upload_file(file_content, blob_name)
        
        # Create file metadata
        metadata = FileMetadata(
            id=file_id,
            filename=file.filename,
            description=description,
            blob_url=blob_url,
            upload_time=datetime.utcnow()
        )
        
        # Store metadata in Cosmos DB
        container = get_cosmos_container()
        container.create_item(body=metadata.model_dump())
        
        return metadata
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/files", response_model=List[FileMetadata])
async def list_files():
    """
    Get list of all uploaded files.
    
    Returns:
        List[FileMetadata]: List of all file metadata
    """
    try:
        container = get_cosmos_container()
        query = "SELECT * FROM c ORDER BY c.upload_time DESC"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return items
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Get download URL for a file by ID.
    
    Args:
        file_id: ID of the file to download
        
    Returns:
        dict: File metadata with blob URL for download
    """
    try:
        container = get_cosmos_container()
        query = f"SELECT * FROM c WHERE c.id = '{file_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_metadata = items[0]
        return file_metadata
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")


@router.delete("/delete/{file_id}")
async def delete_file_endpoint(file_id: str):
    """
    Delete a file by ID.
    
    Args:
        file_id: ID of the file to delete
        
    Returns:
        dict: Confirmation message
    """
    try:
        container = get_cosmos_container()
        query = f"SELECT * FROM c WHERE c.id = '{file_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_metadata = items[0]
        
        # Extract blob name from URL (format: {file_id}/{filename})
        blob_url = file_metadata.get("blob_url", "")
        blob_name = f"{file_id}/{file_metadata.get('filename', '')}"
        
        # Delete from blob storage
        delete_file(blob_name)
        
        # Delete from Cosmos DB
        container.delete_item(item=file_metadata, partition_key=file_metadata.get("id"))
        
        return {"message": f"File {file_id} deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
