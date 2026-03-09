# %%
from pathlib import Path
import os
def find_project_root(start: Path | None = None) -> Path:
    """
    Walk upward from `start` (or cwd) until pyproject.toml is found.
    Returns the project root directory.
    """
    if start is None:
        start = Path.cwd()

    start = start.resolve()

    for path in [start] + list(start.parents):
        if (path / "pyproject.toml").exists():
            return path

    raise FileNotFoundError("Could not find project root (pyproject.toml not found).")

# %%

ROOT_DIR = find_project_root()
DATA_DIR = ROOT_DIR / 'data'
SRC_DIR = ROOT_DIR / 'src'

if __name__ == '__main__':
    
    print(f'Project root: {ROOT_DIR}')
    print(f'Data directory: {DATA_DIR}')
    print(f'Source directory: {SRC_DIR}')
# %%
