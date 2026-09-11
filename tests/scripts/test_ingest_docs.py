"""
Tests for the documentation ingestion CLI script.
"""

from pathlib import Path
import pytest

from scripts.ingest_docs import run_ingestion


def test_run_ingestion_raises_error_if_docs_dir_missing(tmp_path: Path) -> None:
    """Verifies that run_ingestion raises FileNotFoundError when source dir is missing."""
    missing_dir = tmp_path / "non_existent_docs"
    storage_path = tmp_path / "storage"

    with pytest.raises(FileNotFoundError, match="Source directory does not exist"):
        run_ingestion(docs_dir=missing_dir, storage_path=storage_path)


def test_run_ingestion_empty_directory_returns_zero(tmp_path: Path) -> None:
    """Verifies that an empty source directory indexes zero chunks without error."""
    empty_docs_dir = tmp_path / "empty_docs"
    empty_docs_dir.mkdir()
    storage_path = tmp_path / "storage"

    count = run_ingestion(docs_dir=empty_docs_dir, storage_path=storage_path)

    assert count == 0
    assert storage_path.exists()


def test_run_ingestion_persists_chunks_to_disk(tmp_path: Path) -> None:
    """Verifies that markdown files are ingested and Qdrant creates storage files on disk."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    sample_doc = docs_dir / "sample.md"
    sample_doc.write_text(
        "# Header 1\n\nContent for first chunk.\n\n## Subheader\n\nContent for second chunk."
    )

    storage_path = tmp_path / "persistent_storage"

    indexed_chunks = run_ingestion(docs_dir=docs_dir, storage_path=storage_path)

    # 1. Verification of returned count
    assert indexed_chunks > 0

    # 2. Verification of disk persistence
    assert storage_path.exists()
    assert storage_path.is_dir()

    # Qdrant persists metadata and collection folders on disk
    persisted_files = list(storage_path.iterdir())
    assert len(persisted_files) > 0
