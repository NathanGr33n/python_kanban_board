# kanban.py
# NathanGr33n
# August 2025
# A simple terminal-based Kanban board with three columns: To Do, In Progress, Done

import json
import os
import uuid
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
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

#region HelperFunctions
# ------------------------------
# Helper Functions
# ------------------------------

#region SafetyUtils
# ------------------------------
# Safety Utilities
# ------------------------------

def display_error(message: str, exception: Optional[Exception] = None) -> None:
    """Display user-friendly error messages with optional debug info."""
    console.print(f"[bold red]❌ {message}[/]")
    if exception:
        console.print(f"[dim red]Debug: {type(exception).__name__}: {str(exception)}[/]")

def validate_title(title: str) -> Tuple[bool, str]:
    """Validate task title input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Task title cannot be empty"
    
    title = title.strip()
    if len(title) > 100:
        return False, "Task title must be 100 characters or less"
    
    if len(title) < 1:
        return False, "Task title must be at least 1 character"
    
    # Check for control characters (except newlines which we'll strip)
    if any(ord(char) < 32 and char not in '\n\r\t' for char in title):
        return False, "Task title contains invalid characters"
    
    return True, ""

def validate_task_id(task_id: str) -> Tuple[bool, str]:
    """Validate task ID input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not task_id or not task_id.strip():
        return False, "Task ID cannot be empty"
    
    task_id = task_id.strip()
    if len(task_id) < 4:
        return False, "Task ID must be at least 4 characters"
    
    # Check if it's alphanumeric with hyphens (UUID format)
    if not all(char.isalnum() or char == '-' for char in task_id):
        return False, "Task ID must contain only letters, numbers, and hyphens"
    
    return True, ""

def validate_menu_choice(choice: str) -> Tuple[bool, str]:
    """Validate menu choice input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not choice or not choice.strip():
        return False, "Please enter a choice"
    
    choice = choice.strip()
    if choice not in ['1', '2', '3', '4', '5']:
        return False, "Please enter a number between 1 and 5"
    
    return True, ""

def validate_json_structure(data: Any) -> Tuple[bool, str]:
    """Validate that loaded JSON has the correct kanban board structure.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    required_columns = ["To Do", "In Progress", "Done"]
    for column in required_columns:
        if column not in data:
            return False, f"Missing required column: {column}"
        
        if not isinstance(data[column], list):
            return False, f"Column '{column}' must be a list"
        
        # Validate each task in the column
        for i, task in enumerate(data[column]):
            if not isinstance(task, dict):
                return False, f"Task {i+1} in '{column}' must be a dictionary"
            
            if "id" not in task or "title" not in task:
                return False, f"Task {i+1} in '{column}' missing required fields (id, title)"
            
            if not isinstance(task["id"], str) or not isinstance(task["title"], str):
                return False, f"Task {i+1} in '{column}' has invalid field types"
    
    return True, ""

def find_unique_task_id() -> str:
    """Generate a unique task ID ensuring no collision with existing 4-char prefixes."""
    max_attempts = 100  # Prevent infinite loop
    for _ in range(max_attempts):
        new_id = str(uuid.uuid4())
        short_id = new_id[:4]
        
        # Check if this 4-char prefix already exists
        collision = False
        for col in board.values():
            for task in col:
                if task["id"][:4].lower() == short_id.lower():
                    collision = True
                    break
            if collision:
                break
        
        if not collision:
            return new_id
    
    # Fallback: return a UUID even if there might be a collision
    console.print("[yellow]⚠️ Warning: Could not generate unique 4-char ID prefix[/]")
    return str(uuid.uuid4())

def find_matching_tasks(task_id_fragment: str) -> List[Tuple[str, Dict[str, str]]]:
    """Find all tasks that match the given ID fragment.
    
    Returns:
        List of (column_name, task) tuples
    """
    matches = []
    fragment_lower = task_id_fragment.lower()
    
    for col_name, tasks in board.items():
        for task in tasks:
            if task["id"][:len(fragment_lower)].lower() == fragment_lower:
                matches.append((col_name, task))
    
    return matches

#endregion

#region Load&Save
def load_board() -> bool:
    """Load the saved board from a JSON file with error handling and corruption recovery.
    
    Returns:
        bool: True if loaded successfully, False if had to recover from corruption
    """
    global board
    
    if not os.path.exists(DATA_FILE):
        console.print("[yellow]📄 No existing data file found. Creating new board...[/]")
        save_board()
        return True
    
    try:
        # Attempt to read and parse the JSON file
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validate the JSON structure
        is_valid, error_msg = validate_json_structure(data)
        if not is_valid:
            raise ValueError(f"Invalid board structure: {error_msg}")
        
        # Load the data into the board
        for column in board:
            board[column] = data.get(column, [])
        
        console.print("[green]✅ Board loaded successfully[/]")
        return True
        
    except FileNotFoundError:
        display_error("Data file was deleted while running")
        save_board()
        return True
        
    except PermissionError as e:
        display_error(f"Permission denied accessing {DATA_FILE}", e)
        console.print("[yellow]📋 Starting with empty board (changes won't be saved)[/]")
        return False
        
    except json.JSONDecodeError as e:
        display_error(f"Data file is corrupted (invalid JSON)", e)
        return _handle_corrupted_file()
        
    except (ValueError, KeyError, TypeError) as e:
        display_error(f"Data file has invalid structure", e)
        return _handle_corrupted_file()
        
    except OSError as e:
        display_error(f"System error reading {DATA_FILE}", e)
        console.print("[yellow]📋 Starting with empty board[/]")
        return False

