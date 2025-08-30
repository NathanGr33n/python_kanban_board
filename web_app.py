# web_app.py
# NathanGr33n
# August 2025
# FastAPI web interface for the Enhanced Python Kanban Board

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

# Import our existing kanban functionality
import kanban

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Kanban Board",
    description="A feature-rich web-based Kanban board with real-time updates",
    version="2.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Initialize the kanban system
def init_kanban():
    """Initialize the kanban board system"""
    kanban.load_board()

# Web Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main kanban board page"""
    init_kanban()
    current_board_name = kanban.get_current_board_name()
    boards_count = len(kanban.boards_data.get('boards', {}))
    
    # Get current board data
    board_data = {
        "To Do": kanban.board.get("To Do", []),
        "In Progress": kanban.board.get("In Progress", []),
        "Done": kanban.board.get("Done", [])
    }
    
    # Calculate statistics
    stats = kanban.compute_board_statistics()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "board_data": board_data,
        "current_board_name": current_board_name,
        "boards_count": boards_count,
        "stats": stats
    })

@app.get("/boards", response_class=HTMLResponse)
async def boards_page(request: Request):
    """Board management page"""
    init_kanban()
    boards = kanban.boards_data.get('boards', {})
    current_board_id = kanban.boards_data.get('current_board')
    
    boards_list = []
    for board_id, board_info in boards.items():
        task_count = sum(len(tasks) for tasks in board_info['columns'].values())
        boards_list.append({
            "id": board_id,
            "name": board_info['name'],
            "task_count": task_count,
            "created_at": board_info.get('created_at', ''),
            "is_current": board_id == current_board_id
        })
    
    return templates.TemplateResponse("boards.html", {
        "request": request,
        "boards": boards_list,
        "current_board_name": kanban.get_current_board_name()
    })

@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request):
    """Statistics and analytics page"""
    init_kanban()
    stats = kanban.compute_board_statistics()
    current_board_name = kanban.get_current_board_name()
    
    return templates.TemplateResponse("statistics.html", {
        "request": request,
        "stats": stats,
        "current_board_name": current_board_name
    })

# API Routes
@app.get("/api/board")
async def get_board():
    """Get current board data"""
    init_kanban()
    return JSONResponse({
        "board": kanban.board,
        "current_board_name": kanban.get_current_board_name(),
        "stats": kanban.compute_board_statistics()
    })

@app.get("/api/boards")
async def get_boards():
    """Get all boards"""
    init_kanban()
    boards = kanban.boards_data.get('boards', {})
    current_board_id = kanban.boards_data.get('current_board')
    
    boards_list = []
    for board_id, board_info in boards.items():
        task_count = sum(len(tasks) for tasks in board_info['columns'].values())
        boards_list.append({
            "id": board_id,
            "name": board_info['name'],
            "task_count": task_count,
            "created_at": board_info.get('created_at', ''),
            "is_current": board_id == current_board_id
        })
    
    return JSONResponse({"boards": boards_list})

@app.post("/api/tasks")
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    due_date: Optional[str] = Form(None),
    tags: str = Form("")
):
    """Create a new task"""
    init_kanban()
    
    # Validate inputs
    is_valid, error_msg = kanban.validate_title(title)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    is_valid, error_msg = kanban.validate_priority(priority)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    if due_date:
        is_valid, error_msg = kanban.validate_due_date(due_date)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Parse tags
    tag_list = []
    if tags:
        is_valid, error_msg = kanban.validate_tags(tags)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Create task
    task = kanban.create_enhanced_task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date if due_date else None,
        tags=tag_list
    )
    
    # Add to board
    kanban.board["To Do"].append(task)
    
    # Save to file
    if not kanban.save_boards_data() if kanban.boards_data.get('boards') else kanban.save_board():
        raise HTTPException(status_code=500, detail="Failed to save task")
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "task_created",
        "task": task,
        "column": "To Do"
    }))
    
    return JSONResponse({"status": "success", "task": task})

