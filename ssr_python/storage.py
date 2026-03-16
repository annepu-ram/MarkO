"""
Storage Abstraction Layer — supports Local, Cloudflare R2, and GCS backends.

Usage:
    from storage import create_storage
    storage = create_storage(app.config)
    url = storage.save(file_bytes, 'org_id/site_id/abc123.webp')
"""
import os
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract interface for image storage."""

    @abstractmethod
    def save(self, file_bytes: bytes, storage_path: str, content_type: str = 'image/webp') -> str:
        """Save bytes to storage. Returns the public URL for the file."""
        ...

    @abstractmethod
    def delete(self, storage_path: str) -> bool:
        """Delete a file from storage. Returns True if deleted."""
        ...

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        """Get a servable URL for the given storage path."""
        ...

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check if a file exists at the given path."""
        ...

    def generate_path(self, org_id: str, site_id: str, filename: str) -> str:
        """Generate a tenant-isolated storage path: {org_id}/{site_id}/{filename}."""
        return f'{org_id}/{site_id}/{filename}'


class LocalStorage(StorageBackend):
    """Store files on the local filesystem."""

    def __init__(self, base_dir: str, url_prefix: str = '/uploads'):
        self.base_dir = base_dir
        self.url_prefix = url_prefix

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        full_path = os.path.join(self.base_dir, storage_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(file_bytes)
        return self.get_url(storage_path)

    def delete(self, storage_path):
        full_path = os.path.join(self.base_dir, storage_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_url(self, storage_path):
        return f'{self.url_prefix}/{storage_path}'

    def exists(self, storage_path):
        return os.path.exists(os.path.join(self.base_dir, storage_path))


class R2Storage(StorageBackend):
    """Store files in Cloudflare R2 (S3-compatible API)."""

    def __init__(self, bucket: str, account_id: str = '',
                 access_key: str = '', secret_key: str = '',
                 public_domain: str = ''):
        import boto3
        self.bucket = bucket
        self.public_domain = public_domain
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key or None,
            aws_secret_access_key=secret_key or None,
            region_name='auto',
        )

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=storage_path,
            Body=file_bytes,
            ContentType=content_type,
            CacheControl='public, max-age=31536000',
        )
        return self.get_url(storage_path)

    def delete(self, storage_path):
        self.s3.delete_object(Bucket=self.bucket, Key=storage_path)
        return True

    def get_url(self, storage_path):
        if self.public_domain:
            return f'https://{self.public_domain}/{storage_path}'
        return f'https://{self.bucket}.r2.dev/{storage_path}'

    def exists(self, storage_path):
        try:
            self.s3.head_object(Bucket=self.bucket, Key=storage_path)
            return True
        except self.s3.exceptions.ClientError:
            return False


class GCSStorage(StorageBackend):
    """Store files in Google Cloud Storage."""

    def __init__(self, bucket: str, credentials_path: str = '', cdn_domain: str = ''):
        from google.cloud import storage as gcs
        if credentials_path:
            self.client = gcs.Client.from_service_account_json(credentials_path)
        else:
            self.client = gcs.Client()
        self.bucket_obj = self.client.bucket(bucket)
        self.bucket = bucket
        self.cdn_domain = cdn_domain

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        blob = self.bucket_obj.blob(storage_path)
        blob.upload_from_string(file_bytes, content_type=content_type)
        blob.cache_control = 'public, max-age=31536000'
        blob.patch()
        return self.get_url(storage_path)

    def delete(self, storage_path):
        blob = self.bucket_obj.blob(storage_path)
        blob.delete()
        return True

    def get_url(self, storage_path):
        if self.cdn_domain:
            return f'https://{self.cdn_domain}/{storage_path}'
        return f'https://storage.googleapis.com/{self.bucket}/{storage_path}'

    def exists(self, storage_path):
        return self.bucket_obj.blob(storage_path).exists()


def create_storage(app_config) -> StorageBackend:
    """Factory — creates the right storage backend from app config."""
    backend = app_config.get('STORAGE_BACKEND', 'local')

    if backend == 'r2':
        return R2Storage(
            bucket=app_config['R2_BUCKET'],
            account_id=app_config.get('R2_ACCOUNT_ID', ''),
            access_key=app_config.get('R2_ACCESS_KEY', ''),
            secret_key=app_config.get('R2_SECRET_KEY', ''),
            public_domain=app_config.get('R2_PUBLIC_DOMAIN', ''),
        )
    elif backend == 'gcs':
        return GCSStorage(
            bucket=app_config['GCS_BUCKET'],
            credentials_path=app_config.get('GCS_CREDENTIALS_PATH', ''),
            cdn_domain=app_config.get('GCS_CDN_DOMAIN', ''),
        )
    else:
        return LocalStorage(
            base_dir=app_config.get('UPLOAD_FOLDER', 'instance/uploads'),
            url_prefix='/uploads',
        )
