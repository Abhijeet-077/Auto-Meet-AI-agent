# 🚀 Agentic Calendar - Complete Startup Guide

## ✅ Project Status: READY TO RUN

Your Agentic Calendar project is now fully configured and ready to use!

## 🏃‍♂️ Quick Start (Recommended)

### Option 1: Using Python Script (Cross-platform)
```bash
python start_project.py
```

### Option 2: Using PowerShell Script (Windows)
```powershell
.\start_project.ps1
```

### Option 3: Using Batch File (Windows)
```cmd
start_project.bat
```

## 🔧 Manual Startup

If you prefer to start services manually:

### 1. Start FastAPI Backend
```bash
cd backend_api
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start Streamlit Frontend (in new terminal)
```bash
streamlit run streamlit_app_fastapi.py --server.port 8501 --server.address localhost
```

## 🌐 Access URLs

Once both services are running:

- **🎨 Frontend Application**: http://localhost:8501
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🏥 Health Check**: http://localhost:8000/api/v1/health

## ✅ System Status

All services are properly configured:

- ✅ **FastAPI Backend**: Running on port 8000
- ✅ **Streamlit Frontend**: Running on port 8501
- ✅ **OAuth Configuration**: Google Calendar integration ready
- ✅ **AI Service**: Gemini AI configured and ready
- ✅ **Security**: Token encryption properly set up

## 🎯 Features Available

### 📅 Calendar Integration
- Connect your Google Calendar
- View upcoming events
- Create new meetings
- Check availability

### 🤖 AI Assistant
- Natural language meeting scheduling
- Intelligent conversation handling
- Meeting information extraction
- Smart suggestions

### 🔐 Security
- Secure OAuth 2.0 flow
- Encrypted token storage
- CORS protection
- Input validation

## 🛠️ Configuration Files

- **Environment**: `.env.local` (configured)
- **Dependencies**: `requirements.txt` (installed)
- **Backend Config**: `backend_api/main.py`
- **Frontend Config**: `streamlit_app_fastapi.py`

## 📱 How to Use

1. **Open the frontend**: http://localhost:8501
2. **Connect Google Calendar**: Click "Connect Google Calendar" in the sidebar
3. **Start chatting**: Use natural language to schedule meetings
   - "Schedule a meeting with John tomorrow at 2 PM"
   - "What's my availability this week?"
   - "Show me my meetings for today"

## 🔍 Troubleshooting

### Port Already in Use
If you get port errors, check what's running:
```bash
netstat -an | findstr :8000
netstat -an | findstr :8501
```

### Backend Not Responding
Check if the backend is healthy:
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend Connection Issues
Ensure the backend is running first, then start the frontend.

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Both URLs are accessible
- ✅ Frontend shows "Backend Online" status
- ✅ Google Calendar connection works
- ✅ AI chat responds to messages
- ✅ Health check returns "healthy" status

## 📞 Next Steps

1. **Test the connection**: Try connecting your Google Calendar
2. **Schedule a meeting**: Use natural language to create an event
3. **Explore features**: Check availability, view events, etc.
4. **Customize**: Modify the UI or add new features as needed

---

**🎊 Congratulations! Your Agentic Calendar is now running successfully!**

For detailed setup information, see:
- `FASTAPI_OAUTH_SETUP.md` - OAuth configuration details
- `FINAL_SETUP_GUIDE.md` - Complete setup instructions
- `README.md` - Project overview and documentation
