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
# File where data is stored
DATA_FILE = 'kanban_data.json'

# Multiple boards data structure
# {
#   "format_version": "2.0",
#   "current_board": "board_id",
#   "boards": {
#     "board_id": {
#       "name": "Board Name",
#       "created_at": "ISO-datetime",
#       "last_modified": "ISO-datetime",
#       "columns": {
#         "To Do": [],
#         "In Progress": [],
#         "Done": []
#       }
#     }
#   }
# }
boards_data = {
    "format_version": "2.0",
    "current_board": None,
    "boards": {}
}

# Legacy single board structure for backwards compatibility
board = {
    "To Do": [],
    "In Progress": [],
    "Done": []
}

# Keyboard shortcuts mapping
KEYBOARD_SHORTCUTS = {
    '1': {'action': '1', 'desc': 'View Board', 'key': 'v'},
    '2': {'action': '2', 'desc': 'Add Task', 'key': 'a'},
    '3': {'action': '3', 'desc': 'Edit Task', 'key': 'e'},
    '4': {'action': '4', 'desc': 'Move Task', 'key': 'm'},
    '5': {'action': '5', 'desc': 'Delete Task', 'key': 'd'},
    '6': {'action': '6', 'desc': 'Search & Filter', 'key': 's'},
    '7': {'action': '7', 'desc': 'View Statistics', 'key': 'r'},  # 'r' for reports
    '8': {'action': '8', 'desc': 'Board Management', 'key': 'b'},
    '9': {'action': '9', 'desc': 'Exit', 'key': 'q'},
    'help': {'action': 'help', 'desc': 'Show Help', 'key': 'h'}
}

# Reverse lookup for shortcuts to actions
SHORTCUT_TO_ACTION = {}
for action, info in KEYBOARD_SHORTCUTS.items():
    SHORTCUT_TO_ACTION[info['key']] = action
SHORTCUT_TO_ACTION['?'] = 'help'  # Alternative help key
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
    """Validate menu choice input - accepts both numbers and keyboard shortcuts.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not choice or not choice.strip():
        return False, "Please enter a choice"
    
    choice = choice.strip().lower()
    
    # Check if it's a valid number choice
    if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return True, ""
    
    # Check if it's a valid keyboard shortcut
    if choice in SHORTCUT_TO_ACTION:
        return True, ""
    
    # Show helpful error message with available options
    shortcuts_desc = ", ".join([f"'{info['key']}' ({info['desc']})" for info in KEYBOARD_SHORTCUTS.values()])
    return False, f"Please enter 1-9 or use shortcuts: {shortcuts_desc}"

def validate_priority(priority: str) -> Tuple[bool, str]:
    """Validate task priority input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not priority or not priority.strip():
        return False, "Priority cannot be empty"
    
    priority = priority.strip().lower()
    if priority not in ['high', 'medium', 'low']:
        return False, "Priority must be 'high', 'medium', or 'low'"
    
    return True, ""

def validate_due_date(due_date_str: str) -> Tuple[bool, str]:
    """Validate due date input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not due_date_str or not due_date_str.strip():
        return True, ""  # Due date is optional
    
    try:
        # Try to parse as ISO date format
        datetime.fromisoformat(due_date_str.strip())
        return True, ""
    except ValueError:
        return False, "Due date must be in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"

def validate_tags(tags_str: str) -> Tuple[bool, str]:
    """Validate tags input (comma-separated).
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tags_str or not tags_str.strip():
        return True, ""  # Tags are optional
    
    tags = [tag.strip() for tag in tags_str.split(',')]
    for tag in tags:
        if not tag:
            return False, "Tags cannot be empty (remove extra commas)"
        if len(tag) > 20:
            return False, "Each tag must be 20 characters or less"
        if not tag.replace('_', '').replace('-', '').isalnum():
            return False, "Tags can only contain letters, numbers, hyphens, and underscores"
    
    return True, ""

def validate_board_name(board_name: str) -> Tuple[bool, str]:
    """Validate board name input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not board_name or not board_name.strip():
        return False, "Board name cannot be empty"
    
    board_name = board_name.strip()
    if len(board_name) > 50:
        return False, "Board name must be 50 characters or less"
    
    if len(board_name) < 1:
        return False, "Board name must be at least 1 character"
    
    # Check for control characters and invalid filename characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in board_name for char in invalid_chars):
        return False, "Board name contains invalid characters (< > : \" / \\ | ? *)"
    
    if any(ord(char) < 32 for char in board_name):
        return False, "Board name contains invalid control characters"
    
    return True, ""

def validate_json_structure(data: Any) -> Tuple[bool, str]:
    """Validate that loaded JSON has the correct kanban board structure.
    
    Supports both old (id, title) and new (enhanced) task formats.

    Returns:
        Tuple of (is_valid, error_message)
    """
    
    def validate_subtasks(subtasks: Any) -> Tuple[bool, str]:
        if not isinstance(subtasks, list):
            return False, "Subtasks must be a list"
        
        # Prevent excessive nesting (only allow 1 level of subtasks)
        for i, stask in enumerate(subtasks):
            if not isinstance(stask, dict):
                return False, f"Subtask {i+1} must be a dictionary"
            
            # Required fields for subtask
            if "id" not in stask or "title" not in stask or "completed" not in stask:
                return False, f"Subtask {i+1} missing required fields (id, title, completed)"
            
            if not isinstance(stask["id"], str) or not isinstance(stask["title"], str) or not isinstance(stask["completed"], bool):
                return False, f"Subtask {i+1} has invalid field types"
            
            # No nested subtasks beyond first level
            if "subtasks" in stask and stask["subtasks"]:
                return False, f"Subtask {i+1} should not have nested subtasks"
        return True, ""

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
            
            # Required fields for all task formats
            if "id" not in task or "title" not in task:
                return False, f"Task {i+1} in '{column}' missing required fields (id, title)"
            
            if not isinstance(task["id"], str) or not isinstance(task["title"], str):
                return False, f"Task {i+1} in '{column}' has invalid field types"
            
            # Optional fields validation (for enhanced format)
            if "priority" in task and not isinstance(task["priority"], str):
                return False, f"Task {i+1} in '{column}' priority must be a string"
            
            if "priority" in task and task["priority"] not in ['high', 'medium', 'low']:
                return False, f"Task {i+1} in '{column}' has invalid priority"
            
            if "description" in task and not isinstance(task["description"], str):
                return False, f"Task {i+1} in '{column}' description must be a string"
            
            if "created_at" in task and not isinstance(task["created_at"], str):
                return False, f"Task {i+1} in '{column}' created_at must be a string"
            
            if "due_date" in task and task["due_date"] is not None and not isinstance(task["due_date"], str):
                return False, f"Task {i+1} in '{column}' due_date must be a string or null"
            
            if "tags" in task and not isinstance(task["tags"], list):
                return False, f"Task {i+1} in '{column}' tags must be a list"
            
            # Validate subtasks if present
            if "subtasks" in task:
                is_valid, error_msg = validate_subtasks(task["subtasks"])
                if not is_valid:
                    return False, f"Task {i+1} in '{column}' subtasks error: {error_msg}"
    
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

def get_priority_symbol(priority: str) -> str:
    """Get emoji symbol for priority level."""
    priority_map = {
        'high': '🔴',
        'medium': '🟡', 
        'low': '🟢'
    }
    return priority_map.get(priority.lower(), '⚪')

def get_priority_color(priority: str) -> str:
    """Get Rich color for priority level."""
    priority_colors = {
        'high': 'red',
        'medium': 'yellow',
        'low': 'green'
    }
    return priority_colors.get(priority.lower(), 'white')

def format_due_date(due_date_str: Optional[str]) -> str:
    """Format due date with urgency indicators."""
    if not due_date_str:
        return ""
    
    try:
        due_date = datetime.fromisoformat(due_date_str)
        now = datetime.now()
        days_diff = (due_date - now).days
        
        if days_diff < 0:
            return f"⏰ [red]Overdue ({abs(days_diff)}d)[/]"
        elif days_diff == 0:
            return f"⏳ [yellow]Due today[/]"
        elif days_diff <= 3:
            return f"⏳ [yellow]Due in {days_diff}d[/]"
        else:
            return f"📅 [dim]Due {due_date.strftime('%m/%d')}[/]"
    except ValueError:
        return f"⚠️ [dim]Invalid date[/]"

def migrate_old_tasks() -> int:
    """Migrate tasks from old format to new enhanced format.
    
    Returns:
        int: Number of tasks migrated
    """
    migrated_count = 0
    now_iso = datetime.now().isoformat()
    
    for column_name, tasks in board.items():
        for task in tasks:
            # Check if task needs migration (missing enhanced fields)
            needs_migration = False
            
            if "priority" not in task:
                task["priority"] = "medium"
                needs_migration = True
            
            if "description" not in task:
                task["description"] = ""
                needs_migration = True
            
            if "created_at" not in task:
                task["created_at"] = now_iso
                needs_migration = True
            
            if "due_date" not in task:
                task["due_date"] = None
                needs_migration = True
            
            if "tags" not in task:
                task["tags"] = []
                needs_migration = True
            
            if needs_migration:
                migrated_count += 1
    
    return migrated_count

def create_enhanced_task(title: str, description: str = "", priority: str = "medium", 
                        due_date: Optional[str] = None, tags: List[str] = None) -> Dict[str, Any]:
    """Create a new task with enhanced fields.
    
    Returns:
        Dict containing the new task
    """
    if tags is None:
        tags = []
    
    return {
        "id": find_unique_task_id(),
        "title": title.strip(),
        "description": description.strip(),
        "priority": priority.lower(),
        "created_at": datetime.now().isoformat(),
        "due_date": due_date,
        "tags": tags,
        "subtasks": []
    }

def validate_subtask_title(title: str) -> Tuple[bool, str]:
    """Validate subtask title input.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Subtask title cannot be empty"
    
    title = title.strip()
    if len(title) > 80:  # Slightly shorter than main tasks
        return False, "Subtask title must be 80 characters or less"
    
    if len(title) < 1:
        return False, "Subtask title must be at least 1 character"
    
    # Check for control characters (except newlines which we'll strip)
    if any(ord(char) < 32 and char not in '\n\r\t' for char in title):
        return False, "Subtask title contains invalid characters"
    
    return True, ""

