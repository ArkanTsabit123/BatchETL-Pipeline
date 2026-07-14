# structure.py
"""
Script to display project folder structure.

Excludes:
    - Virtual environment (venv/)
    - Git directory (.git/)
    - Cache directories (__pycache__, .pytest_cache)
    - IDE directories (.vscode, .idea)
    - Logs directory (logs/)
    - Temporary files
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
            # Data Files (keep .gitkeep)
            '*.csv', '*.parquet', '*.db', '*.duckdb',
            # Docker
            '.docker',
            # OS
            '.DS_Store', 'Thumbs.db',
            # Airflow
            'airflow.db', 'airflow.cfg', 'webserver_config.py',
            'plugins', '*.pid',
            # Streamlit
            '.streamlit',
            # Verification Reports
            'phase*_verification.json',
            'phase*_verification_report.txt',
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
            print(f"{prefix}{connector}{item.name}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BATCHETL PIPELINE - PROJECT STRUCTURE")
    print("=" * 60 + "\n")
    show_tree(".")
    print("\n" + "=" * 60)
    print(f"Root: {Path.cwd()}")
    print("=" * 60)