def _handle_corrupted_file() -> bool:
    """Handle corrupted data file by backing it up and starting fresh.
    
    Returns:
        bool: True if recovery successful, False if backup failed
    """
    try:
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{DATA_FILE}.bak_corrupt_{timestamp}"
        
        # Move corrupted file to backup
        shutil.move(DATA_FILE, backup_file)
        
        console.print(f"[yellow]💾 Corrupted file backed up as: {backup_file}[/]")
        console.print("[green]🔄 Starting with fresh board...[/]")
        
        # Reset board to initial state and save
        global board
        board = {"To Do": [], "In Progress": [], "Done": []}
        save_board()
        
        return True
        
    except OSError as e:
        display_error(f"Could not backup corrupted file", e)
        console.print("[yellow]📋 Continuing with empty board (original file unchanged)[/]")
        return False

def save_board() -> bool:
    """Save the current board state to a JSON file with atomic writes and error handling.
    
    Returns:
        bool: True if saved successfully, False if save failed
    """
    max_retries = 3
    retry_delay = 0.1  # Start with 100ms delay
    
    for attempt in range(max_retries):
        try:
            # Use atomic write: write to temp file, then replace original
            temp_dir = os.path.dirname(os.path.abspath(DATA_FILE))
            
            with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, 
                                             suffix='.tmp', delete=False, 
                                             encoding='utf-8') as temp_file:
                json.dump(board, temp_file, indent=2, ensure_ascii=False)
                temp_file_path = temp_file.name
            
            # Atomic replace operation
            if os.name == 'nt':  # Windows
                # On Windows, we need to remove the target first
                if os.path.exists(DATA_FILE):
                    os.replace(temp_file_path, DATA_FILE)
                else:
                    os.rename(temp_file_path, DATA_FILE)
            else:  # Unix-like systems
                os.replace(temp_file_path, DATA_FILE)
            
            if attempt > 0:
                console.print(f"[green]✅ Board saved successfully (attempt {attempt + 1})[/]")
            
            return True
            
        except PermissionError as e:
            if attempt < max_retries - 1:
                console.print(f"[yellow]⚠️ Save failed, retrying in {retry_delay:.1f}s... (attempt {attempt + 1}/{max_retries})[/]")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                display_error(f"Permission denied saving to {DATA_FILE}", e)
                console.print("[red]💾 Your changes are NOT saved! Please check file permissions.[/]")
        
        except OSError as e:
            if "No space left on device" in str(e) or "disk full" in str(e).lower():
                display_error("Cannot save: disk is full", e)
                break  # No point retrying if disk is full
            elif attempt < max_retries - 1:
                console.print(f"[yellow]⚠️ Save failed, retrying in {retry_delay:.1f}s... (attempt {attempt + 1}/{max_retries})[/]")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                display_error(f"System error saving {DATA_FILE}", e)
        
        except Exception as e:
            display_error(f"Unexpected error saving {DATA_FILE}", e)
            break  # Don't retry on unexpected errors
        
        finally:
            # Clean up temp file if it still exists
            try:
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors
    
    return False
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
    """Add a new task to the 'To Do' column with robust input validation."""
    max_attempts = 5
    
    for attempt in range(max_attempts):
        title = Prompt.ask("[bold green]Enter task title[/]")
        
        is_valid, error_msg = validate_title(title)
        if is_valid:
            task = {
                "id": find_unique_task_id(),
                "title": title.strip()
            }
            board["To Do"].append(task)
            
            if save_board():
                console.print("[green]✅ Task added to To Do![/]")
            else:
                console.print("[yellow]⚠️ Task added to board but could not save to file[/]")
            return
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
    
    console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")

