from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from kanban.models import Board

DEFAULT_PATH = Path("kanban_data.json")


def load_board(path: Path = DEFAULT_PATH) -> Board:
    if not path.exists():
        return Board()
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return Board.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return Board()


def save_board(board: Board, path: Path = DEFAULT_PATH) -> None:
    data = json.dumps(board.to_dict(), indent=2)
    dir_path = path.parent if path.parent != Path() else Path(".")
    fd, tmp = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(data)
        os.replace(tmp, str(path))
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
