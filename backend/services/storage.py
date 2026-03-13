import os
import shutil
from typing import Optional
from pathlib import Path
from abc import ABC, abstractmethod
import boto3
from config import Config

class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    async def save_file(self, file_path: str, file_content: bytes) -> str:
        """Save a file and return the storage path."""
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file content."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """Get a public URL for the file."""
        pass

class LocalStorageProvider(StorageProvider):
    """Local file system storage provider."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file_path: str, file_content: bytes) -> str:
        """Save a file locally."""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(file_content)
        return str(full_path)
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Get file content from local storage."""
        full_path = self.base_path / file_path
        if full_path.exists():
            with open(full_path, 'rb') as f:
                return f.read()
        return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from local storage."""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    async def get_file_url(self, file_path: str) -> str:
        """Get file URL (for local storage, returns the file path)."""
        return f"/downloads/{file_path}"

class S3StorageProvider(StorageProvider):
    """AWS S3 storage provider."""
    
    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    
    async def save_file(self, file_path: str, file_content: bytes) -> str:
        """Save a file to S3."""
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=file_path,
            Body=file_content
        )
        return file_path
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Get file from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return response['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        """Get a signed URL for the file."""
        url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': file_path},
            ExpiresIn=3600  # 1 hour
        )
        return url

class StorageService:
    """Storage service with provider abstraction."""
    
    def __init__(self):
        config = Config()
        
        if config.USE_S3:
            self.provider = S3StorageProvider(
                bucket_name=config.AWS_S3_BUCKET,
                region=config.AWS_S3_REGION,
                access_key=config.AWS_ACCESS_KEY_ID,
                secret_key=config.AWS_SECRET_ACCESS_KEY
            )
        else:
            self.provider = LocalStorageProvider(config.UPLOAD_DIR)
    
    async def save_file(self, file_path: str, file_content: bytes) -> str:
        """Save a file directly (low-level)."""
        return await self.provider.save_file(file_path, file_content)
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Get a file directly (low-level)."""
        return await self.provider.get_file(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file directly (low-level)."""
        return await self.provider.delete_file(file_path)
    
    async def save_dataset(self, user_id: str, project_id: str, dataset_id: str, file_content: bytes, filename: str) -> str:
        """Save a dataset file."""
        # Create structured path
        file_path = f"datasets/{user_id}/{project_id}/{dataset_id}/{filename}"
        return await self.provider.save_file(file_path, file_content)
    
    async def get_dataset(self, file_path: str) -> Optional[bytes]:
        """Get a dataset file."""
        return await self.provider.get_file(file_path)
    
    async def delete_dataset(self, file_path: str) -> bool:
        """Delete a dataset file."""
        return await self.provider.delete_file(file_path)
    
    async def get_dataset_url(self, file_path: str) -> str:
        """Get a downloadable URL for a dataset."""
        return await self.provider.get_file_url(file_path)
    
    async def save_report(self, user_id: str, dataset_id: str, report_content: bytes, filename: str) -> str:
        """Save a report file."""
        file_path = f"reports/{user_id}/{dataset_id}/{filename}"
        return await self.provider.save_file(file_path, report_content)

# Singleton instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
