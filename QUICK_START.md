# 🚀 TailorTalk Quick Start Guide

Get your TailorTalk AI Calendar Assistant up and running in minutes!

## 🎯 What You'll Need

- Python 3.8+ installed
- Google account
- 10 minutes of your time

## ⚡ Local Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Your API Keys

**Gemini API Key (2 minutes):**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

**Google Calendar API (3 minutes):**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials
5. Add `http://localhost:8501` to authorized origins
6. Copy Client ID and Client Secret

### 3. Configure Environment
Edit `.env.local` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### 4. Run the App
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser!

## 🌐 Deploy to Streamlit Cloud (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app.py`

### 3. Add Secrets
In Streamlit Cloud app settings > Secrets:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"

[google_oauth]
client_id = "your_google_client_id_here"
client_secret = "your_google_client_secret_here"
redirect_uri = "https://your-app-name.streamlit.app"
```

### 4. Update Google OAuth
1. Return to Google Cloud Console
2. Edit OAuth credentials
3. Add your Streamlit Cloud URL to authorized origins
4. Save changes

### 5. Test Your App
Visit your deployed app URL and test the calendar connection!

## 🎉 You're Done!

Your TailorTalk AI Calendar Assistant is now live and ready to help schedule appointments!

## 💡 Quick Tips

- **First Time Setup**: Connect your Google Calendar using the sidebar button
- **Natural Language**: Try "Schedule a meeting tomorrow at 2 PM"
- **Availability**: Ask "When am I free next week?"
- **Confirmation**: The AI will always ask before creating events

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting
- Ensure all API keys are correctly configured

## 🔧 Common Issues

**"API key not configured"**
→ Check your `.env.local` file or Streamlit Cloud secrets

**"Calendar connection failed"**
→ Verify OAuth credentials and authorized URIs

**"Import errors"**
→ Run `pip install -r requirements.txt`

Happy scheduling! 📅✨