def create_subtask(title: str) -> Dict[str, Any]:
    """Create a new subtask with basic fields.
    
    Returns:
        Dict containing the new subtask
    """
    return {
        "id": str(uuid.uuid4())[:8],  # Shorter ID for subtasks
        "title": title.strip(),
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

def calculate_subtask_progress(task: Dict[str, Any]) -> Tuple[int, int, float]:
    """Calculate subtask completion progress.
    
    Returns:
        Tuple of (completed_count, total_count, percentage)
    """
    subtasks = task.get("subtasks", [])
    if not subtasks:
        return 0, 0, 0.0
    
    total_count = len(subtasks)
    completed_count = sum(1 for subtask in subtasks if subtask.get("completed", False))
    percentage = (completed_count / total_count) * 100 if total_count > 0 else 0.0
    
    return completed_count, total_count, percentage

def find_subtask_by_id(task: Dict[str, Any], subtask_id: str) -> Optional[Dict[str, Any]]:
    """Find a subtask by its ID within a task.
    
    Returns:
        Subtask dict if found, None otherwise
    """
    subtasks = task.get("subtasks", [])
    for subtask in subtasks:
        if subtask["id"].lower().startswith(subtask_id.lower()):
            return subtask
    return None

def get_subtask_matches(task: Dict[str, Any], subtask_id_fragment: str) -> List[Dict[str, Any]]:
    """Get all subtasks that match the given ID fragment.
    
    Returns:
        List of matching subtasks
    """
    subtasks = task.get("subtasks", [])
    fragment_lower = subtask_id_fragment.lower()
    matches = []
    
    for subtask in subtasks:
        if subtask["id"].lower().startswith(fragment_lower):
            matches.append(subtask)
    
    return matches

#endregion

#region Load&Save
def load_board() -> bool:
    """Load the saved board from a JSON file with error handling and corruption recovery.
    Supports both single-board (legacy) and multiple-board formats with automatic migration.
    
    Returns:
        bool: True if loaded successfully, False if had to recover from corruption
    """
    global board, boards_data
    
    if not os.path.exists(DATA_FILE):
        console.print("[yellow]📄 No existing data file found. Creating new board...[/]")
        save_board()
        return True
    
    try:
        # Attempt to read and parse the JSON file
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Detect data format and handle accordingly
        if _is_multiple_boards_format(data):
            return _load_multiple_boards_format(data)
        else:
            return _load_single_board_format(data)
        
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

def _is_multiple_boards_format(data: Any) -> bool:
    """Check if the loaded data is in multiple boards format.
    
    Returns:
        bool: True if data is multiple boards format, False if legacy single board
    """
    # Multiple boards format has format_version and boards keys
    if isinstance(data, dict):
        has_format_version = 'format_version' in data
        has_boards = 'boards' in data
        
        # Check if it looks like multiple boards format
        if has_format_version or has_boards:
            return True
        
        # Check if it looks like legacy single board (has To Do, In Progress, Done)
        legacy_columns = ['To Do', 'In Progress', 'Done']
        if all(col in data for col in legacy_columns):
            return False
    
    return False

def _load_multiple_boards_format(data: Dict[str, Any]) -> bool:
    """Load data in multiple boards format.
    
    Returns:
        bool: True if loaded successfully, False otherwise
    """
    global board, boards_data
    
    try:
        # Validate multiple boards structure
        if not isinstance(data, dict):
            raise ValueError("Multiple boards data must be a dictionary")
        
        if 'boards' not in data:
            raise ValueError("Multiple boards data missing 'boards' key")
        
        # Load the boards data
        boards_data.update(data)
        
        # Set current board or default to first available
        current_board_id = boards_data.get('current_board')
        available_boards = boards_data.get('boards', {})
        
        if not available_boards:
            console.print("[yellow]No boards found in file. Creating default board...[/]")
            _create_default_board()
        elif current_board_id and current_board_id in available_boards:
            # Load the current board
            board = available_boards[current_board_id]['columns'].copy()
            board_name = available_boards[current_board_id]['name']
            console.print(f"[green]✅ Loaded multiple boards format - Active: '{board_name}'[/]")
        else:
            # No current board set or invalid, use first available
            first_board_id = next(iter(available_boards.keys()))
            boards_data['current_board'] = first_board_id
            board = available_boards[first_board_id]['columns'].copy()
            board_name = available_boards[first_board_id]['name']
            console.print(f"[green]✅ Loaded multiple boards format - Defaulted to: '{board_name}'[/]")
            # Save the updated current board selection
            save_boards_data()
        
        return True
        
    except Exception as e:
        display_error("Failed to load multiple boards format", e)
        return _handle_corrupted_file()

def _load_single_board_format(data: Dict[str, Any]) -> bool:
    """Load data in legacy single board format and migrate to multiple boards.
    
    Returns:
        bool: True if loaded successfully, False otherwise
    """
    global board, boards_data
    
    try:
        # Validate single board structure
        is_valid, error_msg = validate_json_structure(data)
        if not is_valid:
            raise ValueError(f"Invalid single board structure: {error_msg}")
        
        # Load the legacy board data
        for column in board:
            board[column] = data.get(column, [])
        
        # Ask user if they want to migrate to multiple boards
        console.print("[yellow]📄 Detected single-board format (legacy)[/]")
        console.print("[dim]Would you like to upgrade to multiple boards format?[/]")
        console.print("[dim]This allows you to create and manage multiple project boards.[/]")
        
        migrate = Prompt.ask(
            "[bold cyan]Upgrade to multiple boards? (Y/n)[/]",
            default="Y"
        )
        
        if migrate.lower() in ['y', 'yes', '']:
            # Create multiple boards format with current board as "Main Board"
            board_id = str(uuid.uuid4())
            now_iso = datetime.now().isoformat()
            
            # Migrate current board to multiple boards format
            boards_data['format_version'] = '2.0'
            boards_data['current_board'] = board_id
            boards_data['boards'] = {
                board_id: {
                    'name': 'Main Board',
                    'created_at': now_iso,
                    'last_modified': now_iso,
                    'columns': board.copy()
                }
            }
            
            # Save in new format
            if save_boards_data():
                console.print("[green]✅ Successfully upgraded to multiple boards format![/]")
                console.print("[dim]Your existing tasks are now in 'Main Board'[/]")
                console.print("[dim]You can create additional boards from the main menu[/]")
            else:
                console.print("[yellow]⚠️ Upgraded in memory but could not save new format[/]")
        else:
            console.print("[yellow]Continuing with single-board mode[/]")
        
        console.print("[green]✅ Board loaded successfully[/]")
        return True
        
    except Exception as e:
        display_error("Failed to load single board format", e)
        return _handle_corrupted_file()

def _create_default_board() -> None:
    """Create a default board when none exist."""
    global board, boards_data
    
    board_id = str(uuid.uuid4())
    now_iso = datetime.now().isoformat()
    
    # Create default board
    boards_data['format_version'] = '2.0'
    boards_data['current_board'] = board_id
    boards_data['boards'] = {
        board_id: {
            'name': 'My First Board',
            'created_at': now_iso,
            'last_modified': now_iso,
            'columns': {
                'To Do': [],
                'In Progress': [],
                'Done': []
            }
        }
    }
    
    board = boards_data['boards'][board_id]['columns'].copy()
    console.print("[green]✅ Created default board 'My First Board'[/]")

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
    """Display the Kanban board in the terminal with enhanced task information."""
    console.clear()
    console.rule("[bold red]📋 KANBAN BOARD[/]")
    
    # Auto-migrate any old tasks
    migrated = migrate_old_tasks()
    if migrated > 0:
        console.print(f"[dim green]✨ Migrated {migrated} task(s) to enhanced format[/]")
        save_board()
    
    max_tasks = max(len(board[col]) for col in board) if any(board.values()) else 0
    columns = list(board.keys())

    # Create a table with enhanced task display
    table = Table(show_header=True, header_style="bold cyan", box=box.DOUBLE_EDGE)
    for col in columns:
        table.add_column(col, style="bold", min_width=25)

    if max_tasks == 0:
        # Show empty board message
        table.add_row(*["[dim]No tasks[/]" for _ in columns])
    else:
        for i in range(max_tasks):
            row = []
            for col in columns:
                try:
                    task = board[col][i]
                    cell_content = _format_task_cell(task)
                    row.append(cell_content)
                except IndexError:
                    row.append("")
            table.add_row(*row)

    console.print(table)
    
    # Show quick stats
    total_tasks = sum(len(tasks) for tasks in board.values())
    if total_tasks > 0:
        overdue_count = sum(1 for tasks in board.values() for task in tasks 
                           if _is_overdue(task.get('due_date')))
        if overdue_count > 0:
            console.print(f"\n[bold red]⚠️ {overdue_count} overdue task(s)[/]")
        console.print(f"[dim]Total tasks: {total_tasks}[/]")

def _format_task_cell(task: Dict[str, Any]) -> str:
    """Format a single task for display in the board table."""
    short_id = task["id"][:4]
    title = task["title"]
    
    # Priority indicator
    priority = task.get("priority", "medium")
    priority_symbol = get_priority_symbol(priority)
    priority_color = get_priority_color(priority)
    
    # Build main task line
    task_line = f"{priority_symbol} [{priority_color}]{title}[/] [dim]({short_id})[/]"
    
    # Add due date if present
    due_date = task.get("due_date")
    if due_date:
        due_display = format_due_date(due_date)
        task_line += f"\n{due_display}"
    
    # Add tags if present
    tags = task.get("tags", [])
    if tags:
        tags_display = " ".join(f"[magenta]#{tag}[/]" for tag in tags[:3])  # Limit to first 3 tags
        if len(tags) > 3:
            tags_display += f" [dim]+{len(tags)-3}[/]"
        task_line += f"\n{tags_display}"
    
    # Add description preview if present
    description = task.get("description", "")
    if description:
        preview = description[:40] + "..." if len(description) > 40 else description
        task_line += f"\n[dim italic]{preview}[/]"
    
    return task_line

def _is_overdue(due_date_str: Optional[str]) -> bool:
    """Check if a task is overdue."""
    if not due_date_str:
        return False
    try:
        due_date = datetime.fromisoformat(due_date_str)
        return datetime.now() > due_date
    except ValueError:
        return False
#endregion

#region Task Operations
# ------------------------------
# Task Operations
# ------------------------------

def add_task():
    """Add a new enhanced task to the 'To Do' column with comprehensive input collection."""
    console.print("\n[bold green]✨ Create New Task[/]")
    console.print("[dim]Fill in the details below. Fields marked with * are required.[/dim]\n")
    
    # Title (required)
    title = None
    for attempt in range(5):
        title_input = Prompt.ask("[bold green]*[/] Task title")
        is_valid, error_msg = validate_title(title_input)
        if is_valid:
            title = title_input.strip()
            break
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < 4:
                console.print(f"[dim]Please try again ({attempt + 1}/5 attempts used)[/]")
    
    if not title:
        console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")
        return
    
    # Description (optional)
    description = Prompt.ask("[cyan]Description[/] (optional)", default="")
    
    # Priority (optional, default medium)
    priority = None
    for attempt in range(3):
        priority_input = Prompt.ask(
            "[yellow]Priority[/] ([red]high[/]/[yellow]medium[/]/[green]low[/])", 
            default="medium"
        )
        is_valid, error_msg = validate_priority(priority_input)
        if is_valid:
            priority = priority_input.strip().lower()
            break
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
    
    if not priority:
        priority = "medium"  # Fallback to default
    
    # Due date (optional)
    due_date = None
    due_date_input = Prompt.ask(
        "[blue]Due date[/] (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS, optional)", 
        default=""
    )
    
    if due_date_input.strip():
        is_valid, error_msg = validate_due_date(due_date_input)
        if is_valid:
            due_date = due_date_input.strip()
        else:
            console.print(f"[red]⚠️ {error_msg}. Skipping due date.[/]")
    
    # Tags (optional)
    tags = []
    tags_input = Prompt.ask(
        "[magenta]Tags[/] (comma-separated, optional)", 
        default=""
    )
    
    if tags_input.strip():
        is_valid, error_msg = validate_tags(tags_input)
        if is_valid:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        else:
            console.print(f"[red]⚠️ {error_msg}. Skipping tags.[/]")
    
    # Create the enhanced task
    task = create_enhanced_task(title, description, priority, due_date, tags)
    
    # Show preview
    console.print("\n[bold cyan]📋 Task Preview:[/]")
    priority_symbol = get_priority_symbol(priority)
    console.print(f"  Title: [yellow]{task['title']}[/]")
    console.print(f"  Priority: {priority_symbol} [bold]{priority.title()}[/]")
    if description:
        console.print(f"  Description: [dim]{description}[/]")
    if due_date:
        due_display = format_due_date(due_date)
        console.print(f"  Due: {due_display}")
    if tags:
        tags_display = ", ".join(f"[magenta]#{tag}[/]" for tag in tags)
        console.print(f"  Tags: {tags_display}")
    
    # Confirm creation
    confirm = Prompt.ask("\n[bold]Add this task? (Y/n)[/]", default="Y")
    
    if confirm.lower() in ['y', 'yes', '']:
        board["To Do"].append(task)
        
        if save_board():
            console.print(f"\n[green]✅ Task '{task['title']}' added to To Do![/]")
        else:
            console.print(f"\n[yellow]⚠️ Task added to board but could not save to file[/]")
    else:
        console.print("\n[yellow]❌ Task creation cancelled.[/]")

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

def edit_task():
    """Edit an existing task with comprehensive field editing."""
    display_board()
    
    # Check if there are any tasks to edit
    total_tasks = sum(len(tasks) for tasks in board.values())
    if total_tasks == 0:
        console.print("[yellow]📋 No tasks available to edit.[/]")
        return
    
    # Find task to edit
    max_attempts = 5
    task = None
    col_name = None
    
    for attempt in range(max_attempts):
        task_id = Prompt.ask("[bold blue]Enter the task ID to edit (first 4 chars)[/]")
        
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
        break
    
    if not task:
        console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")
        return
    
    # Show current task details
    console.print(f"\n[bold cyan]📝 Editing Task: {task['title']}[/]")
    _display_task_details(task)
    
    # Edit menu loop
    while True:
        console.print(Panel.fit(
            "[bold cyan]1.[/] Edit Title\n"
            "[bold cyan]2.[/] Edit Description\n"
            "[bold cyan]3.[/] Edit Priority\n"
            "[bold cyan]4.[/] Edit Due Date\n"
            "[bold cyan]5.[/] Edit Tags\n"
            "[bold cyan]6.[/] Move to Different Column\n"
            "[bold cyan]7.[/] Finish Editing",
            title="[bold magenta]EDIT TASK",
            subtitle="Choose what to edit"
        ))
        
        edit_choice = Prompt.ask("[bold]Enter choice (1-7)[/]")
        
        if edit_choice == '1':
            _edit_task_title(task)
        elif edit_choice == '2':
            _edit_task_description(task)
        elif edit_choice == '3':
            _edit_task_priority(task)
        elif edit_choice == '4':
            _edit_task_due_date(task)
        elif edit_choice == '5':
            _edit_task_tags(task)
        elif edit_choice == '6':
            _edit_task_column(task, col_name)
            break  # Moving changes the context, so exit edit mode
        elif edit_choice == '7':
            break
        else:
            console.print("[red]⚠️ Please enter a number between 1 and 7[/]")
            continue
        
        # Save after each edit and show updated details
        if save_board():
            console.print("[green]✅ Changes saved[/]")
        _display_task_details(task)

def _display_task_details(task: Dict[str, Any]) -> None:
    """Display detailed task information."""
    console.print("\n[bold]Current Task Details:[/]")
    console.print(f"  ID: [cyan]{task['id'][:8]}[/]")
    console.print(f"  Title: [yellow]{task['title']}[/]")
    console.print(f"  Description: [dim]{task.get('description', 'No description')}[/]")
    
    priority = task.get('priority', 'medium')
    priority_symbol = get_priority_symbol(priority)
    console.print(f"  Priority: {priority_symbol} [bold]{priority.title()}[/]")
    
    due_date = task.get('due_date')
    if due_date:
        due_display = format_due_date(due_date)
        console.print(f"  Due Date: {due_display}")
    else:
        console.print("  Due Date: [dim]Not set[/]")
    
    tags = task.get('tags', [])
    if tags:
        tags_display = ", ".join(f"[magenta]#{tag}[/]" for tag in tags)
        console.print(f"  Tags: {tags_display}")
    else:
        console.print("  Tags: [dim]None[/]")
    
    created_at = task.get('created_at')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at)
            console.print(f"  Created: [dim]{created_date.strftime('%Y-%m-%d %H:%M')}[/]")
        except ValueError:
            console.print(f"  Created: [dim]{created_at}[/]")

