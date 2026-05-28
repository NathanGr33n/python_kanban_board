from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)
from textual import on

from kanban.models import Board, Column, Priority, Task, COLUMN_ORDER
from kanban.storage import load_board, save_board

PRIORITY_COLORS = {
    Priority.HIGH: "red",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "green",
}

PRIORITY_ICONS = {
    Priority.HIGH: "🔴",
    Priority.MEDIUM: "🟡",
    Priority.LOW: "🟢",
}


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

class TaskCard(Static):
    """Visual display of a single task."""

    def __init__(self, task: Task) -> None:
        color = PRIORITY_COLORS[task.priority]
        icon = PRIORITY_ICONS[task.priority]
        parts = [f"{icon} [{color} bold]{task.title}[/]"]
        if task.description:
            parts.append(f"  [dim]{task.description}[/]")
        parts.append(f"  [dim italic]{task.priority.value} priority[/]")
        super().__init__("\n".join(parts))


class TaskItem(ListItem):
    """A selectable list item wrapping a TaskCard."""

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task_id = task.id
        self._kanban_task = task

    def compose(self) -> ComposeResult:
        yield TaskCard(self._kanban_task)


class ColumnHeader(Static):
    """Styled header for a kanban column."""


class KanbanColumn(Vertical):
    """A single kanban column containing a header and task list."""

    def __init__(self, column: Column) -> None:
        slug = column.value.lower().replace(" ", "-")
        super().__init__(id=f"col-{slug}")
        self.column = column

    def compose(self) -> ComposeResult:
        slug = self.column.value.lower().replace(" ", "-")
        yield ColumnHeader(f" {self.column.value} ", classes="column-header")
        yield ListView(id=f"list-{slug}")


# ---------------------------------------------------------------------------
# Modal screens
# ---------------------------------------------------------------------------

