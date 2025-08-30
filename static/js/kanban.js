// Enhanced Kanban Board JavaScript
// Interactive features with real-time updates, drag-and-drop, and modern UX

class KanbanBoard {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.currentEditingTask = null;
        
        this.init();
    }

    // Initialize the application
    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.updateDueDates();
        this.setupDragAndDrop();
        
        // Refresh due dates every minute
        setInterval(() => this.updateDueDates(), 60000);
    }

    // WebSocket setup for real-time updates
    setupWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus('connected', 'Connected');
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000; // Reset delay
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.log('WebSocket message:', event.data);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus('disconnected', 'Disconnected');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('disconnected', 'Connection Error');
            };
            
        } catch (error) {
            console.error('WebSocket setup failed:', error);
            this.updateConnectionStatus('disconnected', 'Connection Failed');
        }
    }

    // Handle WebSocket messages
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'task_created':
                this.handleTaskCreated(data);
                break;
            case 'task_updated':
                this.handleTaskUpdated(data);
                break;
            case 'task_moved':
                this.handleTaskMoved(data);
                break;
            case 'task_deleted':
                this.handleTaskDeleted(data);
                break;
            case 'board_switched':
                this.handleBoardSwitched(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    // WebSocket reconnection logic
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus('connecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.setupWebSocket();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
        } else {
            this.updateConnectionStatus('disconnected', 'Connection Lost');
        }
    }

    // Update connection status UI
    updateConnectionStatus(status, text) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (statusIndicator && statusText) {
            statusIndicator.className = `status-indicator ${status}`;
            statusText.textContent = text;
            
            // Update icon based on status
            switch (status) {
                case 'connected':
                    statusIndicator.textContent = '✅';
                    break;
                case 'connecting':
                    statusIndicator.textContent = '🔄';
                    break;
                case 'disconnected':
                    statusIndicator.textContent = '❌';
                    break;
            }
        }
    }

    // Setup event listeners
    setupEventListeners() {
        // Header buttons
        document.getElementById('add-task-btn')?.addEventListener('click', () => this.showAddTaskModal());
        document.getElementById('boards-btn')?.addEventListener('click', () => this.showBoardsModal());
        document.getElementById('stats-btn')?.addEventListener('click', () => this.redirectToStats());
        document.getElementById('refresh-btn')?.addEventListener('click', () => this.refreshBoard());

        // Modal close buttons
        document.getElementById('close-add-modal')?.addEventListener('click', () => this.hideAddTaskModal());
        document.getElementById('close-edit-modal')?.addEventListener('click', () => this.hideEditTaskModal());
        document.getElementById('close-boards-modal')?.addEventListener('click', () => this.hideBoardsModal());

        // Form cancel buttons
        document.getElementById('cancel-add-task')?.addEventListener('click', () => this.hideAddTaskModal());
        document.getElementById('cancel-edit-task')?.addEventListener('click', () => this.hideEditTaskModal());

        // Form submissions
        document.getElementById('add-task-form')?.addEventListener('submit', (e) => this.handleAddTask(e));
        document.getElementById('edit-task-form')?.addEventListener('submit', (e) => this.handleEditTask(e));

        // Task actions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-btn')) {
                const taskId = e.target.dataset.taskId;
                this.showEditTaskModal(taskId);
            } else if (e.target.classList.contains('delete-btn')) {
                const taskId = e.target.dataset.taskId;
                this.deleteTask(taskId);
            }
        });

        // Modal background clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('active');
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Board management
        document.getElementById('create-board-btn')?.addEventListener('click', () => this.showCreateBoardForm());
    }

    // Setup drag and drop functionality
    setupDragAndDrop() {
        const columns = document.querySelectorAll('.column-content');
        const tasks = document.querySelectorAll('.task-card');

        // Make tasks draggable
        tasks.forEach(task => {
            task.draggable = true;
            
            task.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.dataset.taskId);
                task.classList.add('dragging');
            });
            
            task.addEventListener('dragend', () => {
                task.classList.remove('dragging');
            });
        });

        // Setup drop zones
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => {
                e.preventDefault();
                column.classList.add('drag-over');
            });
            
            column.addEventListener('dragleave', () => {
                column.classList.remove('drag-over');
            });
            
            column.addEventListener('drop', (e) => {
                e.preventDefault();
                column.classList.remove('drag-over');
                
                const taskId = e.dataTransfer.getData('text/plain');
                const targetColumn = column.closest('.column').dataset.column;
                
                this.moveTask(taskId, targetColumn);
            });
        });
    }

    // Show add task modal
    showAddTaskModal() {
        const modal = document.getElementById('add-task-modal');
        if (modal) {
            modal.classList.add('active');
            document.getElementById('task-title')?.focus();
        }
    }

    // Hide add task modal
    hideAddTaskModal() {
        const modal = document.getElementById('add-task-modal');
        if (modal) {
            modal.classList.remove('active');
            document.getElementById('add-task-form')?.reset();
        }
    }

    // Handle add task form submission
    async handleAddTask(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner"></span> Creating...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', 'Task created successfully!');
                this.hideAddTaskModal();
                // Real-time update will handle UI refresh
            } else {
                this.showToast('error', result.detail || 'Failed to create task');
            }
        } catch (error) {
            console.error('Error creating task:', error);
            this.showToast('error', 'Network error. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    // Show edit task modal
    async showEditTaskModal(taskId) {
        const modal = document.getElementById('edit-task-modal');
        if (!modal) return;

        // Find the task data from the DOM
        const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
        if (!taskCard) return;

        this.currentEditingTask = taskId;

        // Extract task data from DOM
        const title = taskCard.querySelector('.task-title')?.textContent || '';
        const description = taskCard.querySelector('.task-description')?.textContent || '';
        const dueDateElement = taskCard.querySelector('.task-due-date');
        const dueDate = dueDateElement?.dataset.due ? dueDateElement.dataset.due.split('T')[0] : '';
        const priorityEmoji = taskCard.querySelector('.task-priority')?.textContent || '🟡';
        const tagsElements = taskCard.querySelectorAll('.tag:not(.more-tags)');
        
        // Map emoji to priority
        let priority = 'medium';
        if (priorityEmoji === '🔴') priority = 'high';
        else if (priorityEmoji === '🟢') priority = 'low';

        // Get tags
        const tags = Array.from(tagsElements).map(tag => tag.textContent.replace('#', '')).join(', ');

        // Populate form
        document.getElementById('edit-task-title').value = title;
        document.getElementById('edit-task-description').value = description.replace('...', ''); // Remove truncation
        document.getElementById('edit-task-priority').value = priority;
        document.getElementById('edit-task-due-date').value = dueDate;
        document.getElementById('edit-task-tags').value = tags;

        modal.classList.add('active');
        document.getElementById('edit-task-title')?.focus();
    }

    // Hide edit task modal
    hideEditTaskModal() {
        const modal = document.getElementById('edit-task-modal');
        if (modal) {
            modal.classList.remove('active');
            document.getElementById('edit-task-form')?.reset();
            this.currentEditingTask = null;
        }
    }

    // Handle edit task form submission
    async handleEditTask(e) {
        e.preventDefault();
        
        if (!this.currentEditingTask) return;

        const form = e.target;
        const formData = new FormData(form);
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch(`/api/tasks/${this.currentEditingTask}`, {
                method: 'PUT',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', 'Task updated successfully!');
                this.hideEditTaskModal();
                // Real-time update will handle UI refresh
            } else {
                this.showToast('error', result.detail || 'Failed to update task');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showToast('error', 'Network error. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    // Move task to different column
    async moveTask(taskId, targetColumn) {
        try {
            const formData = new FormData();
            formData.append('target_column', targetColumn);
            
            const response = await fetch(`/api/tasks/${taskId}/move`, {
                method: 'PUT',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', `Task moved to ${targetColumn}!`);
                // Real-time update will handle UI refresh
            } else {
                this.showToast('error', result.detail || 'Failed to move task');
            }
        } catch (error) {
            console.error('Error moving task:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Delete task with confirmation
    async deleteTask(taskId) {
        const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
        const taskTitle = taskCard?.querySelector('.task-title')?.textContent || 'this task';
        
        if (!confirm(`Are you sure you want to delete "${taskTitle}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', 'Task deleted successfully!');
                // Real-time update will handle UI refresh
            } else {
                this.showToast('error', result.detail || 'Failed to delete task');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Show boards modal
    async showBoardsModal() {
        const modal = document.getElementById('boards-modal');
        if (!modal) return;

        try {
            const response = await fetch('/api/boards');
            const data = await response.json();
            
            if (response.ok) {
                this.renderBoardsList(data.boards);
                modal.classList.add('active');
            } else {
                this.showToast('error', 'Failed to load boards');
            }
        } catch (error) {
            console.error('Error loading boards:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Hide boards modal
    hideBoardsModal() {
        const modal = document.getElementById('boards-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // Render boards list
    renderBoardsList(boards) {
        const container = document.getElementById('boards-list');
        if (!container) return;

        if (boards.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No boards found. Create your first board!</p>';
            return;
        }

        container.innerHTML = boards.map(board => `
            <div class="board-item ${board.is_current ? 'current' : ''}">
                <div class="board-info">
                    <div class="board-name">${board.name}</div>
                    <div class="board-meta">
                        ${board.task_count} tasks • 
                        Created ${new Date(board.created_at).toLocaleDateString()}
                        ${board.is_current ? ' • Current Board' : ''}
                    </div>
                </div>
                <div class="board-actions">
                    ${!board.is_current ? 
                        `<button class="btn btn-primary" onclick="kanban.switchBoard('${board.id}')">Switch</button>` : 
                        '<span class="text-blue-600 font-medium">Active</span>'
                    }
                </div>
            </div>
        `).join('');
    }

    // Switch to different board
    async switchBoard(boardId) {
        try {
            const response = await fetch(`/api/boards/${boardId}/switch`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', `Switched to ${result.board_name}!`);
                this.hideBoardsModal();
                // Reload page to reflect board change
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast('error', result.detail || 'Failed to switch board');
            }
        } catch (error) {
            console.error('Error switching board:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Show create board form
    showCreateBoardForm() {
        const name = prompt('Enter board name:');
        if (name && name.trim()) {
            this.createBoard(name.trim());
        }
    }

    // Create new board
    async createBoard(name) {
        try {
            const formData = new FormData();
            formData.append('name', name);
            
            const response = await fetch('/api/boards', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showToast('success', `Board "${name}" created successfully!`);
                // Refresh boards list
                this.showBoardsModal();
            } else {
                this.showToast('error', result.detail || 'Failed to create board');
            }
        } catch (error) {
            console.error('Error creating board:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Redirect to statistics page
    redirectToStats() {
        window.location.href = '/statistics';
    }

    // Refresh board data
    async refreshBoard() {
        try {
            const response = await fetch('/api/board');
            if (response.ok) {
                window.location.reload();
            } else {
                this.showToast('error', 'Failed to refresh board');
            }
        } catch (error) {
            console.error('Error refreshing board:', error);
            this.showToast('error', 'Network error. Please try again.');
        }
    }

    // Update due dates with urgency styling
    updateDueDates() {
        const dueDateElements = document.querySelectorAll('.task-due-date[data-due]');
        const now = new Date();
        
        dueDateElements.forEach(element => {
            const dueDate = new Date(element.dataset.due);
            const diffTime = dueDate - now;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            // Remove existing classes
            element.classList.remove('text-red-600', 'text-yellow-600', 'text-gray-500');
            
            if (diffDays < 0) {
                // Overdue
                element.classList.add('text-red-600');
                element.innerHTML = `⏰ Overdue (${Math.abs(diffDays)}d ago)`;
            } else if (diffDays === 0) {
                // Due today
                element.classList.add('text-yellow-600');
                element.innerHTML = '⏳ Due today';
            } else if (diffDays <= 3) {
                // Due soon
                element.classList.add('text-yellow-600');
                element.innerHTML = `⏳ Due in ${diffDays}d`;
            } else {
                // Due later
                element.classList.add('text-gray-500');
                element.innerHTML = `📅 Due ${dueDate.toLocaleDateString()}`;
            }
        });
    }

    // Handle real-time task created
    handleTaskCreated(data) {
        // Refresh page to show new task
        // In a more advanced implementation, you could dynamically add the task
        this.refreshBoard();
    }

    // Handle real-time task updated
    handleTaskUpdated(data) {
        // Refresh page to show updated task
        this.refreshBoard();
    }

    // Handle real-time task moved
    handleTaskMoved(data) {
        // Refresh page to show moved task
        this.refreshBoard();
    }

    // Handle real-time task deleted
    handleTaskDeleted(data) {
        // Remove task from DOM
        const taskCard = document.querySelector(`[data-task-id="${data.task_id}"]`);
        if (taskCard) {
            taskCard.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                taskCard.remove();
                this.updateTaskCounts();
            }, 300);
        }
    }

    // Handle real-time board switched
    handleBoardSwitched(data) {
        this.showToast('info', `Board switched to ${data.board_name}`);
        // Reload page to show new board
        setTimeout(() => window.location.reload(), 1000);
    }

    // Update task counts in column headers
    updateTaskCounts() {
        const columns = document.querySelectorAll('.column');
        columns.forEach(column => {
            const tasks = column.querySelectorAll('.task-card');
            const countElement = column.querySelector('.task-count');
            if (countElement) {
                countElement.textContent = tasks.length;
            }
        });

        // Update stats bar
        const todoCount = document.querySelectorAll('#todo-column .task-card').length;
        const progressCount = document.querySelectorAll('#progress-column .task-card').length;
        const doneCount = document.querySelectorAll('#done-column .task-card').length;
        const totalCount = todoCount + progressCount + doneCount;

        document.querySelector('.todo-count').textContent = todoCount;
        document.querySelector('.progress-count').textContent = progressCount;
        document.querySelector('.done-count').textContent = doneCount;
        document.getElementById('total-tasks').textContent = totalCount;
    }

    // Show toast notification
    showToast(type, message, duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';
        
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-message">${message}</div>
        `;

        container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, duration);

        // Click to dismiss
        toast.addEventListener('click', () => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        });
    }

    // Close all modals
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }
}

// Add CSS animation for fadeOut
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.9); }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the Kanban board when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.kanban = new KanbanBoard();
});

// Handle page visibility changes to reconnect WebSocket
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.kanban && (!window.kanban.ws || window.kanban.ws.readyState !== WebSocket.OPEN)) {
        window.kanban.setupWebSocket();
    }
});
