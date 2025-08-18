# 📋 Enhanced Python Kanban Board

A feature-rich, terminal-based Kanban board application written in Python with enterprise-level error handling, enhanced task management, and comprehensive analytics.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Rich](https://img.shields.io/badge/UI-Rich-purple.svg)
![Features](https://img.shields.io/badge/features-enhanced-brightgreen.svg)

## ✨ Features

### 🆕 Enhanced Task Management
- **📊 Three-Column Board**: "To Do", "In Progress", "Done"
- **🎯 Rich Task Properties**: Title, description, priority, due dates, and tags
- **🔴🟡🟢 Priority System**: Visual priority indicators with color coding
- **📅 Due Date Tracking**: Smart due date display with overdue warnings
- **🏷️ Tagging System**: Organize tasks with customizable tags
- **✏️ In-Place Editing**: Edit any task field after creation
- **🎨 Beautiful Interface**: Rich terminal UI with colors and formatting
- **💾 Persistent Storage**: JSON-based data persistence with auto-migration

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

3. **Run the application**:
   ```bash
   python kanban.py
   ```

## 📖 Usage

### Main Menu Options
1. **View Board** - Display current state of all tasks
2. **Add Task** - Create new task in "To Do" column
3. **Move Task** - Move task between columns using task ID
4. **Delete Task** - Remove task from board (with confirmation)
5. **Exit** - Save and quit the application

### Task Identification
- Each task has a unique ID displayed as first 4 characters (e.g., `abc1`)
- Enter these 4 characters to identify tasks for moving/deleting
- System prevents ambiguous matches and asks for more characters if needed

### Example Workflow
```
📋 KANBAN BOARD
┌─────────────┬─────────────┬──────────────┐
│ To Do       │ In Progress │ Done         │
├─────────────┼─────────────┼──────────────┤
│ Fix bug     │ Review PR   │ Deploy v1.0  │
│ (a1b2)      │ (c3d4)      │ (e5f6)       │
└─────────────┴─────────────┴──────────────┘

# Move task from "To Do" to "In Progress"
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
- **Task IDs**: Minimum 4 characters, alphanumeric with hyphens
- **Menu Choices**: Must be valid numbers 1-5
- **Duplicate Prevention**: Unique 4-character ID prefixes guaranteed
- **Multiple Attempts**: Allows correction of invalid inputs

## 📁 File Structure

```
python_kanban_board/
├── kanban.py              # Main application
├── requirements.txt       # Python dependencies
├── kanban_data.json      # Task data (auto-created)
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
- **Rich**: Terminal UI framework for beautiful displays
- **Standard Library**: json, os, uuid, tempfile, shutil, datetime, typing

### Data Format
Tasks are stored in JSON format:
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