@app.put("/api/tasks/{task_id}/move")
async def move_task(task_id: str, target_column: str = Form(...)):
    """Move a task to a different column"""
    init_kanban()
    
    # Validate target column
    if target_column not in kanban.board:
        raise HTTPException(status_code=400, detail="Invalid target column")
    
    # Find the task
    source_column = None
    task = None
    
    for col_name, tasks in kanban.board.items():
        for t in tasks:
            if t["id"].startswith(task_id.lower()) or task_id.lower() in t["id"].lower():
                task = t
                source_column = col_name
                break
        if task:
            break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if source_column == target_column:
        raise HTTPException(status_code=400, detail="Task is already in target column")
    
    # Move the task
    kanban.board[source_column].remove(task)
    kanban.board[target_column].append(task)
    
    # Save to file
    if not kanban.save_boards_data() if kanban.boards_data.get('boards') else kanban.save_board():
        raise HTTPException(status_code=500, detail="Failed to save changes")
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "task_moved",
        "task": task,
        "from_column": source_column,
        "to_column": target_column
    }))
    
    return JSONResponse({
        "status": "success",
        "task": task,
        "from_column": source_column,
        "to_column": target_column
    })

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    init_kanban()
    
    # Find the task
    source_column = None
    task = None
    
    for col_name, tasks in kanban.board.items():
        for t in tasks:
            if t["id"].startswith(task_id.lower()) or task_id.lower() in t["id"].lower():
                task = t
                source_column = col_name
                break
        if task:
            break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete the task
    kanban.board[source_column].remove(task)
    
    # Save to file
    if not kanban.save_boards_data() if kanban.boards_data.get('boards') else kanban.save_board():
        raise HTTPException(status_code=500, detail="Failed to save changes")
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "task_deleted",
        "task_id": task["id"],
        "column": source_column
    }))
    
    return JSONResponse({"status": "success", "task_id": task["id"]})

@app.put("/api/tasks/{task_id}")
async def update_task(
    task_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    priority: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Update a task"""
    init_kanban()
    
    # Find the task
    task = None
    source_column = None
    
    for col_name, tasks in kanban.board.items():
        for t in tasks:
            if t["id"].startswith(task_id.lower()) or task_id.lower() in t["id"].lower():
                task = t
                source_column = col_name
                break
        if task:
            break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields if provided
    if title is not None:
        is_valid, error_msg = kanban.validate_title(title)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        task["title"] = title.strip()
    
    if description is not None:
        task["description"] = description.strip()
    
    if priority is not None:
        is_valid, error_msg = kanban.validate_priority(priority)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        task["priority"] = priority.lower()
    
    if due_date is not None:
        if due_date.strip():
            is_valid, error_msg = kanban.validate_due_date(due_date)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            task["due_date"] = due_date.strip()
        else:
            task["due_date"] = None
    
    if tags is not None:
        if tags.strip():
            is_valid, error_msg = kanban.validate_tags(tags)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            task["tags"] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        else:
            task["tags"] = []
    
    # Save to file
    if not kanban.save_boards_data() if kanban.boards_data.get('boards') else kanban.save_board():
        raise HTTPException(status_code=500, detail="Failed to save changes")
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "task_updated",
        "task": task,
        "column": source_column
    }))
    
    return JSONResponse({"status": "success", "task": task})

@app.get("/api/statistics")
async def get_statistics():
    """Get board statistics"""
    init_kanban()
    stats = kanban.compute_board_statistics()
    return JSONResponse(stats)

@app.post("/api/boards")
async def create_board(name: str = Form(...)):
    """Create a new board"""
    init_kanban()
    
    # Validate board name
    is_valid, error_msg = kanban.validate_board_name(name)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check for duplicate names
    boards = kanban.boards_data.get('boards', {})
    name_exists = any(
        board['name'].lower() == name.strip().lower() 
        for board in boards.values()
    )
    if name_exists:
        raise HTTPException(status_code=400, detail="A board with this name already exists")
    
    # Create the board (simplified version of kanban.create_board())
    import uuid
    board_id = str(uuid.uuid4())
    now_iso = datetime.now().isoformat()
    
    new_board = {
        "name": name.strip(),
        "created_at": now_iso,
        "last_modified": now_iso,
        "columns": {
            "To Do": [],
            "In Progress": [],
            "Done": []
        }
    }
    
    # Add to boards data
    if 'boards' not in kanban.boards_data:
        kanban.boards_data['boards'] = {}
    
    kanban.boards_data['boards'][board_id] = new_board
    
    # Save to file
    if not kanban.save_boards_data():
        raise HTTPException(status_code=500, detail="Failed to save board")
    
    return JSONResponse({"status": "success", "board_id": board_id, "name": name})

@app.post("/api/boards/{board_id}/switch")
async def switch_board(board_id: str):
    """Switch to a different board"""
    init_kanban()
    
    if not kanban.switch_to_board(board_id):
        raise HTTPException(status_code=404, detail="Board not found or switch failed")
    
    # Broadcast board change
    await manager.broadcast(json.dumps({
        "type": "board_switched",
        "board_id": board_id,
        "board_name": kanban.get_current_board_name()
    }))
    
    return JSONResponse({
        "status": "success",
        "board_name": kanban.get_current_board_name(),
        "board": kanban.board
    })

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo received message (for testing)
            await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
