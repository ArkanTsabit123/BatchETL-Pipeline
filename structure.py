# structure.py
"""
Display project folder structure as a tree.

Excludes virtual environment, cache directories, IDE directories,
logs, and temporary files.
"""

from pathlib import Path
from typing import List, Optional


def show_tree(path: str = ".", prefix: str = "", exclude: Optional[List[str]] = None) -> None:
    """
    Display folder structure as a tree.

    Args:
        path: Root path to display
        prefix: Prefix for tree formatting (used for recursion)
        exclude: List of folder/file names to exclude
    """
    if exclude is None:
        exclude = [
            # Virtual Environment
            'venv', '.venv', 'env',
            # Version Control
            '.git', '.svn', '.hg',
            # Python Cache
            '__pycache__', '.pytest_cache', '.mypy_cache',
            '.ruff_cache', '.tox', '.coverage', 'htmlcov',
            # IDE
            '.vscode', '.idea', '.vs', '.eclipse',
            # Logs & Temp
            'logs', 'log', 'tmp', 'temp',
            # Docker
            '.docker',
            # OS
            '.DS_Store', 'Thumbs.db',
            # Airflow
            'airflow.db', 'airflow.cfg', 'webserver_config.py',
            'plugins', '*.pid',
            # Verification Reports (generated files)
            'phase*_verification.json',
            'phase*_verification_report.txt',
            # Data Files (large files - optional to show)
            # Remove these if you want to see CSV/PARQUET files
            # '*.csv', '*.parquet', '*.db', '*.duckdb',
            # Backup
            '*.bak', '*.tmp', '*.log',
        ]

    path_obj = Path(path)

    try:
        items = [p for p in path_obj.iterdir() if p.name not in exclude]
    except PermissionError:
        return

    folders = sorted([p for p in items if p.is_dir()], key=lambda x: x.name.lower())
    files = sorted([p for p in items if p.is_file()], key=lambda x: x.name.lower())

    all_items = folders + files

    for i, item in enumerate(all_items):
        is_last = (i == len(all_items) - 1)
        connector = "└── " if is_last else "├── "

        if item.is_dir():
            print(f"{prefix}{connector}{item.name}/")
            extension = "    " if is_last else "│   "
            show_tree(str(item), prefix + extension, exclude)
        else:
            # Display file size for better context
            try:
                size_bytes = item.stat().st_size
                if size_bytes > 1024 * 1024 * 100:  # > 100 MB
                    size_str = f"({size_bytes / (1024 * 1024):.0f} MB)"
                elif size_bytes > 1024 * 1024:  # > 1 MB
                    size_str = f"({size_bytes / (1024 * 1024):.1f} MB)"
                elif size_bytes > 1024:  # > 1 KB
                    size_str = f"({size_bytes / 1024:.1f} KB)"
                else:
                    size_str = ""
            except Exception:
                size_str = ""

            print(f"{prefix}{connector}{item.name} {size_str}".strip())


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BATCHETL PIPELINE - PROJECT STRUCTURE")
    print("=" * 60 + "\n")
    show_tree(".")
    print("\n" + "=" * 60)
    print(f"Root: {Path.cwd()}")
    print("=" * 60)