# Agentic Calendar FastAPI OAuth Setup Guide

This guide provides step-by-step instructions for configuring Google OAuth 2.0 for the Agentic Calendar FastAPI backend architecture.

## 🚨 IMPORTANT: OAuth Redirect URI Update Required

**If you're migrating from the old Streamlit-embedded backend to the new FastAPI architecture, you MUST update your Google Cloud Console OAuth configuration.**

### Quick Fix for OAuth Compliance Error

If you're seeing this error:
```
You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy. 
If you're the app developer, register the redirect URI in the Google Cloud Console.
```

**The issue:** Your Google Cloud Console is configured with the old Streamlit redirect URI (`http://localhost:8501`) but the new Agentic Calendar FastAPI backend uses `http://localhost:8000/api/v1/oauth/callback`.

## Step 1: Update Google Cloud Console OAuth Configuration

### 1.1 Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Agentic Calendar project (or create one if needed)
3. Navigate to **APIs & Services** → **Credentials**

### 1.2 Update OAuth 2.0 Client ID
1. Find your existing OAuth 2.0 Client ID for Agentic Calendar
2. Click the **Edit** button (pencil icon)
3. In the **Authorized redirect URIs** section:

#### Remove old URIs (if present):
- `http://localhost:8501`
- `http://localhost:8501/`
- `http://127.0.0.1:8501`
- `http://127.0.0.1:8501/`

#### Add new FastAPI URIs:
- `http://localhost:8000/api/v1/oauth/callback`
- `http://127.0.0.1:8000/api/v1/oauth/callback`

#### For production deployment, also add:
- `https://yourdomain.com/api/v1/oauth/callback`

4. Click **Save**

### 1.3 Verify OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Ensure your app is configured correctly:
   - **App name**: Agentic Calendar
   - **User support email**: Your email
   - **Developer contact information**: Your email
3. In **Test users** section, add your email address if testing

## Step 2: Update Environment Configuration

### 2.1 Update .env.local file
Ensure your `.env.local` file has the correct redirect URI:

```env
# OAuth Configuration
OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### 2.2 Verify FastAPI Backend Configuration
Your FastAPI backend should be configured to run on:
```env
API_HOST=127.0.0.1
API_PORT=8000
API_BASE_URL=http://localhost:8000
```

## Step 3: Start the Application

### 3.1 Start FastAPI Backend
```bash
cd backend_api
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3.2 Start Streamlit Frontend
```bash
streamlit run streamlit_app_fastapi.py --server.port 8501
```

## Step 4: Test OAuth Flow

1. Open the Streamlit frontend at `http://localhost:8501`
2. Click **"Connect Google Calendar"** in the sidebar
3. Click the authorization link
4. Complete Google OAuth flow
5. You should be redirected back to the Streamlit app with successful connection

## Architecture Overview

```
┌─────────────────┐    HTTP API     ┌─────────────────┐    OAuth     ┌─────────────────┐
│   Streamlit     │ ──────────────► │   FastAPI       │ ───────────► │   Google        │
│   Frontend      │                 │   Backend       │              │   OAuth         │
│   :8501         │                 │   :8000         │              │                 │
└─────────────────┘                 └─────────────────┘              └─────────────────┘
                                            │
                                            ▼
                                    /api/v1/oauth/callback
                                    (Redirect URI)
```

## Troubleshooting

### Common Issues

#### 1. "redirect_uri_mismatch" Error
**Cause**: Redirect URI in Google Cloud Console doesn't match the one used by FastAPI
**Solution**: Ensure Google Cloud Console has `http://localhost:8000/api/v1/oauth/callback`

#### 2. "access_blocked" Error  
**Cause**: Your email is not added as a test user
**Solution**: Add your email in OAuth consent screen → Test users

#### 3. Backend Connection Error
**Cause**: FastAPI backend is not running
**Solution**: Start the backend with `uvicorn main:app --reload --host 127.0.0.1 --port 8000`

#### 4. OAuth Not Configured Error
**Cause**: Environment variables not set correctly
**Solution**: Verify `.env.local` has correct `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

### Verification Commands

Check if backend is running:
```bash
curl http://localhost:8000/api/v1/health
```

Check OAuth configuration:
```bash
curl http://localhost:8000/api/v1/oauth/config
```

## Security Notes

- Never commit `.env.local` to version control
- Use strong encryption keys in production
- For production, use HTTPS URLs for all redirect URIs
- Regularly rotate OAuth client secrets

## Next Steps

After successful OAuth setup:
1. Test calendar integration by asking TailorTalk to schedule a meeting
2. Verify events are created in your Google Calendar
3. Check the FastAPI backend logs for any errors

For additional help, see:
- `GOOGLE_OAUTH_SETUP.md` - Detailed Google Cloud setup
- `README.md` - General application setup
- FastAPI docs at `http://localhost:8000/docs`
