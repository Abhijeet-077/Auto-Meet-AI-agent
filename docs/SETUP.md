# 🛠️ Agentic Calendar - Setup Guide

## Prerequisites

Before setting up Agentic Calendar, ensure you have the following:

### System Requirements
- **Python 3.8 or higher**
- **Git** (for cloning the repository)
- **Internet connection** (for API access)

### Required API Keys
- **Google Cloud Project** with Calendar API enabled
- **Google OAuth 2.0 credentials** (Client ID and Secret)
- **Google Gemini AI API key**

## Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Calendar API
   - Google+ API (for user info)

### 1.2 Create OAuth 2.0 Credentials
1. Navigate to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client IDs**
3. Configure the consent screen if prompted
4. Set application type to **Web application**
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/oauth/callback`
6. Download the credentials JSON file

### 1.3 Get Gemini AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key for later use

## Step 2: Project Installation

### 2.1 Clone Repository
```bash
git clone https://github.com/yourusername/agentic-calendar.git
cd agentic-calendar
```

### 2.2 Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 3: Configuration

### 3.1 Environment Setup
1. Copy the environment template:
   ```bash
   cp .env.template .env.local
   ```

2. Edit `.env.local` with your credentials:
   ```env
   # Google OAuth Configuration
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback

   # Google Gemini AI Configuration
   GEMINI_API_KEY=your_gemini_api_key_here

   # Application Configuration
   API_BASE_URL=http://localhost:8000
   FRONTEND_URL=http://localhost:8501

   # Security Configuration
   ENCRYPTION_KEY=your_encryption_key_here
   ```

### 3.2 Generate Encryption Key
Run this command to generate a secure encryption key:
```bash
python -c "import secrets, base64; print('ENCRYPTION_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Copy the output and replace the `ENCRYPTION_KEY` value in `.env.local`.

## Step 4: Running the Application

### 4.1 Quick Start (Recommended)
```bash
python start_project.py
```

This will start both the backend and frontend services automatically.

### 4.2 Manual Start
If you prefer to start services individually:

**Terminal 1 - Backend:**
```bash
cd backend_api
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app_modern.py --server.port 8501 --server.address localhost
```

## Step 5: Verification

### 5.1 Health Check
Run the system health check:
```bash
python check_status.py
```

You should see:
- ✅ Backend Service: Running on port 8000
- ✅ Frontend Service: Running on port 8501
- ✅ All services configured

### 5.2 Access Application
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Endpoint**: http://localhost:8000/api/v1/health

### 5.3 Test OAuth Flow
1. Open the frontend at http://localhost:8501
2. Click "Connect Google Calendar" in the sidebar
3. Complete the OAuth authorization flow
4. Verify successful connection

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the ports
netstat -an | findstr :8000
netstat -an | findstr :8501

# Kill processes if needed (Windows)
taskkill /F /IM python.exe
```

#### OAuth Errors
- Verify redirect URI matches exactly in Google Cloud Console
- Check that Calendar API is enabled
- Ensure OAuth consent screen is configured

#### API Key Issues
- Verify Gemini API key is correct
- Check API quotas and billing in Google Cloud Console
- Ensure APIs are enabled for your project

#### Environment Variables
- Check `.env.local` file exists and has correct values
- Verify no extra spaces or quotes around values
- Ensure file encoding is UTF-8

### Getting Help

If you encounter issues:
1. Check the [troubleshooting section](TROUBLESHOOTING.md)
2. Review the [FAQ](FAQ.md)
3. Check application logs in the terminal
4. Verify all prerequisites are met

## Next Steps

After successful setup:
1. Read the [Features Guide](FEATURES.md) to understand capabilities
2. Review the [API Documentation](API.md) for integration details
3. Check the [Deployment Guide](DEPLOYMENT.md) for production setup

## Security Notes

- Keep your `.env.local` file secure and never commit it to version control
- Regularly rotate your API keys and encryption keys
- Use HTTPS in production environments
- Review OAuth scopes and permissions regularly

---

**Setup complete!** 🎉 Your Agentic Calendar is ready to use.
