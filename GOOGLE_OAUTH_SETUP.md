# Google Calendar OAuth 2.0 Setup Guide

This guide will walk you through setting up Google Calendar OAuth 2.0 integration for TailorTalk.

## Prerequisites

- Google account
- Access to Google Cloud Console
- TailorTalk application running locally

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `tailortalk-calendar` (or your preferred name)
4. Click "Create"

## Step 2: Enable Google Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on "Google Calendar API"
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type (unless you have Google Workspace)
3. Click "Create"

### Fill out the OAuth consent screen:

**App Information:**
- App name: `TailorTalk`
- User support email: Your email address
- App logo: (Optional) Upload your app logo

**App domain:**
- Application home page: `http://localhost:8501` (for Streamlit)
- Application privacy policy link: (Optional)
- Application terms of service link: (Optional)

**Authorized domains:**
- Add: `localhost`

**Developer contact information:**
- Email addresses: Your email address

4. Click "Save and Continue"

### Scopes:
1. Click "Add or Remove Scopes"
2. Add these scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
3. Click "Update" → "Save and Continue"

### Test Users (for development):
1. Add your email address as a test user
2. Click "Save and Continue"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Name: `TailorTalk Web Client`

### Authorized redirect URIs:
Add these URIs for different development scenarios:

**For Streamlit (Python backend):**
- `http://localhost:8501`
- `http://localhost:8501/`
- `http://127.0.0.1:8501`
- `http://127.0.0.1:8501/`

**For React development server:**
- `http://localhost:3000`
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

5. Click "Create"

## Step 5: Download Credentials

1. After creating, you'll see your Client ID and Client Secret
2. **IMPORTANT**: Copy these values immediately
3. Optionally, download the JSON file for backup

## Step 6: Update Environment Variables

Update your `.env.local` file with the credentials:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
```

## Step 7: Security Notes

- **Never commit your client secret to version control**
- Add `.env.local` to your `.gitignore` file
- For production, use environment variables or secure secret management
- Regularly rotate your client secret

## Step 8: Testing the Setup

1. Start your application: `streamlit run streamlit_app.py`
2. Navigate to the Google Calendar connection section
3. Click "Connect Google Calendar"
4. You should be redirected to Google's OAuth consent screen
5. Grant permissions and verify the connection works

## Troubleshooting

### Common Issues:

1. **"redirect_uri_mismatch" error:**
   - Ensure your redirect URI exactly matches what's configured in Google Cloud Console
   - Check for trailing slashes and http vs https

2. **"access_blocked" error:**
   - Make sure your app is in testing mode and you're added as a test user
   - Verify all required scopes are added

3. **"invalid_client" error:**
   - Double-check your Client ID and Client Secret
   - Ensure they're correctly set in environment variables

4. **Scope errors:**
   - Verify you've enabled the Google Calendar API
   - Check that required scopes are configured in OAuth consent screen

## Production Deployment

For production deployment:
1. Submit your app for verification (if needed)
2. Move from "Testing" to "In production" in OAuth consent screen
3. Use secure environment variable management
4. Update redirect URIs to your production domain

## Support

If you encounter issues:
1. Check the Google Cloud Console error logs
2. Verify all steps in this guide
3. Ensure your local development server is running on the correct port
