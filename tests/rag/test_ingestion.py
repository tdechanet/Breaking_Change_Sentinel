"""
Integration tests for the documentation ingestion pipeline.
"""

from pathlib import Path
from breaking_change_sentinel.rag.ingestion import DocumentationIngestionPipeline
from breaking_change_sentinel.rag.vector_store import MigrationVectorStore


def test_ingest_directory_populates_vector_store(tmp_path: Path) -> None:
    """
    Ensures that a directory with multiple markdown files is fully ingested
    with preserved hierarchy and enriched source metadata.
    """
    # 1. Create a dummy documentation hierarchy
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    v1_to_v2_file = docs_dir / "migration_v2.md"
    v1_to_v2_file.write_text(
        "# Migration Guide\n\n"
        "## Validators\n\n"
        "Use @field_validator instead of @validator in Pydantic v2.\n\n"
        "## Root Validators\n\n"
        "Use @model_validator instead of @root_validator.\n",
        encoding="utf-8",
    )

    other_file = docs_dir / "settings.md"
    other_file.write_text(
        "# Settings Management\n\n"
        "BaseSettings is now in pydantic-settings standalone package.\n",
        encoding="utf-8",
    )

    # 2. Ingest via in-memory vector store
    store = MigrationVectorStore(location=":memory:")
    pipeline = DocumentationIngestionPipeline(vector_store=store)

    total_chunks = pipeline.ingest_directory(docs_dir)

    # 3. Assertions
    assert total_chunks >= 3

    # Verify search finds the right chunk with enriched file metadata
    results = store.search(query="how to migrate @validator", limit=1)
    assert len(results) == 1
    assert "@field_validator" in results[0]["content"]
    assert results[0]["metadata"]["source_file"] == "migration_v2.md"


def test_ingest_empty_or_missing_directory(tmp_path: Path) -> None:
    """
    Ensures robust handling when given an empty or non-existent path.
    """
    store = MigrationVectorStore(location=":memory:")
    pipeline = DocumentationIngestionPipeline(vector_store=store)

    missing_dir = tmp_path / "non_existent"
    assert pipeline.ingest_directory(missing_dir) == 0
