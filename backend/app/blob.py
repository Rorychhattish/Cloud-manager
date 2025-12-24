import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO


def get_blob_service_client():
    """
    Create and return Azure Blob Storage service client.
    
    Uses environment variable:
    - BLOB_CONNECTION_STRING: Connection string for Azure Storage Account
    
    Returns:
        BlobServiceClient: Azure Blob Storage service client
        
    Raises:
        ValueError: If BLOB_CONNECTION_STRING environment variable is missing
    """
    connection_string = os.getenv("BLOB_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Missing required environment variable: BLOB_CONNECTION_STRING")
    
    return BlobServiceClient.from_connection_string(connection_string)


def upload_file(file_content: bytes, blob_name: str) -> str:
    """
    Upload file to Azure Blob Storage and return the blob URL.
    
    Args:
        file_content (bytes): File content to upload
        blob_name (str): Name/path of the blob in storage
        
    Returns:
        str: Full URL of the uploaded blob
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If upload fails
    """
    container_name = os.getenv("BLOB_CONTAINER")
    if not container_name:
        raise ValueError("Missing required environment variable: BLOB_CONTAINER")
    
    # Get blob service client
    blob_service_client = get_blob_service_client()
    
    # Get container client
    container_client = blob_service_client.get_container_client(container_name)
    
    # Upload blob
    blob_client = container_client.upload_blob(blob_name, file_content, overwrite=True)
    
    # Return blob URL
    return blob_client.url


async def upload_file_async(file_content: bytes, blob_name: str) -> str:
    """
    Asynchronously upload file to Azure Blob Storage and return the blob URL.
    
    Args:
        file_content (bytes): File content to upload
        blob_name (str): Name/path of the blob in storage
        
    Returns:
        str: Full URL of the uploaded blob
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If upload fails
    """
    container_name = os.getenv("BLOB_CONTAINER")
    if not container_name:
        raise ValueError("Missing required environment variable: BLOB_CONTAINER")
    
    from azure.storage.blob.aio import BlobServiceClient as BlobServiceClientAsync
    
    connection_string = os.getenv("BLOB_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Missing required environment variable: BLOB_CONNECTION_STRING")
    
    # Create async blob service client
    async with BlobServiceClientAsync.from_connection_string(connection_string) as blob_service_client:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = await container_client.upload_blob(blob_name, file_content, overwrite=True)
        return blob_client.url


def delete_file(blob_name: str) -> None:
    """
    Delete file from Azure Blob Storage.
    
    Args:
        blob_name (str): Name/path of the blob to delete
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If deletion fails
    """
    container_name = os.getenv("BLOB_CONTAINER")
    if not container_name:
        raise ValueError("Missing required environment variable: BLOB_CONTAINER")
    
    # Get blob service client
    blob_service_client = get_blob_service_client()
    
    # Get container client
    container_client = blob_service_client.get_container_client(container_name)
    
    # Delete blob
    container_client.delete_blob(blob_name)
