from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Column(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


COLUMN_ORDER = [Column.TODO, Column.IN_PROGRESS, Column.DONE]


@dataclass
class Task:
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    column: Column = Column.TODO
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["column"] = self.column.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data.get("priority", "medium")),
            column=Column(data.get("column", "To Do")),
            id=data.get("id", uuid.uuid4().hex[:8]),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class Board:
    tasks: List[Task] = field(default_factory=list)

    def tasks_in_column(self, column: Column) -> List[Task]:
        return [t for t in self.tasks if t.column == column]

    def get_task(self, task_id: str) -> Task | None:
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def to_dict(self) -> dict:
        return {"tasks": [t.to_dict() for t in self.tasks]}

    @classmethod
    def from_dict(cls, data: dict) -> Board:
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return cls(tasks=tasks)