def _edit_task_title(task: Dict[str, Any]) -> None:
    """Edit task title."""
    console.print(f"\n[bold]Current title:[/] {task['title']}")
    
    for attempt in range(3):
        new_title = Prompt.ask("[green]New title[/]")
        is_valid, error_msg = validate_title(new_title)
        if is_valid:
            old_title = task['title']
            task['title'] = new_title.strip()
            console.print(f"[green]✅ Title changed from '{old_title}' to '{task['title']}'[/]")
            return
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
    
    console.print("[yellow]❌ Too many invalid attempts. Title unchanged.[/]")

def _edit_task_description(task: Dict[str, Any]) -> None:
    """Edit task description."""
    current_desc = task.get('description', '')
    console.print(f"\n[bold]Current description:[/] {current_desc if current_desc else '[dim]Empty[/]'}")
    
    new_description = Prompt.ask("[cyan]New description[/] (enter empty to clear)", default=current_desc)
    task['description'] = new_description.strip()
    console.print("[green]✅ Description updated[/]")

def _edit_task_priority(task: Dict[str, Any]) -> None:
    """Edit task priority."""
    current_priority = task.get('priority', 'medium')
    priority_symbol = get_priority_symbol(current_priority)
    console.print(f"\n[bold]Current priority:[/] {priority_symbol} {current_priority.title()}")
    
    for attempt in range(3):
        new_priority = Prompt.ask(
            "[yellow]New priority[/] ([red]high[/]/[yellow]medium[/]/[green]low[/])",
            default=current_priority
        )
        is_valid, error_msg = validate_priority(new_priority)
        if is_valid:
            task['priority'] = new_priority.strip().lower()
            new_symbol = get_priority_symbol(task['priority'])
            console.print(f"[green]✅ Priority changed to {new_symbol} {task['priority'].title()}[/]")
            return
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
    
    console.print("[yellow]❌ Too many invalid attempts. Priority unchanged.[/]")

