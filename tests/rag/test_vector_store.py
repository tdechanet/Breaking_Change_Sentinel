"""
Integration and behavioral tests for hybrid search (Dense + BM25 RRF).
"""

from typing import Any
import pytest
from breaking_change_sentinel.rag.vector_store import MigrationVectorStore


@pytest.fixture
def populated_vector_store() -> MigrationVectorStore:
    """
    Instantiates an in-memory vector store populated with realistic migration rules.
    """
    store = MigrationVectorStore(location=":memory:")

    corpus: list[dict[str, Any]] = [
        {
            "content": "Use @field_validator to validate individual fields in Pydantic v2. Replaces @validator.",
            "metadata": {"rule_id": "field_validator_rule"},
        },
        {
            "content": "Use @model_validator(mode='before') or mode='after' for whole-model validation. Replaces @root_validator.",
            "metadata": {"rule_id": "model_validator_rule"},
        },
        {
            "content": "ConfigDict replaces the inner Config class in Pydantic v2 for model configuration.",
            "metadata": {"rule_id": "config_dict_rule"},
        },
        {
            "content": "BaseSettings has been moved out of core pydantic to pydantic-settings standalone package.",
            "metadata": {"rule_id": "base_settings_rule"},
        },
    ]

    store.index_chunks(corpus)
    return store


def test_sparse_anchor_wins_on_exact_symbol(
    populated_vector_store: MigrationVectorStore,
) -> None:
    """
    Scenario 1: Lexical search must lift the exact symbol match (@root_validator)
    even if the dense model hesitates between model-level and field-level validators.
    """
    results = populated_vector_store.search(
        query="migration guide for @root_validator", limit=1
    )

    assert len(results) == 1
    assert results[0]["metadata"]["rule_id"] == "model_validator_rule"


def test_dense_semantic_wins_on_paraphrase_without_keywords(
    populated_vector_store: MigrationVectorStore,
) -> None:
    """
    Scenario 2: Semantic search must retrieve the target chunk when the query
    contains zero lexical overlap with the stored document.
    """
    # Notice: None of the words 'entire schema sanity checks' exist in the chunks
    results = populated_vector_store.search(
        query="inspect the entire schema sanity checks across all attributes",
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["metadata"]["rule_id"] == "model_validator_rule"


def test_rrf_prioritizes_consensus_over_unilateral_outlier(
    populated_vector_store: MigrationVectorStore,
) -> None:
    """
    Scenario 3: A query combining both intent and specific configuration
    must rank the relevant chunk at the top by gathering points from both rankers.
    """
    results = populated_vector_store.search(
        query="How do I change model configuration settings without inner classes?",
        limit=2,
    )

    assert len(results) >= 1
    # ConfigDict rule addresses both 'model configuration' and 'inner classes'
    assert results[0]["metadata"]["rule_id"] == "config_dict_rule"
