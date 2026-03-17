"""
Storage Manager — Unified abstraction for S3 and local file storage.

Usage:
    from utils.storage_manager import storage
    storage.upload_file("path/to/file.json", "raw_papers/file.json")
    storage.save_json({"key": "val"}, "outputs/result.json")
    url = storage.get_file_url("outputs/result.json")

Toggle via env var:
    STORAGE_PROVIDER=s3    → uses AWS S3 (primary)
    STORAGE_PROVIDER=local → uses local filesystem (default fallback)
"""

import os
import json
import logging
import shutil
import time
import uuid
from pathlib import Path

logger = logging.getLogger("storage_manager")

# ---------------------------------------------------------------------------
# Resolve project paths
# ---------------------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
_LOCAL_STORAGE_ROOT = os.path.join(_PROJECT_ROOT, "data", "s3_local")


class StorageManager:
    """Unified storage interface with S3 primary + local fallback."""

    def __init__(self):
        self.provider = os.getenv("STORAGE_PROVIDER", "local").lower()
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "researchnex-bucket")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self._s3_client = None

        # Always ensure local root exists (used for fallback)
        os.makedirs(_LOCAL_STORAGE_ROOT, exist_ok=True)

        if self.provider == "s3":
            self._init_s3()

    # ------------------------------------------------------------------
    # S3 client initialisation
    # ------------------------------------------------------------------
    def _init_s3(self):
        try:
            import boto3
            self._s3_client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
            logger.info("S3 client initialised for bucket '%s'", self.bucket_name)
        except Exception as e:
            logger.warning("Failed to initialise S3 client, falling back to local: %s", e)
            self._s3_client = None

    @property
    def _use_s3(self) -> bool:
        return self.provider == "s3" and self._s3_client is not None

    # ------------------------------------------------------------------
    # Local helpers
    # ------------------------------------------------------------------
    def _local_path(self, key: str) -> str:
        path = os.path.join(_LOCAL_STORAGE_ROOT, key.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upload_file(self, local_path: str, s3_key: str) -> str | None:
        """Upload a local file. Returns the S3 key on success or None."""
        if self._use_s3:
            try:
                self._s3_client.upload_file(local_path, self.bucket_name, s3_key)
                logger.info("Uploaded %s → s3://%s/%s", local_path, self.bucket_name, s3_key)
                return s3_key
            except Exception as e:
                logger.warning("S3 upload failed, saving locally: %s", e)

        # Local fallback
        dest = self._local_path(s3_key)
        if os.path.abspath(local_path) != os.path.abspath(dest):
            shutil.copy2(local_path, dest)
        logger.info("Saved locally: %s", dest)
        return s3_key

    def upload_bytes(self, data: bytes, s3_key: str) -> str | None:
        """Upload raw bytes. Returns the S3 key on success or None."""
        if self._use_s3:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=data,
                )
                logger.info("Uploaded bytes → s3://%s/%s", self.bucket_name, s3_key)
                return s3_key
            except Exception as e:
                logger.warning("S3 bytes upload failed, saving locally: %s", e)

        dest = self._local_path(s3_key)
        with open(dest, "wb") as f:
            f.write(data)
        logger.info("Saved bytes locally: %s", dest)
        return s3_key

    def download_file(self, s3_key: str, local_path: str) -> str | None:
        """Download a file from storage to a local path. Returns local_path or None."""
        if self._use_s3:
            try:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                self._s3_client.download_file(self.bucket_name, s3_key, local_path)
                logger.info("Downloaded s3://%s/%s → %s", self.bucket_name, s3_key, local_path)
                return local_path
            except Exception as e:
                logger.warning("S3 download failed, trying local: %s", e)

        # Local fallback
        src = self._local_path(s3_key)
        if os.path.exists(src):
            if os.path.abspath(src) != os.path.abspath(local_path):
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                shutil.copy2(src, local_path)
            return local_path
        return None

    def get_file_url(self, s3_key: str, expiry: int = 3600) -> str | None:
        """Return a presigned URL (S3) or local file path."""
        if self._use_s3:
            try:
                url = self._s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": s3_key},
                    ExpiresIn=expiry,
                )
                return url
            except Exception as e:
                logger.warning("Presigned URL generation failed: %s", e)

        local = self._local_path(s3_key)
        if os.path.exists(local):
            return local
        return None

    def save_json(self, data: dict | list, s3_key: str) -> str | None:
        """Serialize data as JSON and save. Returns the key."""
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False, default=str).encode("utf-8")
        return self.upload_bytes(json_bytes, s3_key)

    def load_json(self, s3_key: str) -> dict | list | None:
        """Load a JSON object from storage."""
        if self._use_s3:
            try:
                resp = self._s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
                body = resp["Body"].read().decode("utf-8")
                return json.loads(body)
            except Exception as e:
                logger.warning("S3 JSON load failed, trying local: %s", e)

        local = self._local_path(s3_key)
        if os.path.exists(local):
            with open(local, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_files(self, prefix: str = "") -> list[dict]:
        """List files under a prefix. Returns list of {key, size, last_modified}."""
        results = []

        if self._use_s3:
            try:
                paginator = self._s3_client.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                    for obj in page.get("Contents", []):
                        results.append({
                            "key": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"].isoformat(),
                        })
                return results
            except Exception as e:
                logger.warning("S3 list failed, trying local: %s", e)

        # Local fallback
        local_prefix_dir = self._local_path(prefix) if prefix else _LOCAL_STORAGE_ROOT
        if os.path.isdir(local_prefix_dir):
            for root, _, files in os.walk(local_prefix_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    rel = os.path.relpath(fpath, _LOCAL_STORAGE_ROOT).replace(os.sep, "/")
                    stat = os.stat(fpath)
                    results.append({
                        "key": rel,
                        "size": stat.st_size,
                        "last_modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(stat.st_mtime)),
                    })
        return results

    @staticmethod
    def generate_project_id() -> str:
        """Generate a unique project id for output storage."""
        return f"{int(time.time())}_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Singleton — mirrors the pattern used in history_manager.py
# ---------------------------------------------------------------------------
storage = StorageManager()
