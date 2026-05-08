# Kanban Board TUI

A simple, keyboard-driven Kanban board for the terminal built with [Textual](https://textual.textualize.io/).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Keybindings

| Key | Action |
|-----|--------|
| `a` | Add a new task |
| `e` | Edit selected task |
| `d` | Delete selected task |
| `l` | Move task left |
| `r` | Move task right |
| `Tab` / `Shift+Tab` | Switch between columns |
| `↑` / `↓` | Navigate tasks within a column |
| `q` | Quit |

## Features

- Three-column board: To Do, In Progress, Done
- Task properties: title, description, priority (high/medium/low)
- Priority color coding (🔴 high, 🟡 medium, 🟢 low)
- Persistent JSON storage
- Modal dialogs for add/edit/delete
