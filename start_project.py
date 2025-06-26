#!/usr/bin/env python3
"""
Agentic Calendar - Production Startup Script
Cross-platform startup script for professional deployment
Starts both FastAPI backend and modern Streamlit frontend
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
from pathlib import Path

def print_colored(text, color="white"):
    """Print colored text to console"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def check_port(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def wait_for_backend(url, timeout=30):
    """Wait for backend to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

def main():
    print_colored("🚀 Starting Agentic Calendar Project...", "green")
    print_colored("=====================================", "green")

    # Check if .env.local exists
    if not Path(".env.local").exists():
        print_colored("❌ .env.local file not found!", "red")
        print_colored("Please copy .env.template to .env.local and configure your API keys", "yellow")
        return 1

    # Check ports
    backend_port = 8000
    frontend_port = 8501

    # Check if ports are in use and offer to kill existing processes
    if not check_port(backend_port):
        print_colored(f"⚠️  Port {backend_port} is already in use!", "yellow")
        response = input("Do you want to continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            return 1

    if not check_port(frontend_port):
        print_colored(f"⚠️  Port {frontend_port} is already in use!", "yellow")
        response = input("Do you want to continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            return 1

    print_colored(f"✅ Starting services on ports {backend_port} and {frontend_port}", "green")
    
    # Start FastAPI backend
    print_colored("🔧 Starting FastAPI Backend...", "cyan")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--host", "127.0.0.1", "--port", str(backend_port)
    ]
    
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd="backend_api",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to be ready
    print_colored("⏳ Waiting for backend to start...", "yellow")
    if wait_for_backend(f"http://localhost:{backend_port}/api/v1/health"):
        print_colored("✅ Backend started successfully!", "green")
    else:
        print_colored("❌ Backend failed to start!", "red")
        backend_process.terminate()
        return 1
    
    # Start Streamlit frontend
    print_colored("🎨 Starting Streamlit Frontend...", "cyan")
    print_colored("=====================================", "green")
    print_colored(f"🌐 Frontend: http://localhost:{frontend_port}", "yellow")
    print_colored(f"🔧 Backend API: http://localhost:{backend_port}", "yellow")
    print_colored(f"📚 API Docs: http://localhost:{backend_port}/docs", "yellow")
    print_colored("=====================================", "green")
    print_colored("Press Ctrl+C to stop both services", "magenta")
    
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app_modern.py",
        "--server.port", str(frontend_port),
        "--server.address", "localhost"
    ]
    
    try:
        # Start Streamlit in foreground
        frontend_process = subprocess.run(frontend_cmd)
    except KeyboardInterrupt:
        print_colored("\n🛑 Stopping services...", "yellow")
    finally:
        # Cleanup
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print_colored("✅ All services stopped", "green")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