def _edit_task_due_date(task: Dict[str, Any]) -> None:
    """Edit task due date."""
    current_due = task.get('due_date')
    if current_due:
        due_display = format_due_date(current_due)
        console.print(f"\n[bold]Current due date:[/] {due_display}")
    else:
        console.print("\n[bold]Current due date:[/] [dim]Not set[/]")
    
    new_due_date = Prompt.ask(
        "[blue]New due date[/] (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS, empty to clear)",
        default=current_due or ""
    )
    
    if not new_due_date.strip():
        task['due_date'] = None
        console.print("[green]✅ Due date cleared[/]")
    else:
        is_valid, error_msg = validate_due_date(new_due_date)
        if is_valid:
            task['due_date'] = new_due_date.strip()
            due_display = format_due_date(task['due_date'])
            console.print(f"[green]✅ Due date set to {due_display}[/]")
        else:
            console.print(f"[red]⚠️ {error_msg}. Due date unchanged.[/]")

def _edit_task_tags(task: Dict[str, Any]) -> None:
    """Edit task tags."""
    current_tags = task.get('tags', [])
    if current_tags:
        tags_display = ", ".join(f"#{tag}" for tag in current_tags)
        console.print(f"\n[bold]Current tags:[/] {tags_display}")
    else:
        console.print("\n[bold]Current tags:[/] [dim]None[/]")
    
    new_tags_input = Prompt.ask(
        "[magenta]New tags[/] (comma-separated, empty to clear)",
        default=", ".join(current_tags) if current_tags else ""
    )
    
    if not new_tags_input.strip():
        task['tags'] = []
        console.print("[green]✅ Tags cleared[/]")
    else:
        is_valid, error_msg = validate_tags(new_tags_input)
        if is_valid:
            task['tags'] = [tag.strip() for tag in new_tags_input.split(',') if tag.strip()]
            if task['tags']:
                tags_display = ", ".join(f"[magenta]#{tag}[/]" for tag in task['tags'])
                console.print(f"[green]✅ Tags updated to: {tags_display}[/]")
            else:
                console.print("[green]✅ Tags cleared[/]")
        else:
            console.print(f"[red]⚠️ {error_msg}. Tags unchanged.[/]")

def _edit_task_column(task: Dict[str, Any], current_col: str) -> None:
    """Move task to a different column."""
    available_cols = [col for col in board.keys() if col != current_col]
    if not available_cols:
        console.print("[yellow]⚠️ Task is already in the only available column.[/]")
        return
    
    new_col = Prompt.ask(
        f"Move '{task['title']}' from {current_col} to which column?",
        choices=list(board.keys())
    )
    
    if new_col == current_col:
        console.print("[yellow]⚠️ Task is already in that column.[/]")
        return
    
    # Perform the move
    board[current_col].remove(task)
    board[new_col].append(task)
    
    console.print(f"[green]✅ Moved '{task['title']}' to {new_col}.[/]")