def move_task():
    """Move a task from one column to another with input validation."""
    display_board()
    
    # Check if there are any tasks to move
    total_tasks = sum(len(tasks) for tasks in board.values())
    if total_tasks == 0:
        console.print("[yellow]📋 No tasks available to move.[/]")
        return
    
    max_attempts = 5
    
    for attempt in range(max_attempts):
        task_id = Prompt.ask("[bold blue]Enter the task ID to move (first 4 chars)[/]")
        
        # Validate task ID format
        is_valid, error_msg = validate_task_id(task_id)
        if not is_valid:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        
        # Find matching tasks
        matches = find_matching_tasks(task_id.strip())
        
        if len(matches) == 0:
            console.print("[red]❌ Task not found.[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        elif len(matches) > 1:
            console.print("[yellow]⚠️ Multiple tasks match that ID:[/]")
            for col_name, task in matches:
                console.print(f"  [cyan]{task['id'][:8]}[/] - {task['title']} (in {col_name})")
            console.print("[yellow]Please enter more characters to uniquely identify the task.[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        
        # Exactly one match found
        from_col, task = matches[0]
        
        # Ask for destination column
        available_cols = [col for col in board.keys() if col != from_col]
        if not available_cols:
            console.print("[yellow]⚠️ Task is already in the only available column.[/]")
            return
        
        to_col = Prompt.ask(f"Move '{task['title']}' from {from_col} to which column?", 
                           choices=list(board.keys()))
        
        if to_col == from_col:
            console.print("[yellow]⚠️ Task is already in that column.[/]")
            return
        
        # Perform the move
        board[from_col].remove(task)
        board[to_col].append(task)
        
        if save_board():
            console.print(f"[green]✅ Moved '{task['title']}' to {to_col}.[/]")
        else:
            console.print(f"[yellow]⚠️ Task moved in memory but could not save to file[/]")
        return
    
    console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")

def delete_task():
    """Delete a task from the board with input validation and confirmation."""
    display_board()
    
    # Check if there are any tasks to delete
    total_tasks = sum(len(tasks) for tasks in board.values())
    if total_tasks == 0:
        console.print("[yellow]📋 No tasks available to delete.[/]")
        return
    
    max_attempts = 5
    
    for attempt in range(max_attempts):
        task_id = Prompt.ask("[bold red]Enter the task ID to delete (first 4 chars)[/]")
        
        # Validate task ID format
        is_valid, error_msg = validate_task_id(task_id)
        if not is_valid:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        
        # Find matching tasks
        matches = find_matching_tasks(task_id.strip())
        
        if len(matches) == 0:
            console.print("[red]❌ Task not found.[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        elif len(matches) > 1:
            console.print("[yellow]⚠️ Multiple tasks match that ID:[/]")
            for col_name, task in matches:
                console.print(f"  [cyan]{task['id'][:8]}[/] - {task['title']} (in {col_name})")
            console.print("[yellow]Please enter more characters to uniquely identify the task.[/]")
            if attempt < max_attempts - 1:
                console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
            continue
        
        # Exactly one match found
        col_name, task = matches[0]
        
        # Confirm deletion
        confirmation = Prompt.ask(
            f"[bold red]Are you sure you want to delete '[/][yellow]{task['title']}[/][bold red]'? (y/N)[/]",
            default="N"
        )
        
        if confirmation.lower() in ['y', 'yes']:
            board[col_name].remove(task)
            
            if save_board():
                console.print(f"[bold red]🗑️ Task '{task['title']}' deleted.[/]")
            else:
                console.print(f"[yellow]⚠️ Task deleted from board but could not save to file[/]")
        else:
            console.print("[green]✅ Deletion cancelled.[/]")
        
        return
    
    console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")

#endregion

#region Main Menu
# ------------------------------
# Main Menu
# ------------------------------

def main_menu():
    """Main menu with robust input validation and error handling."""
    if not load_board():
        console.print("[yellow]⚠️ Warning: Running in read-only mode (file operations may fail)[/]")
    
    while True:
        try:
            console.print(Panel.fit(
                "[bold cyan]1.[/] View Board\n"
                "[bold cyan]2.[/] Add Task\n"
                "[bold cyan]3.[/] Move Task\n"
                "[bold cyan]4.[/] Delete Task\n"
                "[bold cyan]5.[/] Exit",
                title="[bold magenta]KANBAN MENU",
                subtitle="Choose an option"
            ))

            max_attempts = 3
            choice = None
            
            for attempt in range(max_attempts):
                try:
                    raw_choice = Prompt.ask("[bold]Enter choice (1-5)[/]")
                    is_valid, error_msg = validate_menu_choice(raw_choice)
                    
                    if is_valid:
                        choice = raw_choice.strip()
                        break
                    else:
                        console.print(f"[red]⚠️ {error_msg}[/]")
                        if attempt < max_attempts - 1:
                            console.print(f"[dim]Please try again ({attempt + 1}/{max_attempts} attempts used)[/]")
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]👋 Goodbye![/]")
                    return
                except EOFError:
                    console.print("\n[yellow]👋 Input stream ended. Goodbye![/]")
                    return
            
            if not choice:
                console.print("[red]❌ Too many invalid attempts. Exiting...[/]")
                break
            
            # Execute menu choice
            if choice == '1':
                display_board()
                input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '2':
                add_task()
            elif choice == '3':
                move_task()
            elif choice == '4':
                delete_task()
            elif choice == '5':
                console.print("[bold yellow]👋 Exiting Kanban Board. Goodbye![/]")
                break
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/]")
            break
        except Exception as e:
            display_error("Unexpected error in main menu", e)
            console.print("[yellow]Continuing...[/]")

#endregion

#endregion
# ------------------------------
# Run the Program
# ------------------------------
if __name__ == "__main__":
    main_menu()
