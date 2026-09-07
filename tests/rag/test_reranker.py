"""
Unit tests for the FlashRank document reranker.
"""

from breaking_change_sentinel.rag.reranker import DocumentReranker


def test_reranker_reorders_documents_by_cross_encoder_relevance() -> None:
    """
    Verifies that the cross-encoder correctly elevates the genuinely relevant chunk
    even when placed at the bottom of the candidate pool.
    """
    reranker = DocumentReranker()

    query = "How to migrate @validator in Pydantic v2?"

    # Simulating candidates returned by vector search where position 0 is distracter context
    candidates = [
        {
            "content": "Pydantic v2 introduces major performance improvements rewritten in Rust core.",
            "metadata": {"section": "overview"},
        },
        {
            "content": "The @validator decorator is deprecated in Pydantic v2. Replace it with @field_validator.",
            "metadata": {"section": "validators"},
        },
    ]

    reranked = reranker.rerank(query=query, documents=candidates, top_n=1)

    assert len(reranked) == 1
    assert reranked[0]["metadata"]["section"] == "validators"
    assert "rerank_score" in reranked[0]
    assert isinstance(reranked[0]["rerank_score"], float)
