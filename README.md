# 📋 Enhanced Python Kanban Board

A feature-rich, terminal-based Kanban board application written in Python with enterprise-level error handling, enhanced task management, comprehensive analytics, and full project organization capabilities.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Rich](https://img.shields.io/badge/UI-Rich-purple.svg)
![Features](https://img.shields.io/badge/features-enhanced-brightgreen.svg)
![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Boards](https://img.shields.io/badge/boards-multiple-green.svg)

## 🆕 Recent Updates (August 2025)

Major feature updates have been implemented to enhance productivity and project management:

### 🆕 **Version 2.0 Features**
- ✨ **Multiple Boards Support**: Create separate boards for different projects
- ✅ **Subtasks System**: Break down complex tasks into manageable subtasks with progress tracking
- ⏰ **Time Tracking System**: Built-in timer, time estimates, manual time logging, and time analytics
- 📊 **JSON Export & Reports**: Generate detailed reports (board summary, time tracking, productivity analysis)
- ⌨️ **Keyboard Shortcuts**: Single-key shortcuts for all major functions (`v`, `a`, `e`, `m`, `d`, `s`, `r`, `x`, `b`, `q`)
- 🔍 **Advanced Search & Filter**: Multi-criteria filtering by title, description, priority, tags, due dates
- 📈 **Statistics Dashboard**: Comprehensive analytics with priority breakdown, overdue tracking, tag usage
- 🔧 **Automatic Migration**: Legacy single-board data automatically upgrades to new format
- 🎨 **Enhanced UI**: Richer task display with priority indicators, due date warnings, tag visualization

All existing functionality remains fully compatible with automatic data migration.

## ✨ Features

### 🆕 Enhanced Task Management
- **📊 Three-Column Board**: "To Do", "In Progress", "Done"
- **🎯 Rich Task Properties**: Title, description, priority, due dates, and tags
- **🔴🟡🟢 Priority System**: Visual priority indicators with color coding
- **📅 Due Date Tracking**: Smart due date display with overdue warnings
- **🏷️ Tagging System**: Organize tasks with customizable tags
- **✅ Subtask Support**: Break down tasks into manageable subtasks with progress tracking
- **⏰ Time Tracking**: Built-in timer, time estimates, manual logging, and time analytics
- **✏️ In-Place Editing**: Edit any task field after creation
- **🔍 Advanced Search & Filter**: Filter tasks by title, description, priority, tags, due dates
- **📈 Statistics & Analytics**: Comprehensive board statistics and progress insights
- **📊 JSON Export & Reports**: Generate detailed reports and export data for external analysis
- **🎨 Beautiful Interface**: Rich terminal UI with colors and formatting
- **💾 Persistent Storage**: JSON-based data persistence with auto-migration

### 📋 Multiple Boards Support
- **🗂️ Project Organization**: Create separate boards for different projects
- **🔄 Easy Board Switching**: Seamlessly switch between multiple boards
- **📛 Board Management**: Create, rename, delete, and organize boards
- **🔧 Automatic Migration**: Legacy single-board data automatically upgrades
- **💾 Unified Storage**: All boards stored in single file with proper isolation

### ⌨️ Keyboard Shortcuts
- **🚀 Quick Navigation**: Single-key shortcuts for all major functions
- **📋 View Board**: Press `v` to display current board
- **➕ Add Task**: Press `a` to create new task
- **✏️ Edit Task**: Press `e` to edit existing task
- **🔄 Move Task**: Press `m` to move task between columns
- **🗑️ Delete Task**: Press `d` to delete task
- **🔍 Search**: Press `s` to search and filter tasks
- **📊 Statistics**: Press `r` for board analytics and reports
- **🗂️ Board Management**: Press `b` to manage multiple boards
- **❓ Help**: Press `h` or `?` for help and shortcuts reference

### 🛡️ Enterprise-Grade Reliability
- **🔒 Atomic File Operations**: Prevents data corruption during saves
- **🚨 Comprehensive Error Handling**: Graceful handling of all failure scenarios
- **🔧 Auto-Recovery**: Automatic backup and recovery from corrupted data
- **✅ Input Validation**: Robust validation for all user inputs
- **🔄 Retry Logic**: Exponential backoff for transient failures
- **🛠️ Cross-Platform**: Works on Windows, macOS, and Linux

### 🎯 User Experience
- **🚫 Ambiguity Prevention**: Smart task ID matching prevents confusion
- **⚠️ Confirmation Prompts**: Safety confirmations for destructive operations
- **📢 Clear Feedback**: Informative messages for all operations
- **🎹 Keyboard Friendly**: Ctrl+C handling and graceful exits
- **🔍 Empty State Handling**: Intelligent behavior when no tasks exist

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Modern web browser (for web interface)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/python_kanban_board.git
   cd python_kanban_board
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your interface**:
   
   **🌐 Web Interface (Recommended)**:
   ```bash
   python start_web.py
   ```
   
   **💻 Terminal Interface**:
   ```bash
   python kanban.py
   ```

## 🌐 Web Interface

The Enhanced Kanban Board now includes a modern web interface with real-time collaboration features!

### Features
- **🖱️ Drag & Drop**: Move tasks between columns with intuitive drag-and-drop
- **⚡ Real-Time Updates**: See changes instantly via WebSocket connections
- **📱 Mobile Responsive**: Works perfectly on phones, tablets, and desktops
- **🎨 Modern UI**: Clean, professional interface with smooth animations
- **🔄 Live Sync**: Multiple users can collaborate on the same board
- **⌨️ Keyboard Shortcuts**: Full keyboard navigation support
- **📊 Interactive Stats**: Beautiful charts and analytics
- **🌙 Auto-Refresh**: Due dates and status update automatically

### Getting Started
1. **Start the web server**:
   ```bash
   python start_web.py
   ```

2. **Open your browser** to `http://localhost:8000`

3. **Start managing tasks** with the intuitive web interface!

### Web Interface Screenshots
```
📋 Main Board View
┌─────────────────────────────────────────────────────────────┐
│  📋 Enhanced Kanban Board                    [Add Task] [⚙️] │
├─────────────┬─────────────────┬───────────────────────────────┤
│   To Do     │   In Progress   │           Done                │
├─────────────┼─────────────────┼───────────────────────────────┤
│ 🔴 Fix bug  │ 🟡 Review PR    │ 🟢 Deploy v2.1               │
│ (abc1) ✏️🗑️  │ (def2) ✏️🗑️     │ (ghi3) ✏️🗑️                    │
│ #urgent     │ #review         │ ✅ Completed                  │
└─────────────┴─────────────────┴───────────────────────────────┘

✨ Drag tasks between columns • 🔄 Real-time updates • 📱 Mobile ready
```

### Network Access
The web interface is accessible from:
- **Local**: `http://localhost:8000`
- **Network**: `http://[your-ip]:8000` (for team collaboration)
- **Mobile**: Same URLs work on mobile devices

### Web API Endpoints
For developers, the web interface exposes a REST API:
- `GET /api/board` - Get current board data
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/statistics` - Get board statistics
- `WebSocket /ws` - Real-time updates

## 📖 Usage

### Main Menu Options
1. **View Board** (`v`) - Display current state of all tasks with rich formatting
2. **Add Task** (`a`) - Create new enhanced task with properties like priority, due dates, tags
3. **Edit Task** (`e`) - Edit any existing task properties including subtasks and time tracking
4. **Move Task** (`m`) - Move task between columns using task ID
5. **Delete Task** (`d`) - Remove task from board (with confirmation)
6. **Search & Filter** (`s`) - Advanced search and filtering capabilities
7. **View Statistics** (`r`) - Comprehensive board analytics and reports
8. **Export Reports** (`x`) - Generate and export JSON reports (board summary, time tracking, productivity)
9. **Board Management** (`b`) - Create, switch, rename, and delete boards
10. **Exit** (`q`) - Save and quit the application

### Keyboard Shortcuts
For faster navigation, you can use single-key shortcuts instead of menu numbers:
- Press the letter in parentheses next to each menu option
- Press `h` or `?` for help and shortcuts reference
- All shortcuts work from the main menu

### Task Identification
- Each task has a unique ID displayed as first 4 characters (e.g., `abc1`)
- Enter these 4 characters to identify tasks for moving/deleting
- System prevents ambiguous matches and asks for more characters if needed

### Enhanced Task Creation
When adding a new task, you'll be prompted for comprehensive details:
```
✨ Create New Task
* Task title: Implement user authentication
Description (optional): Add login/logout functionality with JWT tokens
Priority (high/medium/low): high
Due date (YYYY-MM-DD, optional): 2025-09-15
Tags (comma-separated, optional): security, backend, auth

📋 Task Preview:
  Title: Implement user authentication
  Priority: 🔴 High
  Description: Add login/logout functionality with JWT tokens
  Due: 📅 Due 2025-09-15
  Tags: #security, #backend, #auth
  
Add this task? (Y/n): Y
✅ Task 'Implement user authentication' added to To Do!
```

### Subtasks Management
Break down complex tasks into manageable subtasks:
```
# When editing a task, you can manage subtasks:
📝 Editing Task: Implement user authentication

EDIT TASK MENU:
7. Manage Subtasks

# Add subtasks:
➕ Add Subtask: Set up JWT library
➕ Add Subtask: Create login endpoint
➕ Add Subtask: Create logout endpoint  
➕ Add Subtask: Add authentication middleware

# View progress:
📋 Subtasks Progress: 2/4 completed (50%)
✅ Set up JWT library
✅ Create login endpoint
⏳ Create logout endpoint
⏳ Add authentication middleware
```

### ⏰ Time Tracking System
Track time spent on tasks with built-in timer and manual logging:
```
# Time tracking during task editing:
📝 Editing Task: Implement user authentication

EDIT TASK MENU:
6. Time Tracking

⏱️ TIME TRACKING MENU:
1. Set Time Estimate
2. Start Timer
3. Stop Timer  
4. Log Time Entry
5. View All Time Entries

# Set time estimate:
New time estimate (hours, e.g. 2.5): 4
✅ Time estimate set to 4h

# Start/Stop timer workflow:
▶️ Timer started for 'Implement user authentication'
# ... work on task ...
Description for this time entry: Initial JWT setup
✅ Timer stopped. Logged 1h 23m

# Manual time logging:
Time worked (hours): 0.5
Description: Code review and testing
✅ Time logged: 30m

# View time summary:
⏱️ Estimated: 4h
⏰ Spent: 1h 53m
📊 Progress: 48%

📋 Recent Time Entries:
  1. 1h 23m on 08/28 14:30 - Initial JWT setup
  2. 30m on 08/28 16:15 - Code review and testing
```

### Multiple Boards Workflow
Organize different projects with separate boards:
```
🗂️ Board Management:
1. Create New Board
2. List All Boards
3. Switch Board

# Create a new board:
Board name: Mobile App Project
✅ Board 'Mobile App Project' created successfully!
Switch to this board now? (Y/n): Y
✅ Switched to board 'Mobile App Project'

# Switch between boards:
🔄 Switch Board
1. Web Dashboard (5 tasks) (current)
2. Mobile App Project (0 tasks)
3. DevOps Infrastructure (12 tasks)

Enter board number (1-3): 2
✅ Switched to board 'Mobile App Project'
```

### Advanced Search & Filtering
Find tasks quickly with powerful search capabilities:
```
🔍 Search & Filter Tasks
Search in title (optional): authentication
Search in description (optional): JWT
Filter by priority (high/medium/low, optional): high
Filter by column (optional): To Do
Search in tags (optional): security
Due date filter (overdue/today/upcoming, optional): upcoming

🔍 Search Results: 2 task(s) found
┏━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ ID     ┃ Title   ┃ Column ┃
┣━━━━━━━━╋━━━━━━━━╋━━━━━━━━┫
┃ a1b2c3d4 ┃ Implement user auth ┃ To Do  ┃
┃ e5f6g7h8 ┃ JWT token validation ┃ To Do  ┃
┗━━━━━━━━┻━━━━━━━━┻━━━━━━━━┛
```

### Board Statistics
Get insights into your project progress:
```
📊 BOARD STATISTICS

📈 Overview        🎨 Priority Breakdown
Total Tasks: 15      🔴 High Priority: 4
To Do: 8            🟡 Medium Priority: 7  
In Progress: 4       🟢 Low Priority: 4
Done: 3
                    📅 Due Date Status
🏷️ Top Tags           ⏰ Overdue: 2
#backend: 6 tasks    ⏳ Due Today: 1
#frontend: 4 tasks   📅 Upcoming: 5
#security: 3 tasks   No Due Date: 7
#testing: 2 tasks

⚠️ OVERDUE TASKS
a1b2 - Fix critical security vulnerability
c3d4 - Update user documentation
```

### 📊 JSON Export & Reports
Generate comprehensive reports and export data for external analysis:
```
# Main export menu (press 'x' or choose option 8):
📊 REPORT TYPES
1. Board Summary Report
2. Detailed Tasks Report  
3. Time Tracking Report
4. Productivity Analysis
5. Custom Export Options

# Board Summary Report:
📊 Generating Board Summary Report...
Report Preview:
  Total Tasks: 15
  Time Tracked: 24h 30m
  Estimated: 32h
  Overdue Tasks: 2

Custom filename (optional, .json will be added): project_summary
✅ Board summary exported successfully!
Saved to: E:\project_summary_20250829_041200.json

# Time Tracking Report with date filtering:
⏰ Generating Time Tracking Report...
Choose date range:
  1. All time (complete history)
  2. Last 7 days
  3. Last 30 days
  4. Custom range

Enter choice: 2
Report Preview:
  Date Range: Last 7 days
  Total Hours: 12.5
  Total Entries: 8
  Tasks with Data: 5

# Productivity Analysis:
📈 Generating Productivity Analysis...
Report Preview:
  Completion Rate: 68.2%
  WIP Ratio: 33.3%
  Overdue Tasks: 2

Key Recommendations:
  1. Focus on completing In Progress tasks before starting new ones
  2. Address 2 overdue high-priority tasks first
  3. Consider breaking down large tasks into smaller subtasks

# Custom filtered export:
🔧 Custom Export Options
Apply filters (leave empty to include all):
Include only column: In Progress
Include only priority: high
Include only tasks with tag: security

Custom Report Preview:
  Matching Tasks: 3
  Column Filter: In Progress
  Priority Filter: High
  Tag Filter: #security
```

### Basic Example Workflow
```
📋 KANBAN BOARD - Web Dashboard
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ To Do                   │ In Progress             │ Done                    │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ 🔴 Fix authentication bug │ 🟡 Review PR #123       │ 🟢 Deploy v2.1.0        │
│ (a1b2)                  │ (c3d4)                  │ (e5f6)                  │
│ ⏰ Overdue (2d)            │ #frontend #review       │ Subtasks: 3/3 (100%)    │
│ #security #critical     │                         │ 📅 Completed 08/25      │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘

# Quick actions with keyboard shortcuts:
Press 'v' to view board, 'a' to add task, 'm' to move task
Press 's' to search, 'r' for statistics, 'b' for board management

# Move task with ID:
Enter task ID: a1b2
Move to: In Progress  
✅ Task moved successfully!
```

## 🛡️ Error Handling & Safety Features

### File Operation Safety
- **Atomic Writes**: Uses temporary files and atomic replacement to prevent corruption
- **Permission Handling**: Graceful degradation when file access is denied
- **Disk Space Detection**: Intelligent handling of disk full scenarios
- **Retry Mechanism**: Up to 3 attempts with exponential backoff for transient failures

### Data Corruption Recovery
- **Automatic Backup**: Corrupted files are backed up with timestamps
- **Structure Validation**: Ensures loaded data matches expected schema
- **Fresh Start Recovery**: Creates new board when corruption is detected
- **Backup Naming**: `kanban_data.json.bak_corrupt_YYYYMMDD_HHMMSS`

### Input Validation
- **Task Titles**: 1-100 characters, no control characters
- **Subtask Titles**: 1-80 characters, no control characters
- **Task IDs**: Minimum 4 characters, alphanumeric with hyphens
- **Menu Choices**: Must be valid numbers 1-9 or keyboard shortcuts
- **Priority Levels**: Must be 'high', 'medium', or 'low'
- **Due Dates**: Must be valid ISO format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- **Tags**: Alphanumeric with hyphens/underscores, max 20 characters each
- **Board Names**: 1-50 characters, no invalid filename characters
- **Duplicate Prevention**: Unique 4-character ID prefixes guaranteed
- **Multiple Attempts**: Allows correction of invalid inputs

## 📁 File Structure

```
python_kanban_board/
├── kanban.py              # Terminal application
├── web_app.py            # FastAPI web application  
├── start_web.py          # Web server launcher
├── requirements.txt       # Python dependencies
├── kanban_data.json      # Task data (auto-created)
├── templates/            # HTML templates
│   ├── index.html        # Main kanban board page
│   ├── boards.html       # Board management page
│   └── statistics.html   # Statistics & analytics page
├── static/               # Web assets
│   ├── css/
│   │   └── kanban.css    # Stylesheet
│   └── js/
│       └── kanban.js     # JavaScript functionality
├── test_kanban_features.py # Test suite
├── README.md             # This file
├── LICENSE               # License information
└── .gitignore            # Git ignore rules
```

## 🔧 Data Recovery

### If Data File Becomes Corrupted
1. Application automatically backs up corrupted file
2. Creates fresh board to continue working
3. Check for backup files: `kanban_data.json.bak_corrupt_*`
4. Manually inspect backup files to recover data if needed

### Manual Recovery
If you need to restore from a backup:
```bash
# List available backups
dir *.bak_corrupt_*

# Restore from backup (replace TIMESTAMP with actual timestamp)
copy kanban_data.json.bak_corrupt_TIMESTAMP kanban_data.json
```

## 🎯 Technical Details

### Dependencies
- **Rich**: Terminal UI framework for beautiful displays and UI components
- **Standard Library**: json, os, uuid, tempfile, shutil, datetime, typing

### Enhanced Data Format

#### Multiple Boards Format (v2.0+)
The new multiple boards format supports project organization:
```json
{
  "format_version": "2.0",
  "current_board": "board-uuid-here",
  "boards": {
    "board-uuid-here": {
      "name": "Web Dashboard Project",
      "created_at": "2025-08-28T10:30:00",
      "last_modified": "2025-08-28T15:45:00",
      "columns": {
        "To Do": [
          {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "title": "Implement user authentication",
            "description": "Add login/logout with JWT tokens",
            "priority": "high",
            "created_at": "2025-08-28T10:00:00",
            "due_date": "2025-09-15T00:00:00",
            "tags": ["security", "backend", "auth"],
            "subtasks": [
              {
                "id": "sub12345",
                "title": "Set up JWT library",
                "completed": true,
                "created_at": "2025-08-28T10:15:00"
              },
              {
                "id": "sub67890",
                "title": "Create login endpoint",
                "completed": false,
                "created_at": "2025-08-28T10:16:00"
              }
            ]
          }
        ],
        "In Progress": [],
        "Done": []
      }
    }
  }
}
```

#### Legacy Single Board Format (v1.0)
Backward compatible with original format:
```json
{
  "To Do": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Example task"
    }
  ],
  "In Progress": [],
  "Done": []
}
```

### Enhanced Task Properties

#### Core Fields
- **id**: UUID4 string for unique identification
- **title**: Task title (1-100 characters)
- **description**: Optional detailed description
- **priority**: "high", "medium", or "low"
- **created_at**: ISO datetime string
- **due_date**: Optional ISO datetime string
- **tags**: Array of tag strings
- **subtasks**: Array of subtask objects

#### Time Tracking Fields
- **estimated_hours**: Optional float for time estimate
- **time_spent**: Float total hours spent on task
- **time_entries**: Array of time entry objects with hours, description, and timestamps
- **start_time**: ISO datetime string for active timer (null when timer not running)

#### Subtask Structure
- **id**: Short UUID for subtask identification
- **title**: Subtask title (1-80 characters)
- **completed**: Boolean completion status
- **created_at**: ISO datetime string

#### Time Entry Structure
- **id**: Short UUID for time entry identification
- **hours**: Float hours worked in this entry
- **description**: Optional description of work performed
- **created_at**: ISO datetime string when logged

### Validation & Error Handling

#### Input Validation Functions
- `validate_title()`: Task title validation (1-100 chars, no control chars)
- `validate_task_id()`: Task ID format validation (min 4 chars, alphanumeric + hyphens)
- `validate_priority()`: Priority level validation (high/medium/low)
- `validate_due_date()`: Date format validation (ISO format)
- `validate_tags()`: Tag format validation (alphanumeric + hyphens/underscores)
- `validate_board_name()`: Board name validation (1-50 chars, no invalid filename chars)
- `validate_json_structure()`: Data structure integrity validation

#### Enhanced Error Handling
- **Atomic File Operations**: Prevents data corruption during saves
- **Automatic Data Migration**: Seamlessly upgrades legacy formats
- **Corrupted File Recovery**: Auto-backup and recovery mechanisms
- **Graceful Degradation**: Continues operation when non-critical operations fail
- **User-Friendly Messages**: Clear error messages without technical jargon
- **Retry Logic**: Exponential backoff for transient failures

### Keyboard Shortcut System

#### Shortcut Mapping
```python
KEYBOARD_SHORTCUTS = {
    '1': {'action': '1', 'desc': 'View Board', 'key': 'v'},
    '2': {'action': '2', 'desc': 'Add Task', 'key': 'a'},
    '3': {'action': '3', 'desc': 'Edit Task', 'key': 'e'},
    '4': {'action': '4', 'desc': 'Move Task', 'key': 'm'},
    '5': {'action': '5', 'desc': 'Delete Task', 'key': 'd'},
    '6': {'action': '6', 'desc': 'Search & Filter', 'key': 's'},
    '7': {'action': '7', 'desc': 'View Statistics', 'key': 'r'},
    '8': {'action': '8', 'desc': 'Board Management', 'key': 'b'},
    '9': {'action': '9', 'desc': 'Exit', 'key': 'q'}
}
```

### Statistics & Analytics

#### Computed Metrics
- **Task Distribution**: Count by column (To Do, In Progress, Done)
- **Priority Breakdown**: Count by priority level (High, Medium, Low)
- **Due Date Analysis**: Overdue, due today, upcoming within 7 days
- **Tag Usage Statistics**: Most frequently used tags with counts
- **Completion Progress**: Overall completion percentages
- **Overdue Task Tracking**: List of overdue tasks with details

### Search & Filter System

#### Filter Criteria
- **Title Search**: Partial text matching in task titles
- **Description Search**: Partial text matching in descriptions
- **Priority Filter**: Exact match on priority levels
- **Column Filter**: Tasks from specific columns
- **Tag Search**: Partial matching in task tags
- **Due Date Filter**: Overdue, due today, or upcoming tasks

#### Multi-Criteria Filtering
All filters work together using AND logic - tasks must match ALL specified criteria to appear in results.

### Error Handling Strategy
- **Fail-Safe**: Application never crashes due to file or input errors
- **User-Friendly**: Clear error messages without technical jargon
- **Debug Info**: Optional technical details for troubleshooting
- **Graceful Degradation**: Continues operation even when saves fail

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" errors**:
- Check file permissions on `kanban_data.json`
- Ensure you have write access to the application directory
- Application continues in read-only mode if needed

**"Task not found" errors**:
- Ensure you're entering at least 4 characters
- Check for typos in the task ID
- Use more characters if multiple tasks match

**Data file corruption**:
- Application automatically handles this
- Check for `.bak_corrupt_*` files in the directory
- Contact support if you need help recovering specific data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Test coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**NathanGr33n** - August 2025

---

*Built with ❤️ and Python*
