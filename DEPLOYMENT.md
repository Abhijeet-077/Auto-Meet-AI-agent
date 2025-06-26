# 🚀 TailorTalk Deployment Guide

This guide provides detailed step-by-step instructions for deploying TailorTalk to Streamlit Cloud.

## 📋 Pre-Deployment Checklist

### ✅ Required Files
- [ ] `streamlit_app.py` - Main application file
- [ ] `requirements.txt` - Python dependencies
- [ ] `packages.txt` - System packages (if needed)
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `.streamlit/secrets.toml.example` - Secrets template
- [ ] `README.md` - Documentation
- [ ] `backend/` directory with all service files

### ✅ API Keys and Credentials
- [ ] Gemini API key obtained from Google AI Studio
- [ ] Google Cloud Project created
- [ ] Google Calendar API enabled
- [ ] OAuth 2.0 credentials created
- [ ] Client ID and Client Secret obtained

### ✅ Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository is public or accessible to Streamlit Cloud
- [ ] All sensitive data removed from code
- [ ] `.env` files added to `.gitignore`

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Google Cloud Project

1. **Create or Select Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Note the project ID

2. **Enable APIs**
   - Navigate to "APIs & Services" > "Library"
   - Search for and enable:
     - Google Calendar API
     - Google+ API (for user info)

3. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized origins:
     - `http://localhost:8501` (for local testing)
     - `https://your-app-name.streamlit.app` (replace with your app URL)
   - Add authorized redirect URIs:
     - `http://localhost:8501` (for local testing)
     - `https://your-app-name.streamlit.app` (replace with your app URL)
   - Save and note the Client ID and Client Secret

### Step 2: Get Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Choose your Google Cloud project
   - Copy the generated API key

### Step 3: Deploy to Streamlit Cloud

1. **Access Streamlit Cloud**
   - Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository
   - Choose branch (usually `main`)
   - Set main file path: `streamlit_app.py`
   - Choose a custom app URL (optional)

3. **Configure Secrets**
   - In the app settings, click "Secrets"
   - Add the following in TOML format:
   ```toml
   GEMINI_API_KEY = "AIzaSyBn-kcJcmzPzxqmu4U-nAQXpUiWa9XRWCQ"

   [google_oauth]
   client_id = "your_actual_google_client_id"
   client_secret = "your_actual_google_client_secret"
   redirect_uri = "https://your-actual-app-url.streamlit.app"

   # Optional: Enhanced security with token encryption
   encryption_key = "your_base64_encryption_key_here"
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete
   - Monitor logs for any errors

### Step 4: Update OAuth Settings

1. **Return to Google Cloud Console**
   - Go to "APIs & Services" > "Credentials"
   - Edit your OAuth 2.0 Client

2. **Update Authorized URIs**
   - Add your actual Streamlit Cloud URL to:
     - Authorized JavaScript origins
     - Authorized redirect URIs
   - Format: `https://your-app-name.streamlit.app`

3. **Save Changes**

### Step 5: Test Deployment

1. **Access Your App**
   - Open your Streamlit Cloud URL
   - Verify the app loads correctly

2. **Test Google Calendar Connection**
   - Click "Connect Google Calendar"
   - Complete OAuth flow
   - Verify connection status

3. **Test AI Functionality**
   - Send a test message
   - Verify Gemini AI responds correctly

4. **Test Calendar Operations**
   - Try scheduling a test appointment
   - Verify calendar integration works

## 🔍 Troubleshooting

### Common Deployment Issues

1. **App Won't Start**
   - Check Streamlit Cloud logs
   - Verify all dependencies in `requirements.txt`
   - Check for syntax errors in code

2. **Import Errors**
   - Ensure all custom modules are in the repository
   - Check file paths and imports
   - Verify Python version compatibility

3. **API Key Issues**
   - Verify secrets are correctly formatted in TOML
   - Check API key validity
   - Ensure no extra spaces or characters

4. **OAuth Errors**
   - Verify redirect URIs match exactly
   - Check client ID and secret
   - Ensure Calendar API is enabled

### Performance Optimization

1. **Caching**
   - Use `@st.cache_data` for expensive operations
   - Cache API responses when appropriate

2. **Resource Management**
   - Minimize API calls
   - Use session state efficiently
   - Optimize imports

3. **Error Handling**
   - Add comprehensive error handling
   - Provide user-friendly error messages
   - Log errors for debugging

## 📊 Monitoring and Maintenance

### Health Checks
- [ ] App loads without errors
- [ ] All features work as expected
- [ ] API integrations are functional
- [ ] Performance is acceptable

### Regular Maintenance
- [ ] Update dependencies regularly
- [ ] Monitor API usage and quotas
- [ ] Review and rotate API keys
- [ ] Check for security updates

### Scaling Considerations
- [ ] Monitor app usage and performance
- [ ] Consider caching strategies
- [ ] Plan for increased API quotas if needed
- [ ] Consider database integration for user data

## 🆘 Support

If you encounter issues during deployment:

1. **Check Logs**
   - Streamlit Cloud app logs
   - Browser developer console
   - Google Cloud Console logs

2. **Verify Configuration**
   - Double-check all API keys and secrets
   - Verify OAuth settings
   - Confirm all required files are present

3. **Test Locally First**
   - Ensure the app works locally
   - Test all integrations locally
   - Debug issues in development environment

4. **Community Resources**
   - Streamlit Community Forum
   - Stack Overflow
   - Google Cloud Support

## ✅ Post-Deployment Checklist

- [ ] App is accessible at the deployed URL
- [ ] Google Calendar connection works
- [ ] AI chat functionality works
- [ ] Calendar operations (create events) work
- [ ] Error handling works properly
- [ ] Performance is acceptable
- [ ] Security settings are configured
- [ ] Monitoring is set up
- [ ] Documentation is updated
