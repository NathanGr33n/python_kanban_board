#!/usr/bin/env python3
"""
Test script for enhanced Kanban features
Tests the new functionality without UI interaction
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to the path so we can import kanban
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the kanban module
import kanban

def test_enhanced_task_creation():
    """Test creating enhanced tasks"""
    print("🧪 Testing enhanced task creation...")
    
    # Test creating a task with all fields
    task = kanban.create_enhanced_task(
        title="Test Task with All Fields",
        description="This is a test task with full details",
        priority="high",
        due_date="2025-08-25",
        tags=["testing", "python", "kanban"]
    )
    
    print(f"✅ Created task: {task['title']}")
    print(f"   Priority: {task['priority']}")
    print(f"   Due date: {task['due_date']}")
    print(f"   Tags: {task['tags']}")
    print(f"   Description: {task['description']}")
    
    # Test validation functions
    assert kanban.validate_title("Valid Title")[0] == True
    assert kanban.validate_title("")[0] == False
    assert kanban.validate_priority("high")[0] == True
    assert kanban.validate_priority("invalid")[0] == False
    assert kanban.validate_due_date("2025-12-31")[0] == True
    assert kanban.validate_due_date("invalid-date")[0] == False
    assert kanban.validate_tags("tag1, tag2, tag3")[0] == True
    assert kanban.validate_tags("tag1, , tag3")[0] == False
    
    print("✅ All validation tests passed!")

def test_filtering():
    """Test task filtering functionality"""
    print("\n🧪 Testing task filtering...")
    
    # Create test board with sample tasks
    kanban.board = {
        "To Do": [
            {
                "id": "test-001", "title": "High Priority Task", 
                "priority": "high", "description": "Urgent work",
                "created_at": datetime.now().isoformat(),
                "due_date": (datetime.now() - timedelta(days=1)).isoformat(),  # Overdue
                "tags": ["urgent", "work"]
            },
            {
                "id": "test-002", "title": "Medium Priority Task",
                "priority": "medium", "description": "Regular work",
                "created_at": datetime.now().isoformat(),
                "due_date": None, "tags": ["work"]
            }
        ],
        "In Progress": [
            {
                "id": "test-003", "title": "Low Priority Task",
                "priority": "low", "description": "Minor task",
                "created_at": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),  # Due tomorrow
                "tags": ["minor"]
            }
        ],
        "Done": []
    }
    
    # Test title filter
    matches = kanban.filter_tasks(title_search="High")
    assert len(matches) == 1
    assert matches[0][1]['title'] == "High Priority Task"
    print("✅ Title filtering works")
    
    # Test priority filter
    matches = kanban.filter_tasks(priority_filter="high")
    assert len(matches) == 1
    assert matches[0][1]['priority'] == "high"
    print("✅ Priority filtering works")
    
    # Test column filter
    matches = kanban.filter_tasks(column_filter="In Progress")
    assert len(matches) == 1
    assert matches[0][0] == "In Progress"
    print("✅ Column filtering works")
    
    # Test tag filter
    matches = kanban.filter_tasks(tag_search="work")
    assert len(matches) == 2
    print("✅ Tag filtering works")
    
    # Test due date filter
    matches = kanban.filter_tasks(due_filter="overdue")
    assert len(matches) == 1
    assert matches[0][1]['title'] == "High Priority Task"
    print("✅ Due date filtering works")

def test_statistics():
    """Test statistics computation"""
    print("\n🧪 Testing statistics computation...")
    
    stats = kanban.compute_board_statistics()
    
    assert stats['total_tasks'] == 3
    assert stats['by_column']['To Do'] == 2
    assert stats['by_column']['In Progress'] == 1
    assert stats['by_column']['Done'] == 0
    assert stats['by_priority']['high'] == 1
    assert stats['by_priority']['medium'] == 1
    assert stats['by_priority']['low'] == 1
    assert stats['due_stats']['overdue'] == 1
    assert len(stats['overdue_tasks']) == 1
    
    print("✅ Statistics computation works correctly!")
    print(f"   Total tasks: {stats['total_tasks']}")
    print(f"   Overdue tasks: {stats['due_stats']['overdue']}")
    print(f"   Priority breakdown: {stats['by_priority']}")

def test_migration():
    """Test migration of old-format tasks"""
    print("\n🧪 Testing task migration...")
    
    # Create an old-format task
    old_task = {"id": "old-001", "title": "Old Format Task"}
    kanban.board["To Do"] = [old_task]
    
    # Run migration
    migrated_count = kanban.migrate_old_tasks()
    assert migrated_count == 1
    
    # Check that all new fields were added
    migrated_task = kanban.board["To Do"][0]
    assert "priority" in migrated_task
    assert "description" in migrated_task
    assert "created_at" in migrated_task
    assert "due_date" in migrated_task
    assert "tags" in migrated_task
    
    print("✅ Task migration works correctly!")
    print(f"   Migrated {migrated_count} task(s)")

def main():
    """Run all tests"""
    print("🚀 Running Enhanced Kanban Tests\n")
    
    try:
        test_enhanced_task_creation()
        test_filtering()
        test_statistics()
        test_migration()
        
        print("\n🎉 All tests passed! Enhanced Kanban functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