def search_and_filter_tasks():
    """Search and filter tasks based on various criteria."""
    console.print("\n[bold magenta]🔍 Search & Filter Tasks[/]")
    console.print("[dim]Enter criteria to filter tasks. Leave empty to skip a filter.[/dim]\n")
    
    # Get filter criteria
    title_search = Prompt.ask("[yellow]Search in title[/] (partial match, optional)", default="")
    description_search = Prompt.ask("[cyan]Search in description[/] (partial match, optional)", default="")
    
    # Priority filter
    priority_filter = Prompt.ask(
        "[yellow]Filter by priority[/] ([red]high[/]/[yellow]medium[/]/[green]low[/], optional)",
        default=""
    )
    if priority_filter and priority_filter.lower() not in ['high', 'medium', 'low']:
        console.print("[red]⚠️ Invalid priority. Ignoring priority filter.[/]")
        priority_filter = ""
    
    # Column filter
    column_filter = Prompt.ask(
        "[blue]Filter by column[/] (To Do/In Progress/Done, optional)",
        default=""
    )
    if column_filter and column_filter not in board.keys():
        console.print("[red]⚠️ Invalid column. Ignoring column filter.[/]")
        column_filter = ""
    
    # Tag filter
    tag_search = Prompt.ask("[magenta]Search in tags[/] (partial match, optional)", default="")
    
    # Due date filter
    due_filter = Prompt.ask(
        "[blue]Due date filter[/] ([red]overdue[/]/[yellow]today[/]/[green]upcoming[/], optional)",
        default=""
    )
    if due_filter and due_filter.lower() not in ['overdue', 'today', 'upcoming']:
        console.print("[red]⚠️ Invalid due filter. Ignoring due date filter.[/]")
        due_filter = ""
    
    # Apply filters
    matching_tasks = filter_tasks(
        title_search=title_search.strip(),
        description_search=description_search.strip(),
        priority_filter=priority_filter.strip().lower() if priority_filter else None,
        column_filter=column_filter.strip() if column_filter else None,
        tag_search=tag_search.strip(),
        due_filter=due_filter.strip().lower() if due_filter else None
    )
    
    # Display results
    _display_filtered_tasks(matching_tasks)

def filter_tasks(
    title_search: str = "",
    description_search: str = "",
    priority_filter: Optional[str] = None,
    column_filter: Optional[str] = None,
    tag_search: str = "",
    due_filter: Optional[str] = None
) -> List[Tuple[str, Dict[str, Any]]]:
    """Filter tasks based on multiple criteria.
    
    Returns:
        List of (column_name, task) tuples that match all criteria
    """
    matching_tasks = []
    now = datetime.now()
    
    for col_name, tasks in board.items():
        # Apply column filter first
        if column_filter and col_name != column_filter:
            continue
            
        for task in tasks:
            # Title search
            if title_search and title_search.lower() not in task['title'].lower():
                continue
            
            # Description search
            description = task.get('description', '')
            if description_search and description_search.lower() not in description.lower():
                continue
            
            # Priority filter
            if priority_filter and task.get('priority', 'medium') != priority_filter:
                continue
            
            # Tag search
            if tag_search:
                tags = task.get('tags', [])
                tag_match = any(tag_search.lower() in tag.lower() for tag in tags)
                if not tag_match:
                    continue
            
            # Due date filter
            if due_filter:
                due_date_str = task.get('due_date')
                if not due_date_str:
                    continue
                
                try:
                    due_date = datetime.fromisoformat(due_date_str)
                    days_diff = (due_date - now).days
                    
                    if due_filter == 'overdue' and days_diff >= 0:
                        continue
                    elif due_filter == 'today' and days_diff != 0:
                        continue
                    elif due_filter == 'upcoming' and days_diff <= 0:
                        continue
                except ValueError:
                    continue
            
            # If we get here, task matches all criteria
            matching_tasks.append((col_name, task))
    
    return matching_tasks

def _display_filtered_tasks(matching_tasks: List[Tuple[str, Dict[str, Any]]]) -> None:
    """Display filtered tasks in a formatted table."""
    console.print(f"\n[bold cyan]🔍 Search Results: {len(matching_tasks)} task(s) found[/]")
    
    if not matching_tasks:
        console.print("[yellow]No tasks match your criteria.[/]")
        return
    
    # Create results table
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Title", style="yellow", min_width=20)
    table.add_column("Column", style="blue", width=12)
    table.add_column("Priority", style="bold", width=10)
    table.add_column("Due Date", style="dim", width=15)
    table.add_column("Tags", style="magenta", width=20)
    
    for col_name, task in matching_tasks:
        # Format each field
        task_id = task['id'][:8]
        title = task['title'][:30] + "..." if len(task['title']) > 30 else task['title']
        
        priority = task.get('priority', 'medium')
        priority_symbol = get_priority_symbol(priority)
        priority_display = f"{priority_symbol} {priority.title()}"
        
        due_date = task.get('due_date')
        due_display = format_due_date(due_date) if due_date else "[dim]None[/]"
        
        tags = task.get('tags', [])
        tags_display = ", ".join(f"#{tag}" for tag in tags[:2])  # Show first 2 tags
        if len(tags) > 2:
            tags_display += f" +{len(tags)-2}"
        if not tags_display:
            tags_display = "[dim]None[/]"
        
        table.add_row(task_id, title, col_name, priority_display, due_display, tags_display)
    
    console.print(table)
    
    # Option to view detailed info for a specific task
    if len(matching_tasks) <= 10:  # Only offer if reasonable number of results
        console.print("\n[dim]Enter a task ID to view full details, or press Enter to continue...[/]")
        detail_choice = Prompt.ask("[blue]Task ID (optional)[/]", default="")
        
        if detail_choice.strip():
            # Find the task in results
            detail_matches = []
            fragment = detail_choice.strip().lower()
            for col_name, task in matching_tasks:
                if task['id'][:len(fragment)].lower() == fragment:
                    detail_matches.append((col_name, task))
            
            if len(detail_matches) == 1:
                _, task = detail_matches[0]
                console.print(f"\n[bold cyan]📝 Full Task Details:[/]")
                _display_task_details(task)
            elif len(detail_matches) > 1:
                console.print("[yellow]⚠️ Multiple tasks match that ID in results.[/]")
            else:
                console.print("[red]❌ Task ID not found in search results.[/]")

def view_statistics():
    """Display comprehensive statistics about the Kanban board."""
    console.clear()
    console.rule("[bold magenta]📊 BOARD STATISTICS[/]")
    
    stats = compute_board_statistics()
    
    # Overall Stats Panel
    overall_content = (
        f"[bold cyan]Total Tasks:[/] {stats['total_tasks']}\n"
        f"[dim green]To Do:[/] {stats['by_column']['To Do']}\n"
        f"[dim yellow]In Progress:[/] {stats['by_column']['In Progress']}\n"
        f"[dim blue]Done:[/] {stats['by_column']['Done']}"
    )
    
    console.print(Panel.fit(
        overall_content,
        title="[bold green]📈 Overview",
        border_style="green"
    ))
    
    # Priority Stats Panel
    priority_content = (
        f"🔴 [red]High Priority:[/] {stats['by_priority']['high']}\n"
        f"🟡 [yellow]Medium Priority:[/] {stats['by_priority']['medium']}\n"
        f"🟢 [green]Low Priority:[/] {stats['by_priority']['low']}"
    )
    
    console.print(Panel.fit(
        priority_content,
        title="[bold yellow]🎨 Priority Breakdown",
        border_style="yellow"
    ))
    
    # Due Date Stats Panel
    due_content = (
        f"⏰ [red]Overdue:[/] {stats['due_stats']['overdue']}\n"
        f"⏳ [yellow]Due Today:[/] {stats['due_stats']['due_today']}\n"
        f"📅 [green]Upcoming (next 7 days):[/] {stats['due_stats']['upcoming']}\n"
        f"[dim]No Due Date:[/] {stats['due_stats']['no_due_date']}"
    )
    
    due_panel_style = "red" if stats['due_stats']['overdue'] > 0 else "blue"
    console.print(Panel.fit(
        due_content,
        title="[bold blue]📅 Due Date Status",
        border_style=due_panel_style
    ))
    
    # Overdue Tasks Warning
    if stats['overdue_tasks']:
        overdue_content = "\n".join([
            f"[red]{task['id'][:4]}[/] - {task['title'][:50]}"
            for task in stats['overdue_tasks'][:10]  # Show first 10
        ])
        
        if len(stats['overdue_tasks']) > 10:
            overdue_content += f"\n[dim]... and {len(stats['overdue_tasks']) - 10} more[/]"
        
        console.print(Panel.fit(
            overdue_content,
            title="[bold red]⚠️ OVERDUE TASKS",
            border_style="red"
        ))
    
    # Tags Statistics
    if stats['tag_usage']:
        tag_content = "\n".join([
            f"[magenta]#{tag}[/]: {count} task(s)"
            for tag, count in stats['tag_usage'][:10]  # Show top 10 tags
        ])
        
        if len(stats['tag_usage']) > 10:
            tag_content += f"\n[dim]... and {len(stats['tag_usage']) - 10} more tags[/]"
        
        console.print(Panel.fit(
            tag_content,
            title="[bold magenta]🏷️ Top Tags",
            border_style="magenta"
        ))
    
    console.print(f"\n[dim]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]")

