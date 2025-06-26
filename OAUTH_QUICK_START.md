# Google Calendar OAuth Quick Start Guide

This is a simplified guide to get Google Calendar OAuth working quickly.

## Prerequisites

- Python 3.7+
- TailorTalk application
- Google account

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API:
   - Go to "APIs & Services" → "Library"
   - Search "Google Calendar API" → Enable

### 3. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URI: `http://localhost:8501`
5. Copy your Client ID and Client Secret

### 4. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" → Fill required fields:
   - App name: `TailorTalk`
   - User support email: Your email
   - Developer contact: Your email
3. Add scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`
4. Add yourself as a test user

### 5. Configure Application

Run the setup script:

```bash
python setup_oauth.py
```

Or manually update `.env.local`:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=http://localhost:8501
```

### 6. Test the Integration

```bash
streamlit run streamlit_app.py
```

1. Open the application in your browser
2. Go to the Google Calendar section
3. Click "Connect Google Calendar"
4. Complete the OAuth flow

## Troubleshooting

### Common Issues

**"redirect_uri_mismatch"**
- Ensure redirect URI in Google Cloud Console exactly matches: `http://localhost:8501`

**"access_blocked"**
- Add yourself as a test user in OAuth consent screen
- Make sure app is in "Testing" mode

**"invalid_client"**
- Double-check Client ID and Client Secret in `.env.local`

**"OAuth not configured"**
- Run `python setup_oauth.py --check` to verify setup
- Ensure all required packages are installed

### Debug Mode

Enable debug mode in `.env.local`:

```env
DEBUG_MODE=true
```

This will show additional information about the OAuth flow.

### Getting Help

1. Check the full setup guide: `GOOGLE_OAUTH_SETUP.md`
2. Verify configuration: `python setup_oauth.py --check`
3. Check Streamlit logs for error details

## Security Notes

- Never commit `.env.local` to version control
- Rotate your client secret regularly
- Use HTTPS in production
- Keep your encryption key secure

## Production Deployment

For production:

1. Update redirect URI to your domain
2. Submit app for verification (if needed)
3. Move OAuth consent screen to "In production"
4. Use secure environment variable management

## Next Steps

Once OAuth is working:

1. Test calendar operations (read events, create events)
2. Integrate with your AI assistant
3. Add error handling for your specific use cases
4. Consider implementing refresh token rotation

## Support

If you encounter issues:

1. Check Google Cloud Console error logs
2. Verify all steps in this guide
3. Ensure your development server is running on port 8501
4. Check that all required scopes are configured
