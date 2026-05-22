import os
from urllib.parse import urlparse

from networksecurity.logging.logger import logging


class S3Sync:
    def __init__(self):
        self._boto3 = None
        try:
            import boto3  # type: ignore

            self._boto3 = boto3
        except Exception:
            self._boto3 = None

        self._credentials_missing = False

    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str) -> None:
        try:
            if not os.path.exists(folder):
                logging.info("Skipping S3 sync because folder does not exist: %s", folder)
                return

            if not aws_bucket_url.startswith("s3://"):
                raise ValueError(f"Invalid S3 URL: {aws_bucket_url}")

            if self._boto3 is None:
                logging.info(
                    "boto3 is not installed. Skipping S3 sync for folder %s to %s",
                    folder,
                    aws_bucket_url,
                )
                return

            parsed_url = urlparse(aws_bucket_url)
            bucket_name = parsed_url.netloc
            prefix = parsed_url.path.lstrip("/")

            s3_client = self._boto3.client("s3")

            for root, _, files in os.walk(folder):
                for file_name in files:
                    local_file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(local_file_path, folder).replace("\\", "/")
                    s3_key = f"{prefix}/{relative_path}" if prefix else relative_path
                    s3_client.upload_file(local_file_path, bucket_name, s3_key)

            logging.info("Synced folder %s to %s", folder, aws_bucket_url)

        except Exception as e:
            error_message = str(e).lower()
            if "unable to locate credentials" in error_message or "no credentials" in error_message:
                if not self._credentials_missing:
                    logging.info(
                        "AWS credentials are unavailable. Skipping S3 sync for folder %s to %s",
                        folder,
                        aws_bucket_url,
                    )
                    self._credentials_missing = True
                return

            logging.info(
                "S3 sync failed for folder %s to %s. Skipping because this is not required for local runs: %s",
                folder,
                aws_bucket_url,
                e,
            )
            return