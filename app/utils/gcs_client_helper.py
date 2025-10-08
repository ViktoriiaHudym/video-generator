import json
from typing import Dict

from google.cloud import storage

from app.config import GCS_BUCKET_NAME
from app.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    A service for interacting with Google Cloud Storage.
    """

    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = None

    def upload_json(self, data: Dict, remote_path: str) -> str:
        """
        Uploads a dictionary as a JSON file to GCS.

        Args:
            data: The dictionary to upload.
            remote_path: The destination path within the GCS bucket.

        Returns:
            The public URL of the uploaded file.
        """
        if self.bucket is None:
            try:
                self.bucket = self.client.get_bucket(self.bucket_name)
            except Exception as e:
                logger.error("Failed to connect to GCS bucket %s: %s", self.bucket_name, e)
                raise ConnectionError(f"GCS bucket '{self.bucket_name}' not found or accessible.") from e
        
        blob = self.bucket.blob(remote_path)
        json_data = json.dumps(data, indent=4)

        blob.upload_from_string(json_data, content_type="application/json")

        logger.info("Successfully uploaded JSON to gs://%s/%s", self.bucket_name, remote_path)
        return f"https://storage.cloud.google.com/{self.bucket_name}/{remote_path}"


def get_storage_service() -> StorageService:
    """Factory function to get a configured StorageService instance."""
    return StorageService(bucket_name=GCS_BUCKET_NAME)