def compute_board_statistics() -> Dict[str, Any]:
    """Compute comprehensive statistics about the board.
    
    Returns:
        Dictionary containing various statistics
    """
    stats = {
        'total_tasks': 0,
        'by_column': {col: 0 for col in board.keys()},
        'by_priority': {'high': 0, 'medium': 0, 'low': 0},
        'due_stats': {
            'overdue': 0,
            'due_today': 0,
            'upcoming': 0,  # Due within 7 days
            'no_due_date': 0
        },
        'overdue_tasks': [],
        'tag_usage': []  # List of (tag, count) tuples
    }
    
    now = datetime.now()
    tag_counts = {}
    
    for col_name, tasks in board.items():
        stats['by_column'][col_name] = len(tasks)
        stats['total_tasks'] += len(tasks)
        
        for task in tasks:
            # Priority stats
            priority = task.get('priority', 'medium')
            if priority in stats['by_priority']:
                stats['by_priority'][priority] += 1
            
            # Due date stats
            due_date_str = task.get('due_date')
            if not due_date_str:
                stats['due_stats']['no_due_date'] += 1
            else:
                try:
                    due_date = datetime.fromisoformat(due_date_str)
                    days_diff = (due_date - now).days
                    
                    if days_diff < 0:
                        stats['due_stats']['overdue'] += 1
                        stats['overdue_tasks'].append(task)
                    elif days_diff == 0:
                        stats['due_stats']['due_today'] += 1
                    elif days_diff <= 7:
                        stats['due_stats']['upcoming'] += 1
                except ValueError:
                    stats['due_stats']['no_due_date'] += 1
            
            # Tag usage stats
            tags = task.get('tags', [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort tags by usage count (descending)
    stats['tag_usage'] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Sort overdue tasks by due date (most overdue first)
    stats['overdue_tasks'] = sorted(
        stats['overdue_tasks'],
        key=lambda x: datetime.fromisoformat(x['due_date']) if x.get('due_date') else datetime.max
    )
    
    return stats

#endregion

#region Board Management
# ------------------------------
# Board Management
# ------------------------------

def get_current_board_name() -> str:
    """Get the name of the currently active board."""
    current_id = boards_data.get('current_board')
    if current_id and current_id in boards_data.get('boards', {}):
        return boards_data['boards'][current_id]['name']
    return "Default Board"

def create_board():
    """Create a new board with validation."""
    console.print("\n[bold green]✨ Create New Board[/]")
    console.print("[dim]Enter details for your new board.[/dim]\n")
    
    # Get board name
    board_name = None
    for attempt in range(5):
        name_input = Prompt.ask("[bold green]Board name[/]")
        is_valid, error_msg = validate_board_name(name_input)
        if is_valid:
            # Check for duplicate names
            name_exists = any(
                board['name'].lower() == name_input.strip().lower() 
                for board in boards_data.get('boards', {}).values()
            )
            if name_exists:
                console.print("[red]⚠️ A board with this name already exists[/]")
                if attempt < 4:
                    console.print(f"[dim]Please try again ({attempt + 1}/5 attempts used)[/]")
                continue
            
            board_name = name_input.strip()
            break
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < 4:
                console.print(f"[dim]Please try again ({attempt + 1}/5 attempts used)[/]")
    
    if not board_name:
        console.print("[red]❌ Too many invalid attempts. Returning to main menu.[/]")
        return
    
    # Create the new board
    board_id = str(uuid.uuid4())
    now_iso = datetime.now().isoformat()
    
    new_board = {
        "name": board_name,
        "created_at": now_iso,
        "last_modified": now_iso,
        "columns": {
            "To Do": [],
            "In Progress": [],
            "Done": []
        }
    }
    
    # Add to boards data
    if 'boards' not in boards_data:
        boards_data['boards'] = {}
    
    boards_data['boards'][board_id] = new_board
    
    # Show preview
    console.print(f"\n[bold cyan]📋 New Board Preview:[/]")
    console.print(f"  Name: [yellow]{board_name}[/]")
    console.print(f"  Created: [dim]{datetime.fromisoformat(now_iso).strftime('%Y-%m-%d %H:%M')}[/]")
    
    # Confirm creation
    confirm = Prompt.ask("\n[bold]Create this board? (Y/n)[/]", default="Y")
    
    if confirm.lower() in ['y', 'yes', '']:
        if save_boards_data():
            console.print(f"\n[green]✅ Board '{board_name}' created successfully![/]")
            
            # Ask if user wants to switch to the new board
            switch = Prompt.ask("[bold cyan]Switch to this board now? (Y/n)[/]", default="Y")
            if switch.lower() in ['y', 'yes', '']:
                switch_to_board(board_id)
        else:
            # Remove the board from memory if save failed
            if board_id in boards_data.get('boards', {}):
                del boards_data['boards'][board_id]
            console.print(f"\n[yellow]⚠️ Board created in memory but could not save to file[/]")
    else:
        # Remove the board from memory if cancelled
        if board_id in boards_data.get('boards', {}):
            del boards_data['boards'][board_id]
        console.print("\n[yellow]❌ Board creation cancelled.[/]")

def list_boards():
    """Display all available boards."""
    console.clear()
    console.rule("[bold blue]📋 ALL BOARDS[/]")
    
    boards = boards_data.get('boards', {})
    current_board_id = boards_data.get('current_board')
    
    if not boards:
        console.print("\n[yellow]No boards found. Using default single-board mode.[/]")
        console.print("[dim]Create a new board to start using multiple boards.[/]")
        return
    
    # Create boards table
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="yellow", min_width=20)
    table.add_column("Tasks", style="cyan", width=8)
    table.add_column("Created", style="dim", width=12)
    table.add_column("Last Modified", style="dim", width=12)
    table.add_column("Status", style="bold", width=10)
    
    board_list = list(boards.items())
    for i, (board_id, board_info) in enumerate(board_list, 1):
        # Count tasks in this board
        task_count = sum(len(tasks) for tasks in board_info['columns'].values())
        
        # Format dates
        try:
            created = datetime.fromisoformat(board_info['created_at']).strftime('%m/%d/%Y')
        except ValueError:
            created = "Unknown"
        
        try:
            modified = datetime.fromisoformat(board_info['last_modified']).strftime('%m/%d/%Y')
        except ValueError:
            modified = "Unknown"
        
        # Status indicator
        status = "[green]● Active[/]" if board_id == current_board_id else "[dim]○ Inactive[/]"
        
        table.add_row(
            str(i),
            board_info['name'],
            str(task_count),
            created,
            modified,
            status
        )
    
    console.print(table)
    
    # Show current board info
    if current_board_id and current_board_id in boards:
        current_name = boards[current_board_id]['name']
        console.print(f"\n[bold green]Currently active:[/] {current_name}")
    else:
        console.print("\n[yellow]No active board (using default mode)[/]")
    
    total_boards = len(boards)
    total_tasks = sum(
        sum(len(tasks) for tasks in board_info['columns'].values())
        for board_info in boards.values()
    )
    console.print(f"[dim]Total: {total_boards} board(s) with {total_tasks} task(s)[/]")

def switch_board():
    """Switch to a different board."""
    boards = boards_data.get('boards', {})
    
    if not boards:
        console.print("\n[yellow]No boards available. Create a board first.[/]")
        return
    
    if len(boards) == 1:
        console.print("\n[yellow]Only one board exists. No switching needed.[/]")
        return
    
    console.print("\n[bold cyan]🔄 Switch Board[/]")
    console.print("[dim]Select a board to switch to:[/dim]\n")
    
    # Display board choices
    board_list = list(boards.items())
    current_board_id = boards_data.get('current_board')
    
    for i, (board_id, board_info) in enumerate(board_list, 1):
        task_count = sum(len(tasks) for tasks in board_info['columns'].values())
        status = " [green](current)[/]" if board_id == current_board_id else ""
        console.print(f"  [cyan]{i}.[/] {board_info['name']} [dim]({task_count} tasks)[/]{status}")
    
    # Get user choice
    while True:
        try:
            choice = Prompt.ask(f"[bold]Enter board number (1-{len(board_list)})[/]")
            choice_num = int(choice)
            if 1 <= choice_num <= len(board_list):
                selected_board_id = board_list[choice_num - 1][0]
                selected_board_name = board_list[choice_num - 1][1]['name']
                
                if selected_board_id == current_board_id:
                    console.print(f"[yellow]You're already on '{selected_board_name}'[/]")
                    return
                
                switch_to_board(selected_board_id)
                return
            else:
                console.print(f"[red]Please enter a number between 1 and {len(board_list)}[/]")
        except ValueError:
            console.print("[red]Please enter a valid number[/]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Board switching cancelled.[/]")
            return

def switch_to_board(board_id: str):
    """Switch to a specific board by ID."""
    global board, boards_data
    
    boards = boards_data.get('boards', {})
    if board_id not in boards:
        console.print(f"[red]❌ Board with ID {board_id} not found[/]")
        return False
    
    # Save current board state if we're switching from a multi-board setup
    current_board_id = boards_data.get('current_board')
    if current_board_id and current_board_id in boards:
        # Update the current board's data and last_modified timestamp
        boards[current_board_id]['columns'] = board.copy()
        boards[current_board_id]['last_modified'] = datetime.now().isoformat()
    
    # Switch to the new board
    boards_data['current_board'] = board_id
    board = boards[board_id]['columns'].copy()
    boards[board_id]['last_modified'] = datetime.now().isoformat()
    
    # Save the updated state
    if save_boards_data():
        board_name = boards[board_id]['name']
        console.print(f"[green]✅ Switched to board '{board_name}'[/]")
        return True
    else:
        console.print(f"[yellow]⚠️ Switched to board but could not save state[/]")
        return False

def delete_board():
    """Delete a board with confirmation."""
    boards = boards_data.get('boards', {})
    
    if not boards:
        console.print("\n[yellow]No boards available to delete.[/]")
        return
    
    if len(boards) == 1:
        console.print("\n[yellow]Cannot delete the only remaining board.[/]")
        return
    
    console.print("\n[bold red]🗑️ Delete Board[/]")
    console.print("[dim]Select a board to delete:[/dim]\n")
    
    # Display board choices (excluding current board to prevent accidental deletion)
    board_list = list(boards.items())
    current_board_id = boards_data.get('current_board')
    deletable_boards = [(bid, binfo) for bid, binfo in board_list if bid != current_board_id]
    
    if not deletable_boards:
        console.print("[yellow]No other boards available to delete. You can't delete the current active board.[/]")
        console.print("[dim]Switch to a different board first if you want to delete the current one.[/]")
        return
    
    for i, (board_id, board_info) in enumerate(deletable_boards, 1):
        task_count = sum(len(tasks) for tasks in board_info['columns'].values())
        console.print(f"  [red]{i}.[/] {board_info['name']} [dim]({task_count} tasks)[/]")
    
    # Get user choice
    while True:
        try:
            choice = Prompt.ask(f"[bold red]Enter board number to delete (1-{len(deletable_boards)})[/]")
            choice_num = int(choice)
            if 1 <= choice_num <= len(deletable_boards):
                selected_board_id = deletable_boards[choice_num - 1][0]
                selected_board_info = deletable_boards[choice_num - 1][1]
                break
            else:
                console.print(f"[red]Please enter a number between 1 and {len(deletable_boards)}[/]")
        except ValueError:
            console.print("[red]Please enter a valid number[/]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Board deletion cancelled.[/]")
            return
    
    board_name = selected_board_info['name']
    task_count = sum(len(tasks) for tasks in selected_board_info['columns'].values())
    
    # Show warning and confirm
    console.print(f"\n[bold red]⚠️ WARNING:[/] You are about to delete '[yellow]{board_name}[/]'")
    if task_count > 0:
        console.print(f"[red]This board contains {task_count} task(s) that will be permanently lost![/]")
    console.print("[dim]This action cannot be undone.[/]")
    
    confirmation = Prompt.ask(
        f"\n[bold red]Type the board name exactly to confirm deletion:[/]"
    )
    
    if confirmation == board_name:
        # Delete the board
        del boards_data['boards'][selected_board_id]
        
        if save_boards_data():
            console.print(f"\n[bold red]🗑️ Board '{board_name}' and all its tasks deleted permanently.[/]")
        else:
            console.print(f"\n[yellow]⚠️ Board deleted from memory but could not save to file[/]")
    else:
        console.print("\n[yellow]❌ Board name doesn't match. Deletion cancelled.[/]")

def rename_board():
    """Rename the current board."""
    current_board_id = boards_data.get('current_board')
    boards = boards_data.get('boards', {})
    
    if not current_board_id or current_board_id not in boards:
        console.print("\n[yellow]No active board to rename. You're in single-board mode.[/]")
        return
    
    current_board = boards[current_board_id]
    current_name = current_board['name']
    
    console.print(f"\n[bold blue]✏️ Rename Board[/]")
    console.print(f"[dim]Current name: {current_name}[/dim]\n")
    
    # Get new board name
    new_name = None
    for attempt in range(3):
        name_input = Prompt.ask("[bold blue]New board name[/]", default=current_name)
        
        if name_input.strip() == current_name:
            console.print("[yellow]Name unchanged.[/]")
            return
        
        is_valid, error_msg = validate_board_name(name_input)
        if is_valid:
            # Check for duplicate names
            name_exists = any(
                board_id != current_board_id and 
                board['name'].lower() == name_input.strip().lower() 
                for board_id, board in boards.items()
            )
            if name_exists:
                console.print("[red]⚠️ A board with this name already exists[/]")
                if attempt < 2:
                    console.print(f"[dim]Please try again ({attempt + 1}/3 attempts used)[/]")
                continue
            
            new_name = name_input.strip()
            break
        else:
            console.print(f"[red]⚠️ {error_msg}[/]")
            if attempt < 2:
                console.print(f"[dim]Please try again ({attempt + 1}/3 attempts used)[/]")
    
    if not new_name:
        console.print("[red]❌ Too many invalid attempts. Board not renamed.[/]")
        return
    
    # Update the board name and last modified timestamp
    current_board['name'] = new_name
    current_board['last_modified'] = datetime.now().isoformat()
    
    if save_boards_data():
        console.print(f"\n[green]✅ Board renamed from '{current_name}' to '{new_name}'[/]")
    else:
        # Revert the change if save failed
        current_board['name'] = current_name
        console.print(f"\n[yellow]⚠️ Board renamed in memory but could not save to file[/]")

def board_management_menu():
    """Display board management submenu."""
    if not boards_data.get('boards'):
        console.print("\n[yellow]📋 No multiple boards configured. You're in single-board mode.[/]")
        console.print("[dim]Create your first board to start using multiple boards.[/dim]")
        
        # Offer to create first board
        create_first = Prompt.ask("[bold cyan]Create your first board now? (Y/n)[/]", default="Y")
        if create_first.lower() in ['y', 'yes', '']:
            create_board()
        return
    
    while True:
        try:
            current_board_name = get_current_board_name()
            boards_count = len(boards_data.get('boards', {}))
            
            console.print(Panel.fit(
                "[bold green]1.[/] Create New Board\n"
                "[bold cyan]2.[/] List All Boards\n"
                "[bold blue]3.[/] Switch Board\n"
                "[bold yellow]4.[/] Rename Current Board\n"
                "[bold red]5.[/] Delete Board\n"
                "[bold magenta]6.[/] Back to Main Menu",
                title="[bold blue]📋 BOARD MANAGEMENT",
                subtitle=f"[dim]Active: [yellow]{current_board_name}[/yellow] • {boards_count} total boards[/dim]"
            ))
            
            board_choice = Prompt.ask("[bold]Enter choice (1-6)[/]")
            
            if board_choice == '1':
                create_board()
            elif board_choice == '2':
                list_boards()
                input("\n[dim]Press Enter to continue...[/dim]")
            elif board_choice == '3':
                switch_board()
            elif board_choice == '4':
                rename_board()
            elif board_choice == '5':
                delete_board()
            elif board_choice == '6':
                break
            else:
                console.print("[red]⚠️ Please enter a number between 1 and 6[/]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Returning to main menu...[/]")
            break
        except Exception as e:
            display_error("Unexpected error in board management menu", e)
            console.print("[yellow]Continuing...[/]")

def save_boards_data() -> bool:
    """Save the boards data structure to file with atomic writes and error handling.
    
    Returns:
        bool: True if saved successfully, False if save failed
    """
    # If we're in single-board mode (no boards_data.boards), use legacy save
    if not boards_data.get('boards'):
        return save_board()
    
    max_retries = 3
    retry_delay = 0.1  # Start with 100ms delay
    
    for attempt in range(max_retries):
        try:
            # Use atomic write: write to temp file, then replace original
            temp_dir = os.path.dirname(os.path.abspath(DATA_FILE))
            
            with tempfile.NamedTemporaryFile(mode='w', dir=temp_dir, 
                                             suffix='.tmp', delete=False, 
                                             encoding='utf-8') as temp_file:
                json.dump(boards_data, temp_file, indent=2, ensure_ascii=False)
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
                console.print(f"[green]✅ Data saved successfully (attempt {attempt + 1})[/]")
            
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

#region Help System
# ------------------------------
# Help System
# ------------------------------

def show_keyboard_shortcuts_help():
    """Display comprehensive help screen for keyboard shortcuts and features."""
    console.clear()
    console.rule("[bold green]⌨️ KEYBOARD SHORTCUTS HELP[/]")
    
    # Main menu shortcuts
    shortcuts_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    shortcuts_table.add_column("Shortcut", style="bold cyan", width=10)
    shortcuts_table.add_column("Number", style="dim", width=8)
    shortcuts_table.add_column("Action", style="yellow", min_width=20)
    shortcuts_table.add_column("Description", style="dim", min_width=30)
    
    # Add main menu shortcuts
    for action, info in KEYBOARD_SHORTCUTS.items():
        if action != 'help':  # Skip help entry for main table
            shortcuts_table.add_row(
                f"[bold cyan]{info['key']}[/]",
                action,
                info['desc'],
                f"Same as menu option {action}"
            )
    
    # Add special shortcuts
    shortcuts_table.add_row(
        "[bold cyan]h[/] or [bold cyan]?[/]",
        "-",
        "Show Help",
        "Display this help screen"
    )
    
    console.print(shortcuts_table)
    
    # Additional help sections
    console.print("\n[bold magenta]💡 Tips & Features:[/]")
    
    tips_panel = Panel.fit(
        "• [cyan]Quick Navigation:[/] Use single letters instead of numbers\n"
        "• [cyan]Case Insensitive:[/] Both 'A' and 'a' work for Add Task\n"
        "• [cyan]Task IDs:[/] Only need first 4 characters to identify tasks\n"
        "• [cyan]Validation:[/] System prevents ambiguous task ID matches\n"
        "• [cyan]Auto-save:[/] Changes are automatically saved to disk\n"
        "• [cyan]Backup Recovery:[/] Corrupted files are automatically backed up\n"
        "• [cyan]Rich Formatting:[/] Colored priority indicators and due date warnings\n"
        "• [cyan]Enhanced Tasks:[/] Support for descriptions, priorities, due dates, and tags\n"
        "• [cyan]Multiple Boards:[/] Create and manage separate project boards\n"
        "• [cyan]Auto-migration:[/] Legacy single-board data automatically upgraded",
        title="[bold green]🌟 Features",
        border_style="green"
    )
    console.print(tips_panel)
    
    # Task management help
    task_help_panel = Panel.fit(
        "• [yellow]Priority Levels:[/] 🔴 High, 🟡 Medium, 🟢 Low\n"
        "• [yellow]Due Dates:[/] Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS\n"
        "• [yellow]Tags:[/] Comma-separated, alphanumeric with hyphens/underscores\n"
        "• [yellow]Task IDs:[/] Generated automatically, use first 4+ chars to reference\n"
        "• [yellow]Columns:[/] To Do → In Progress → Done (moveable)\n"
        "• [yellow]Search:[/] Filter by title, description, priority, tags, due dates",
        title="[bold yellow]📋 Task Management",
        border_style="yellow"
    )
    console.print(task_help_panel)
    
    # Board management help
    board_help_panel = Panel.fit(
        "• [blue]Multiple Boards:[/] Create separate boards for different projects\n"
        "• [blue]Board Switching:[/] Switch between boards with 'b' shortcut\n"
        "• [blue]Auto-save State:[/] Current board and changes are saved automatically\n"
        "• [blue]Migration Support:[/] Legacy single-board data seamlessly upgraded\n"
        "• [blue]Board Operations:[/] Create, rename, delete, list all available boards\n"
        "• [blue]Safe Deletion:[/] Cannot delete current active board by accident",
        title="[bold blue]📋 Multiple Boards",
        border_style="blue"
    )
    console.print(board_help_panel)
    
    # Error recovery help
    recovery_panel = Panel.fit(
        "• [red]Data Safety:[/] All file operations use atomic writes\n"
        "• [red]Corruption Recovery:[/] Automatic backup with timestamps\n"
        "• [red]Retry Logic:[/] Exponential backoff for transient failures\n"
        "• [red]Validation:[/] All inputs validated with helpful error messages\n"
        "• [red]Read-only Mode:[/] Continues operation if file saves fail\n"
        "• [red]Migration:[/] Old task formats automatically upgraded",
        title="[bold red]🛡️ Data Safety",
        border_style="red"
    )
    console.print(recovery_panel)
    
    console.print(f"\n[dim]Enhanced Kanban Board v2.0 • Press Enter to return to main menu[/]")
    input()

#endregion

#region Main Menu
# ------------------------------
# Main Menu
# ------------------------------

def main_menu():
    """Enhanced main menu with comprehensive task management features."""
    if not load_board():
        console.print("[yellow]⚠️ Warning: Running in read-only mode (file operations may fail)[/]")
    
    while True:
        try:
            # Show current board info
            current_board_name = get_current_board_name()
            boards_count = len(boards_data.get('boards', {}))
            
            if boards_count > 0:
                board_info = f"[dim]Active Board: [yellow]{current_board_name}[/yellow] ({boards_count} total)[/dim]"
            else:
                board_info = "[dim]Single Board Mode[/dim]"
            
            console.print(Panel.fit(
                "[bold cyan]1.[/] View Board         [dim]([cyan]v[/])[/]\n"
                "[bold cyan]2.[/] Add Task          [dim]([cyan]a[/])[/]\n"
                "[bold cyan]3.[/] Edit Task         [dim]([cyan]e[/])[/]\n"
                "[bold cyan]4.[/] Move Task         [dim]([cyan]m[/])[/]\n"
                "[bold cyan]5.[/] Delete Task       [dim]([cyan]d[/])[/]\n"
                "[bold cyan]6.[/] Search & Filter   [dim]([cyan]s[/])[/]\n"
                "[bold cyan]7.[/] View Statistics    [dim]([cyan]r[/])[/]\n"
                "[bold cyan]8.[/] Board Management  [dim]([cyan]b[/])[/]\n"
                "[bold cyan]9.[/] Exit              [dim]([cyan]q[/])[/]",
                title="[bold magenta]ENHANCED KANBAN MENU",
                subtitle=f"{board_info}\nEnter number or shortcut key • [dim cyan]h[/dim cyan] for help"
            ))

            max_attempts = 3
            choice = None
            
            for attempt in range(max_attempts):
                try:
                    raw_choice = Prompt.ask("[bold]Enter choice (1-9)[/]")
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
            
            # Convert keyboard shortcut to action number if needed
            choice_lower = choice.lower()
            if choice_lower in SHORTCUT_TO_ACTION:
                action = SHORTCUT_TO_ACTION[choice_lower]
                if action == 'help':
                    show_keyboard_shortcuts_help()
                    continue
                else:
                    choice = action  # Convert shortcut to number
            
            # Execute menu choice
            if choice == '1':
                display_board()
                input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '2':
                add_task()
            elif choice == '3':
                edit_task()
            elif choice == '4':
                move_task()
            elif choice == '5':
                delete_task()
            elif choice == '6':
                search_and_filter_tasks()
                input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '7':
                view_statistics()
                input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == '8':
                board_management_menu()
            elif choice == '9':
                console.print("[bold yellow]👋 Exiting Enhanced Kanban Board. Goodbye![/]")
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
