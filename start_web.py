#!/usr/bin/env python3
"""
Enhanced Kanban Board Web Interface Launcher
Starts the FastAPI web server with proper configuration
"""

import os
import sys
import uvicorn
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import jinja2
        import rich
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies with: pip install -r requirements.txt")
        return False

def find_free_port(start_port=8000):
    """Find a free port starting from the given port"""
    import socket
    
    port = start_port
    while port <= 8099:  # Try up to port 8099
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            port += 1
    
    return start_port  # Fallback to original port

def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Kanban Board Web Interface...")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check if data file exists
    data_file = script_dir / "kanban_data.json"
    if data_file.exists():
        print(f"📄 Found existing data file: {data_file}")
    else:
        print("📄 No existing data file found - will create new board")
    
    # Find available port
    port = find_free_port(8000)
    host = "0.0.0.0"  # Allow external connections
    
    print(f"🌐 Starting web server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Local URL: http://localhost:{port}")
    print(f"   Network URL: http://{get_local_ip()}:{port}")
    print("=" * 60)
    print("📋 Web interface features:")
    print("   • Interactive Kanban board with drag & drop")
    print("   • Real-time updates via WebSocket")
    print("   • Create, edit, move, and delete tasks")
    print("   • Multiple boards support")
    print("   • Statistics and analytics")
    print("   • Mobile responsive design")
    print("=" * 60)
    
    # Offer to open browser
    if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
        try:
            # Wait a moment then open browser
            import threading
            def open_browser():
                time.sleep(2)  # Wait for server to start
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            print("🌐 Opening web browser...")
        except Exception:
            pass
    
    # Start the server
    try:
        uvicorn.run(
            "web_app:app",
            host=host,
            port=port,
            reload=True,  # Auto-reload on file changes
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down web server...")
        print("Thank you for using Enhanced Kanban Board!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

def get_local_ip():
    """Get the local IP address"""
    import socket
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return '127.0.0.1'

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
