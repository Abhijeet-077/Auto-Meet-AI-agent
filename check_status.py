#!/usr/bin/env python3
"""
Status checker for Agentic Calendar
Verifies that both backend and frontend are running properly
"""

import requests
import socket
import sys
from datetime import datetime

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

def check_port(host, port):
    """Check if a port is open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def check_backend_health():
    """Check backend health endpoint"""
    try:
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print_colored("🔍 Agentic Calendar Status Check", "cyan")
    print_colored("=" * 40, "cyan")
    print_colored(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "white")
    print()
    
    # Check backend port
    print_colored("🔧 Backend Service (Port 8000):", "yellow")
    if check_port('localhost', 8000):
        print_colored("  ✅ Port 8000 is open", "green")
        
        # Check health endpoint
        healthy, data = check_backend_health()
        if healthy:
            print_colored("  ✅ Health endpoint responding", "green")
            print_colored(f"  📊 Status: {data.get('status', 'unknown')}", "white")
            
            services = data.get('services', {})
            for service, status in services.items():
                color = "green" if status == "configured" else "red"
                icon = "✅" if status == "configured" else "❌"
                print_colored(f"  {icon} {service.title()}: {status}", color)
        else:
            print_colored(f"  ❌ Health check failed: {data}", "red")
    else:
        print_colored("  ❌ Port 8000 is not accessible", "red")
    
    print()
    
    # Check frontend port
    print_colored("🎨 Frontend Service (Port 8501):", "yellow")
    if check_port('localhost', 8501):
        print_colored("  ✅ Port 8501 is open", "green")
        print_colored("  🌐 Frontend URL: http://localhost:8501", "blue")
    else:
        print_colored("  ❌ Port 8501 is not accessible", "red")
    
    print()
    
    # Overall status
    backend_ok = check_port('localhost', 8000)
    frontend_ok = check_port('localhost', 8501)
    
    if backend_ok and frontend_ok:
        print_colored("🎉 Overall Status: ALL SYSTEMS OPERATIONAL", "green")
        print_colored("🚀 Ready to use Agentic Calendar!", "green")
        print()
        print_colored("📱 Quick Access:", "cyan")
        print_colored("  • Frontend: http://localhost:8501", "blue")
        print_colored("  • API Docs: http://localhost:8000/docs", "blue")
        print_colored("  • Health: http://localhost:8000/api/v1/health", "blue")
    elif backend_ok and not frontend_ok:
        print_colored("⚠️  Overall Status: BACKEND ONLY", "yellow")
        print_colored("💡 Start the frontend with: streamlit run streamlit_app_fastapi.py --server.port 8501", "yellow")
    elif not backend_ok and frontend_ok:
        print_colored("⚠️  Overall Status: FRONTEND ONLY", "yellow")
        print_colored("💡 Start the backend with: cd backend_api && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000", "yellow")
    else:
        print_colored("❌ Overall Status: SERVICES DOWN", "red")
        print_colored("💡 Start both services with: python start_project.py", "yellow")
    
    return 0 if (backend_ok and frontend_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
