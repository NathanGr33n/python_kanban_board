# kanban.py
# NathanGr33n
# August 2025
# A simple terminal-based Kanban board with three columns: To Do, In Progress, Done

import json
import os
import uuid
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

#region Setup
#--------------- Setup ---------------#
console = Console()
# File where tasks are stored
DATA_FILE = 'kanban_data.json'
# Initial board structure
board = {
    "To Do": [],
    "In Progress": [],
    "Done": []
}
#endregion

#region HelperFuntions
# ------------------------------
# Helper Functions
# ------------------------------

#region Load&Save
def load_board():
    """Load the saved board from a JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            for column in board:
                board[column] = data.get(column, [])
    else:
        save_board()

def save_board():
    """Save the current board state to a JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(board, file, indent=2)
#endregion

#region Display
def display_board():
    """Display the Kanban board in the terminal."""
    console.clear()
    console.rule("[bold red]📋 KANBAN BOARD[/]")
    print("\n📋 KANBAN BOARD\n" + "-" * 80)
    max_tasks = max(len(board[col]) for col in board)
    columns = list(board.keys())

    # Create a table with three columns
    table = Table(show_header=True, header_style="bold cyan", box=box.DOUBLE_EDGE)
    for col in columns:
        table.add_column(col, style="bold")

    for i in range(max_tasks):
        row = []
        for col in columns:
            try:
                task = board[col][i]
                short_id = task["id"][:4]
                row.append(f"[yellow]{task['title']}[/] ({short_id})")
            except IndexError:
                row.append("")
        table.add_row(*row)

    console.print(table)
#endregion

#region Task Operations
# ------------------------------
# Task Operations
# ------------------------------

def add_task():
    """Add a new task to the 'To Do' column."""
    title = Prompt.ask("[bold green]Enter task title[/]")
    if title.strip():
        task = {
            "id": str(uuid.uuid4()),
            "title": title.strip()
        }
        board["To Do"].append(task)
        save_board()
        console.print("[green]✅ Task added to To Do![/]")
    else:
        console.print("[red]⚠️ Task title cannot be empty.[/]")

def move_task():
    """Move a task from one column to another."""
    display_board()
    task_id = Prompt.ask("[bold blue]Enter the task ID to move (first 4 chars)[/]").strip()
    found = None

    for col in board:
        for task in board[col]:
            if task["id"].startswith(task_id):
                found = (col, task)
                break
        if found:
            break

    if not found:
        console.print("[red]❌ Task not found.[/]")
        return

    from_col, task = found
    to_col = Prompt.ask(f"Move to which column?", choices=list(board.keys()))
    board[from_col].remove(task)
    board[to_col].append(task)
    save_board()
    console.print(f"[green]✅ Moved task to {to_col}.[/]")

def delete_task():
    """Delete a task from the board."""
    display_board()
    task_id = Prompt.ask("[bold red]Enter the task ID to delete (first 4 chars)[/]").strip()
    for col in board:
        for task in board[col]:
            if task["id"].startswith(task_id):
                board[col].remove(task)
                save_board()
                console.print("[bold red]🗑️ Task deleted.[/]")
                return
    console.print("[red]❌ Task not found.[/]")

#endregion

#region Main Menu
# ------------------------------
# Main Menu
# ------------------------------

def main_menu():
    load_board()
    while True:
        console.print(Panel.fit(
            "[bold cyan]1.[/] View Board\n"
            "[bold cyan]2.[/] Add Task\n"
            "[bold cyan]3.[/] Move Task\n"
            "[bold cyan]4.[/] Delete Task\n"
            "[bold cyan]5.[/] Exit",
            title="[bold magenta]KANBAN MENU",
            subtitle="Choose an option"
        ))

        choice = Prompt.ask("Enter choice", choices=['1', '2', '3', '4', '5'])
        if choice == '1':
            display_board()
        elif choice == '2':
            add_task()
        elif choice == '3':
            move_task()
        elif choice == '4':
            delete_task()
        elif choice == '5':
            console.print("[bold yellow]👋 Exiting Kanban Board. Goodbye![/]")
            break

#endregion

#endregion
# ------------------------------
# Run the Program
# ------------------------------
if __name__ == "__main__":
    main_menu()
