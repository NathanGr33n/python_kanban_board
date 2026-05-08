# Kanban Board TUI

A simple, keyboard-driven Kanban board for the terminal built with [Textual](https://textual.textualize.io/).

## Features

- **Three-column board** — To Do, In Progress, and Done
- **Task management** — Create, edit, move, and delete tasks
- **Task properties** — Title, description, and priority level
- **Priority system** — Three levels with color-coded indicators:
  - 🔴 High (red)
  - 🟡 Medium (yellow)
  - 🟢 Low (green)
- **Keyboard-driven** — Navigate and manage everything from the keyboard
- **Modal dialogs** — Focused forms for adding and editing tasks, with confirmation on delete
- **Persistent storage** — Board state saved automatically to `kanban_data.json`
- **Atomic writes** — File saves use a temp-file-and-replace strategy to prevent data corruption
- **Focus follows task** — When moving a task between columns, focus tracks to the destination column

## Requirements

- Python 3.10+
- [Textual](https://textual.textualize.io/) (installed via `requirements.txt`)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/NathanGr33n/python_kanban_board.git
cd python_kanban_board
```

2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Activate the virtual environment (if not already active) and run:

```bash
source venv/bin/activate
python main.py
```

The board launches in your terminal. Tasks are saved automatically to `kanban_data.json` in the working directory.

## Keybindings

| Key | Action |
|-----|--------|
| `a` | Add a new task (opens modal form) |
| `e` | Edit the selected task |
| `d` | Delete the selected task (with confirmation) |
| `l` | Move task one column to the left |
| `r` | Move task one column to the right |
| `Tab` / `Shift+Tab` | Switch focus between columns |
| `↑` / `↓` | Navigate tasks within a column |
| `q` | Quit |

When a modal dialog is open, press `Escape` to cancel and return to the board.

## Project Structure

```
python_kanban_board/
├── main.py              # Entry point
├── requirements.txt     # Dependencies (textual)
├── kanban/
│   ├── __init__.py
│   ├── app.py           # Textual app, widgets, screens, and keybindings
│   ├── models.py        # Task and Board dataclasses, Priority/Column enums
│   └── storage.py       # JSON file load/save with atomic writes
└── kanban_data.json     # Auto-generated board data (gitignored)
```

## Data Storage

Board data is persisted as a JSON file (`kanban_data.json`) in the current working directory. The file is created automatically on the first save. Writes use an atomic temp-file-and-replace pattern to avoid corruption if the process is interrupted.

Example structure:

```json
{
  "tasks": [
    {
      "title": "Implement feature X",
      "description": "Add the new widget",
      "priority": "high",
      "column": "In Progress",
      "id": "a1b2c3d4",
      "created_at": "2026-05-08T02:30:00.000000"
    }
  ]
}
```

## License

MIT
