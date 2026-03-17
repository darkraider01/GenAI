"""
Tests for the StorageManager (local provider mode — no AWS credentials needed).
"""
import os
import json
import tempfile
import shutil
import pytest

# Patch env BEFORE importing storage_manager
os.environ["STORAGE_PROVIDER"] = "local"

import sys
# Ensure backend dir is on path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from utils.storage_manager import StorageManager


@pytest.fixture
def tmp_storage(tmp_path, monkeypatch):
    """Create a StorageManager that uses a temp directory as local root."""
    monkeypatch.setenv("STORAGE_PROVIDER", "local")
    mgr = StorageManager()
    # Override internal local root to temp dir
    import utils.storage_manager as sm
    original_root = sm._LOCAL_STORAGE_ROOT
    sm._LOCAL_STORAGE_ROOT = str(tmp_path)
    mgr.provider = "local"
    yield mgr, tmp_path
    sm._LOCAL_STORAGE_ROOT = original_root


class TestSaveAndLoadJson:
    def test_roundtrip(self, tmp_storage):
        mgr, tmp_path = tmp_storage
        data = {"topic": "AI in Healthcare", "score": 0.95, "tags": ["ml", "bio"]}
        key = "outputs/test_result.json"

        mgr.save_json(data, key)
        loaded = mgr.load_json(key)

        assert loaded is not None
        assert loaded["topic"] == "AI in Healthcare"
        assert loaded["score"] == 0.95
        assert loaded["tags"] == ["ml", "bio"]

    def test_load_missing_returns_none(self, tmp_storage):
        mgr, _ = tmp_storage
        assert mgr.load_json("nonexistent/file.json") is None


class TestUploadAndDownload:
    def test_upload_file(self, tmp_storage, tmp_path):
        mgr, _ = tmp_storage

        # Create a source file
        src = tmp_path / "source.txt"
        src.write_text("hello world")

        key = mgr.upload_file(str(src), "raw_papers/source.txt")
        assert key == "raw_papers/source.txt"

    def test_download_file(self, tmp_storage, tmp_path):
        mgr, _ = tmp_storage

        # Upload first
        src = tmp_path / "upload.txt"
        src.write_text("test content")
        mgr.upload_file(str(src), "test/upload.txt")

        # Download
        dest = str(tmp_path / "downloaded.txt")
        result = mgr.download_file("test/upload.txt", dest)
        assert result is not None
        assert os.path.exists(dest)
        with open(dest) as f:
            assert f.read() == "test content"

    def test_download_missing(self, tmp_storage, tmp_path):
        mgr, _ = tmp_storage
        dest = str(tmp_path / "nope.txt")
        result = mgr.download_file("nonexistent/key.txt", dest)
        assert result is None


class TestUploadBytes:
    def test_upload_and_load(self, tmp_storage):
        mgr, _ = tmp_storage
        data = b"raw binary content"
        key = mgr.upload_bytes(data, "raw_papers/test.pdf")

        assert key == "raw_papers/test.pdf"
        url = mgr.get_file_url(key)
        assert url is not None
        assert os.path.exists(url)


class TestGetFileUrl:
    def test_returns_path_for_existing_file(self, tmp_storage):
        mgr, _ = tmp_storage
        mgr.save_json({"x": 1}, "outputs/url_test.json")
        url = mgr.get_file_url("outputs/url_test.json")
        assert url is not None
        assert os.path.exists(url)

    def test_returns_none_for_missing(self, tmp_storage):
        mgr, _ = tmp_storage
        assert mgr.get_file_url("missing/key.json") is None


class TestListFiles:
    def test_list_outputs(self, tmp_storage):
        mgr, _ = tmp_storage
        mgr.save_json({"a": 1}, "outputs/file1.json")
        mgr.save_json({"b": 2}, "outputs/file2.json")
        mgr.save_json({"c": 3}, "other/file3.json")

        results = mgr.list_files("outputs")
        keys = [r["key"] for r in results]

        assert len(results) == 2
        assert "outputs/file1.json" in keys
        assert "outputs/file2.json" in keys

    def test_list_empty(self, tmp_storage):
        mgr, _ = tmp_storage
        results = mgr.list_files("nonexistent_prefix")
        assert results == []


class TestGenerateProjectId:
    def test_unique_ids(self):
        id1 = StorageManager.generate_project_id()
        id2 = StorageManager.generate_project_id()
        assert id1 != id2
        assert "_" in id1  # format: timestamp_hex
