#!/usr/bin/env pwsh
# PowerShell script to start both FastAPI backend and Streamlit frontend

Write-Host "🚀 Starting Agentic Calendar Project..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "❌ .env.local file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.template to .env.local and configure your API keys" -ForegroundColor Yellow
    exit 1
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

# Check if ports are available
$backendPort = 8000
$frontendPort = 8501

if (-not (Test-Port $backendPort)) {
    Write-Host "❌ Port $backendPort is already in use!" -ForegroundColor Red
    Write-Host "Please stop any services running on port $backendPort" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Port $frontendPort)) {
    Write-Host "❌ Port $frontendPort is already in use!" -ForegroundColor Red
    Write-Host "Please stop any services running on port $frontendPort" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Ports $backendPort and $frontendPort are available" -ForegroundColor Green

# Start FastAPI backend in background
Write-Host "🔧 Starting FastAPI Backend on http://localhost:$backendPort..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "backend_api"
    python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Check if backend started successfully
try {
    $response = Invoke-RestMethod -Uri "http://localhost:$backendPort/api/v1/health" -TimeoutSec 5
    Write-Host "✅ Backend started successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend failed to start!" -ForegroundColor Red
    Write-Host "Stopping background job..." -ForegroundColor Yellow
    Stop-Job $backendJob
    Remove-Job $backendJob
    exit 1
}

# Start Streamlit frontend
Write-Host "🎨 Starting Streamlit Frontend on http://localhost:$frontendPort..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:$frontendPort" -ForegroundColor Yellow
Write-Host "🔧 Backend API: http://localhost:$backendPort" -ForegroundColor Yellow
Write-Host "📚 API Docs: http://localhost:$backendPort/docs" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Magenta

try {
    # Start Streamlit in foreground
    streamlit run streamlit_app_modern.py --server.port $frontendPort --server.address localhost
} finally {
    # Cleanup: Stop backend job when Streamlit exits
    Write-Host "`n🛑 Stopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Write-Host "✅ All services stopped" -ForegroundColor Green
}
