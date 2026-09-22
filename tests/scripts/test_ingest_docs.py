"""
Integration smoke test for the documentation ingestion CLI script.
"""

from pathlib import Path
import subprocess
import sys


def test_run_ingestion_cli_success(tmp_path: Path) -> None:
    """
    Verifies that scripts/ingest_docs.py runs end-to-end via CLI,
    reads source markdown, and creates Qdrant storage files.
    """
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    sample_doc = docs_dir / "sample_rule.md"
    sample_doc.write_text(
        "# Migration Guide\n\n## Section 1\n\nDeprecated feature details."
    )

    storage_dir = tmp_path / "qdrant_storage"

    # Execute the script as an external CLI process
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ingest_docs.py",
            "--docs-dir",
            str(docs_dir),
            "--storage-path",
            str(storage_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # 1. OS exit code must be 0 (success)
    assert result.returncode == 0, f"CLI execution failed:\n{result.stderr}"

    # 2. Verify expected output log
    assert "Ingestion finished successfully" in result.stderr or result.stdout

    # 3. Verify disk persistence
    assert storage_dir.exists()
    assert any(
        storage_dir.iterdir()
    ), "Storage directory should contain Qdrant index files"