class AddTaskScreen(ModalScreen[Task | None]):
    """Modal for creating a new task."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label("Add New Task", classes="modal-title")
            yield Label("Title")
            yield Input(placeholder="Task title", id="title-input")
            yield Label("Description (optional)")
            yield Input(placeholder="Description", id="desc-input")
            yield Label("Priority")
            yield Select(
                [(p.value.capitalize(), p.value) for p in Priority],
                value="medium",
                id="priority-select",
            )
            with Horizontal(classes="button-row"):
                yield Button("Add", variant="primary", id="btn-add")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    @on(Button.Pressed, "#btn-add")
    def _submit(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()
        if not title:
            self.notify("Title is required", severity="error")
            return
        desc = self.query_one("#desc-input", Input).value.strip()
        priority = Priority(self.query_one("#priority-select", Select).value)
        self.dismiss(Task(title=title, description=desc, priority=priority))

    @on(Button.Pressed, "#btn-cancel")
    def _cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class EditTaskScreen(ModalScreen[Task | None]):
    """Modal for editing an existing task."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, task: Task) -> None:
        super().__init__()
        self._kanban_task = task

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label("Edit Task", classes="modal-title")
            yield Label("Title")
            yield Input(value=self._kanban_task.title, id="title-input")
            yield Label("Description")
            yield Input(value=self._kanban_task.description, id="desc-input")
            yield Label("Priority")
            yield Select(
                [(p.value.capitalize(), p.value) for p in Priority],
                value=self._kanban_task.priority.value,
                id="priority-select",
            )
            with Horizontal(classes="button-row"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    @on(Button.Pressed, "#btn-save")
    def _submit(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()
        if not title:
            self.notify("Title is required", severity="error")
            return
        self._kanban_task.title = title
        self._kanban_task.description = self.query_one("#desc-input", Input).value.strip()
        self._kanban_task.priority = Priority(
            self.query_one("#priority-select", Select).value
        )
        self.dismiss(self._kanban_task)

    @on(Button.Pressed, "#btn-cancel")
    def _cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfirmDeleteScreen(ModalScreen[bool]):
    """Confirmation dialog for task deletion."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, task_title: str) -> None:
        super().__init__()
        self._title = task_title

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container confirm-container"):
            yield Label(f'Delete "{self._title}"?', classes="modal-title")
            with Horizontal(classes="button-row"):
                yield Button("Delete", variant="error", id="btn-yes")
                yield Button("Cancel", id="btn-no")

    @on(Button.Pressed, "#btn-yes")
    def _yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-no")
    def _no(self) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class KanbanApp(App):
    """A TUI Kanban Board."""

    TITLE = "Kanban Board"

    CSS = """
    Screen {
        background: $surface-darken-1;
    }
    Header {
        background: #5b21b6;
        color: #f5f3ff;
    }

    Footer {
        background: #4c1d95;
        color: #ede9fe;
    }

    Footer > .footer--key {
        background: #7c3aed;
        color: #f5f3ff;
    }

    #board {
        height: 1fr;
    }

    KanbanColumn {
        width: 1fr;
        border: solid #7c3aed;
        margin: 0 1;
    }

    .column-header {
        text-align: center;
        text-style: bold;
        background: #7c3aed;
        color: #f5f3ff;
        padding: 1 0;
    }

    ListView {
        height: 1fr;
        padding: 1;
    }

    ListItem {
        padding: 1;
        margin: 0 0 1 0;
        background: $surface;
    }

    ListItem > TaskCard {
        padding: 0 1;
    }

    .modal-container {
        width: 60;
        max-height: 80%;
        border: thick #7c3aed;
        background: $surface;
        padding: 1 2;
    }

    .confirm-container {
        height: auto;
    }

    .modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }

    .button-row {
        margin-top: 1;
        align: center middle;
        height: auto;
    }

    .button-row Button {
        margin: 0 1;
    }

    .button-row Button.-primary {
        background: #7c3aed;
        color: #f5f3ff;
    }

    .button-row Button.-primary:hover {
        background: #8b5cf6;
    }

    AddTaskScreen, EditTaskScreen, ConfirmDeleteScreen {
        align: center middle;
    }

    Input {
        margin-bottom: 1;
    }

    Select {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("a", "add_task", "Add Task"),
        Binding("e", "edit_task", "Edit"),
        Binding("d", "delete_task", "Delete"),
        Binding("l", "move_left", "← Move Left"),
        Binding("r", "move_right", "Move Right →"),
        Binding("tab", "focus_next_column", "Next Column", show=False),
        Binding("shift+tab", "focus_prev_column", "Prev Column", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.board = load_board()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="board"):
            for col in COLUMN_ORDER:
                yield KanbanColumn(col)
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_board()
        first_list = self.query("ListView").first()
        if first_list:
            first_list.focus()

    # --- Board refresh ---

    def _refresh_board(self) -> None:
        """Rebuild all three column ListViews from board data."""
        for col in COLUMN_ORDER:
            slug = col.value.lower().replace(" ", "-")
            lv = self.query_one(f"#list-{slug}", ListView)
            lv.clear()
            tasks = self.board.tasks_in_column(col)
            for task in tasks:
                lv.append(TaskItem(task))
            if tasks:
                lv.index = 0
        self._update_headers()

    def _update_headers(self) -> None:
        for col in COLUMN_ORDER:
            slug = col.value.lower().replace(" ", "-")
            header = self.query_one(f"#col-{slug} ColumnHeader", ColumnHeader)
            count = len(self.board.tasks_in_column(col))
            header.update(f" {col.value} ({count}) ")

    # --- Helpers ---

    def _get_selected_task(self) -> Task | None:
        for lv in self.query(ListView):
            if lv.has_focus and lv.highlighted_child is not None:
                item = lv.highlighted_child
                if isinstance(item, TaskItem):
                    return self.board.get_task(item.task_id)
        return None

    def _get_focused_column(self) -> Column | None:
        for col in COLUMN_ORDER:
            slug = col.value.lower().replace(" ", "-")
            lv = self.query_one(f"#list-{slug}", ListView)
            if lv.has_focus:
                return col
        return None

    # --- Actions ---

    def action_add_task(self) -> None:
        def on_result(task: Task | None) -> None:
            if task is None:
                return
            col = self._get_focused_column() or Column.TODO
            task.column = col
            self.board.add_task(task)
            save_board(self.board)
            self._refresh_board()
            self.notify(f"Added: {task.title}")

        self.push_screen(AddTaskScreen(), callback=on_result)

    def action_edit_task(self) -> None:
        task = self._get_selected_task()
        if not task:
            self.notify("No task selected", severity="warning")
            return

        def on_result(result: Task | None) -> None:
            if result is None:
                return
            save_board(self.board)
            self._refresh_board()
            self.notify(f"Updated: {result.title}")

        self.push_screen(EditTaskScreen(task), callback=on_result)

    def action_delete_task(self) -> None:
        task = self._get_selected_task()
        if not task:
            self.notify("No task selected", severity="warning")
            return

        def on_result(confirmed: bool) -> None:
            if not confirmed:
                return
            self.board.remove_task(task.id)
            save_board(self.board)
            self._refresh_board()
            self.notify(f"Deleted: {task.title}")

        self.push_screen(ConfirmDeleteScreen(task.title), callback=on_result)

    def _move_task(self, direction: int) -> None:
        """Move the selected task left (-1) or right (+1)."""
        task = self._get_selected_task()
        if not task:
            self.notify("No task selected", severity="warning")
            return
        idx = COLUMN_ORDER.index(task.column)
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(COLUMN_ORDER):
            edge = "first" if direction < 0 else "last"
            self.notify(f"Already in {edge} column", severity="warning")
            return
        task.column = COLUMN_ORDER[new_idx]
        save_board(self.board)
        self._refresh_board()
        slug = task.column.value.lower().replace(" ", "-")
        self.query_one(f"#list-{slug}", ListView).focus()
        self.notify(f"Moved '{task.title}' to {task.column.value}")

    def action_move_left(self) -> None:
        self._move_task(-1)

    def action_move_right(self) -> None:
        self._move_task(1)

    def action_focus_next_column(self) -> None:
        lists = list(self.query(ListView))
        for i, lv in enumerate(lists):
            if lv.has_focus:
                lists[(i + 1) % len(lists)].focus()
                return
        if lists:
            lists[0].focus()

    def action_focus_prev_column(self) -> None:
        lists = list(self.query(ListView))
        for i, lv in enumerate(lists):
            if lv.has_focus:
                lists[(i - 1) % len(lists)].focus()
                return
        if lists:
            lists[0].focus()
