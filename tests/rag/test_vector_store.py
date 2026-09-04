"""
Unit tests for hybrid search (Dense + Sparse BM25).
"""

from breaking_change_sentinel.rag.vector_store import MigrationVectorStore


def test_hybrid_search_resolves_decorator_ambiguity() -> None:
    """
    Tests that hybrid search correctly ranks exact keyword matches
    over semantically similar but syntactically distinct decorators.
    """
    store = MigrationVectorStore(location=":memory:")

    sample_chunks = [
        {
            "content": "The @validator decorator is deprecated in Pydantic v2. Use @field_validator instead.",
            "metadata": {"decorator": "validator"},
        },
        {
            "content": "The @root_validator decorator is deprecated in Pydantic v2. Use @model_validator instead.",
            "metadata": {"decorator": "root_validator"},
        },
    ]

    store.index_chunks(sample_chunks)

    # Requête avec token exact
    results = store.search(query="How to migrate @root_validator syntax?", limit=1)

    assert len(results) == 1
    assert results[0]["metadata"]["decorator"] == "root_validator"
    assert "@model_validator" in results[0]["content"]
