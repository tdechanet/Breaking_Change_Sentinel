"""
Unit tests for the Qdrant vector store integration.
"""

from breaking_change_sentinel.rag.vector_store import MigrationVectorStore


def test_vector_store_indexing_and_search() -> None:
    """Tests if chunks are correctly embedded, stored, and retrieved."""
    store = MigrationVectorStore(location=":memory:")

    sample_chunks = [
        {
            "content": "The `validator` decorator is deprecated. Use `field_validator` instead.",
            "metadata": {"Header 2": "Changes in Pydantic V2"},
        },
        {
            "content": "BaseSettings has been moved to `pydantic-settings`.",
            "metadata": {"Header 3": "BaseSettings"},
        },
    ]

    store.index_chunks(sample_chunks)
    results = store.search(query="How do I migrate BaseSettings?", limit=1)

    assert len(results) == 1
    assert "pydantic-settings" in results[0]["content"]
    assert results[0]["metadata"]["Header 3"] == "BaseSettings"
