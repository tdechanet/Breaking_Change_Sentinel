"""
Unit tests for the markdown chunking logic.
"""

from breaking_change_sentinel.rag.chunker import chunk_markdown_documentation


def test_chunk_markdown_documentation() -> None:
    """Tests if markdown is correctly split by headers with metadata."""
    sample_md = """
# Main Title (Ignored for split)
Some intro text.

## Changes in Pydantic V2
The `validator` decorator is deprecated.
Use `field_validator` instead.

### BaseSettings
BaseSettings has been moved to `pydantic-settings`.
	"""

    chunks = chunk_markdown_documentation(sample_md)

    assert len(chunks) >= 2

    # Find the BaseSettings chunk based on its content
    base_settings_chunk = next(
        c for c in chunks if "BaseSettings has been moved" in c["content"]
    )

    # Check if metadata was correctly extracted
    assert "Header 2" in base_settings_chunk["metadata"]
    assert base_settings_chunk["metadata"]["Header 2"] == "Changes in Pydantic V2"
    assert "Header 3" in base_settings_chunk["metadata"]
    assert base_settings_chunk["metadata"]["Header 3"] == "BaseSettings"
