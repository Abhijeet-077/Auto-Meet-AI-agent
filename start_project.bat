@echo off
echo 🚀 Starting Agentic Calendar Project...
echo =====================================

REM Check if .env.local exists
if not exist ".env.local" (
    echo ❌ .env.local file not found!
    echo Please copy .env.template to .env.local and configure your API keys
    pause
    exit /b 1
)

echo ✅ Environment file found

REM Start FastAPI backend in background
echo 🔧 Starting FastAPI Backend on http://localhost:8000...
start "FastAPI Backend" cmd /k "cd backend_api && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Streamlit frontend
echo 🎨 Starting Streamlit Frontend on http://localhost:8501...
echo =====================================
echo 🌐 Frontend: http://localhost:8501
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo =====================================
echo Press Ctrl+C to stop the frontend (backend will continue running)

streamlit run streamlit_app_modern.py --server.port 8501 --server.address localhost

echo.
echo ✅ Frontend stopped
echo Note: Backend is still running in separate window
pause
