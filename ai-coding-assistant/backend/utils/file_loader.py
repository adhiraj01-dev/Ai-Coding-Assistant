"""
File Loader Utility - Loads code files from a project directory.
"""

import os
import logging
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)

# File extensions to include during ingestion
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c",
    ".h", ".go", ".rs", ".rb", ".php", ".cs", ".kt", ".swift",
    ".sh", ".sql", ".html", ".css", ".md", ".yaml", ".yml",
    ".json", ".toml", ".xml", ".env.example",
}

# Directories to skip
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "env", ".env", "dist", "build", ".idea", ".vscode",
    "data", "vector_store", ".mypy_cache", ".pytest_cache",
}


def iter_code_files(root_dir: str) -> Generator[tuple[str, str], None, None]:
    """
    Walk a directory tree and yield (filepath, content) for supported files.

    Args:
        root_dir: Root directory to scan.

    Yields:
        Tuples of (relative_filepath, file_content).
    """
    root = Path(root_dir)
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_dir}")

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Skip very large files (> 1MB)
            if filepath.stat().st_size > 1_000_000:
                logger.warning(f"Skipping large file: {filepath}")
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                if content.strip():
                    relative = str(filepath.relative_to(root))
                    yield relative, content
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")


def load_single_file(filepath: str) -> str:
    """Read a single file and return its content."""
    try:
        return Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        raise


def get_file_tree(root_dir: str) -> dict:
    """
    Build a nested dictionary representing the project file tree.

    Returns:
        Dict with directory structure and file list.
    """
    root = Path(root_dir)
    tree = {"name": root.name, "type": "directory", "children": []}

    def build_tree(path: Path, node: dict):
        try:
            items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
            for item in items:
                if item.name in SKIP_DIRS or item.name.startswith("."):
                    continue
                if item.is_dir():
                    child = {"name": item.name, "type": "directory", "children": []}
                    build_tree(item, child)
                    node["children"].append(child)
                elif item.suffix.lower() in SUPPORTED_EXTENSIONS:
                    node["children"].append({"name": item.name, "type": "file"})
        except PermissionError:
            pass

    build_tree(root, tree)
    return tree
