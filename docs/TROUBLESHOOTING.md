# 🔧 Agentic Calendar - Troubleshooting Guide

## Common Issues & Solutions

### 🚀 Application Startup Issues

#### Backend Service Won't Start

**Symptoms:**
- Error: "Port 8000 already in use"
- Backend health check fails
- API endpoints not accessible

**Solutions:**

1. **Check if port is in use:**
   ```bash
   # Windows
   netstat -an | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. **Kill existing process:**
   ```bash
   # Windows
   taskkill /F /PID <process_id>
   
   # macOS/Linux
   kill -9 <process_id>
   ```

3. **Start backend manually:**
   ```bash
   cd backend_api
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Use alternative port:**
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8001
   ```

#### Frontend Service Won't Start

**Symptoms:**
- Error: "Port 8501 already in use"
- Streamlit won't load
- Browser shows connection error

**Solutions:**

1. **Check port availability:**
   ```bash
   netstat -an | findstr :8501
   ```

2. **Start frontend manually:**
   ```bash
   streamlit run streamlit_app_modern.py --server.port 8501
   ```

3. **Use alternative port:**
   ```bash
   streamlit run streamlit_app_modern.py --server.port 8502
   ```

4. **Clear Streamlit cache:**
   ```bash
   streamlit cache clear
   ```

### 🔐 Authentication Issues

#### OAuth Configuration Problems

**Symptoms:**
- "OAuth not configured" message
- Authorization URL generation fails
- Connection button doesn't work

**Solutions:**

1. **Enable Demo Mode (Recommended for Evaluation):**
   ```bash
   # Visit this URL to enable demo mode
   http://localhost:8000/api/v1/demo/enable
   ```

2. **Check OAuth configuration:**
   ```bash
   # Check configuration status
   curl http://localhost:8000/api/v1/oauth/config
   ```

3. **Verify environment variables:**
   ```bash
   # Check .env.local file exists and contains:
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

#### Demo Mode Authentication Issues

**Symptoms:**
- Demo OAuth flow fails
- Demo user not displayed
- Connection status incorrect

**Solutions:**

1. **Verify demo mode is enabled:**
   ```bash
   curl http://localhost:8000/api/v1/demo/status
   ```

2. **Enable demo mode manually:**
   ```bash
   curl http://localhost:8000/api/v1/demo/enable
   ```

3. **Test demo OAuth flow:**
   ```bash
   curl http://localhost:8000/api/v1/demo/oauth/auth-url
   ```

### 🤖 AI Service Issues

#### AI Responses Not Working

**Symptoms:**
- AI doesn't respond to messages
- Error messages in chat
- "AI service unavailable" status

**Solutions:**

1. **Check AI service status:**
   ```bash
   curl http://localhost:8000/api/v1/ai/status
   ```

2. **Use Demo Mode (No API key required):**
   ```bash
   # Demo mode provides simulated AI responses
   curl http://localhost:8000/api/v1/demo/enable
   ```

3. **Verify Gemini API key (if using real API):**
   ```bash
   # Check .env.local contains:
   GEMINI_API_KEY=your_api_key
   ```

4. **Test AI endpoint directly:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "chat_history": []}'
   ```

### 📅 Calendar Integration Issues

#### Calendar Events Not Creating

**Symptoms:**
- Meeting scheduling fails
- No verification links appear
- Calendar integration errors

**Solutions:**

1. **Use Demo Mode (Recommended):**
   ```bash
   # Demo mode simulates calendar operations
   curl http://localhost:8000/api/v1/demo/enable
   ```

2. **Test demo calendar creation:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/demo/calendar/events \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Meeting", "start_time": "2024-01-01T14:00:00", "end_time": "2024-01-01T15:00:00"}'
   ```

3. **Check calendar service status:**
   ```bash
   curl http://localhost:8000/api/v1/calendar/status
   ```

### 🖥️ Frontend Display Issues

#### UI Not Loading Properly

**Symptoms:**
- Broken layout
- Missing styles
- Components not rendering

**Solutions:**

1. **Clear browser cache:**
   - Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Or use incognito/private browsing mode

2. **Restart Streamlit:**
   ```bash
   # Stop current process and restart
   streamlit run streamlit_app_modern.py --server.port 8501
   ```

3. **Check browser console for errors:**
   - Press F12 to open developer tools
   - Look for JavaScript errors in console

#### Chat Interface Issues

**Symptoms:**
- Messages not displaying
- Input box not working
- Chat history lost

**Solutions:**

1. **Clear Streamlit session:**
   - Refresh the page (F5)
   - Or restart the Streamlit server

2. **Check session state:**
   ```python
   # In Streamlit, session state should contain:
   # - messages
   # - google_calendar_connected
   # - access_token
   ```

### 🔍 Debugging & Diagnostics

#### System Health Check

**Run comprehensive health check:**
```bash
python check_status.py
```

**Expected output:**
```
✅ Backend Service: Running on port 8000
✅ Frontend Service: Running on port 8501
✅ All services configured
```

#### API Endpoint Testing

**Test all major endpoints:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Demo status
curl http://localhost:8000/api/v1/demo/status

# OAuth config
curl http://localhost:8000/api/v1/oauth/config

# AI status
curl http://localhost:8000/api/v1/ai/status
```

#### Log Analysis

**Check application logs:**
1. Backend logs appear in terminal where uvicorn is running
2. Frontend logs appear in terminal where streamlit is running
3. Browser console logs (F12 → Console tab)

### 📱 Environment-Specific Issues

#### Windows-Specific Issues

**PowerShell Execution Policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Path Issues:**
```bash
# Use full Python path if needed
C:\Python39\python.exe start_project.py
```

#### macOS/Linux-Specific Issues

**Permission Issues:**
```bash
chmod +x start_project.py
```

**Python Version Issues:**
```bash
# Use python3 explicitly
python3 start_project.py
```

### 🆘 Emergency Recovery

#### Complete Reset

**If everything fails:**
1. **Stop all processes:**
   ```bash
   # Kill all Python processes
   taskkill /F /IM python.exe  # Windows
   pkill -f python             # macOS/Linux
   ```

2. **Clear all caches:**
   ```bash
   # Clear Streamlit cache
   streamlit cache clear
   
   # Remove __pycache__ directories
   find . -name "__pycache__" -exec rm -rf {} +
   ```

3. **Restart fresh:**
   ```bash
   python start_project.py
   ```

#### Demo Mode Fallback

**For evaluation purposes, always use demo mode:**
```bash
# Enable demo mode
curl http://localhost:8000/api/v1/demo/enable

# Verify demo mode active
curl http://localhost:8000/api/v1/demo/status
```

### 📞 Getting Help

#### Quick Diagnostics
1. Run `python check_status.py`
2. Check http://localhost:8000/docs for API status
3. Verify demo mode at http://localhost:8000/api/v1/demo/status

#### Common Solutions Summary
- **Port conflicts**: Use alternative ports or kill existing processes
- **OAuth issues**: Enable demo mode for evaluation
- **AI problems**: Use demo mode for simulated responses
- **UI issues**: Clear cache and restart services
- **General problems**: Enable demo mode as fallback

#### Contact Information
- **Developer**: Abhijeet Swami
- **GitHub**: https://github.com/Abhijeet-077
- **Documentation**: See `docs/` folder for comprehensive guides

---

**Remember**: Demo mode solves 90% of evaluation issues by providing simulated functionality without requiring real API credentials!
