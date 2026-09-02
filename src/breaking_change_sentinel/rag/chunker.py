"""
Module for smart chunking of Markdown migration documentation.
"""

from typing import Any

from langchain_text_splitters import MarkdownHeaderTextSplitter


def chunk_markdown_documentation(markdown_text: str) -> list[dict[str, Any]]:
    """
    Chunks markdown text based on headers (##, ###) to preserve context.

    Args:
            markdown_text: The raw markdown string of the migration guide.

    Returns:
            A list of dictionaries, each containing 'content' (the chunk text)
            and 'metadata' (the headers associated with this chunk).
    """
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]

    txt_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
    splitted_txt = txt_splitter.split_text(markdown_text)

    return [
        {"metadata": obj.metadata, "content": obj.page_content} for obj in splitted_txt
    ]
