# 🚨 Streamlit Cloud Deployment Troubleshooting Guide

## 🔍 **Step-by-Step Deployment Fix**

### **Option 1: Minimal Configuration (Recommended)**

1. **Replace your current files with these minimal versions:**

   **Replace `requirements.txt` with:**
   ```
   streamlit
   google-generativeai
   requests
   ```

   **Replace `packages.txt` with:**
   ```
   # Empty packages.txt - no system packages required
   ```

   **Use the minimal app file:**
   - Rename `streamlit_app.py` to `streamlit_app_backup.py`
   - Rename `streamlit_app_minimal.py` to `streamlit_app.py`

2. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Minimal deployment configuration"
   git push origin main
   ```

3. **Deploy to Streamlit Cloud:**
   - Go to your Streamlit Cloud app
   - Click "Reboot app" or redeploy
   - Monitor the deployment logs

### **Option 2: Fix Current Configuration**

If you want to keep the full version, try these fixes:

1. **Update `packages.txt` to minimal:**
   ```
   libffi-dev
   libssl-dev
   ```

2. **Update `requirements.txt` to minimal:**
   ```
   streamlit
   google-api-python-client
   google-auth
   google-auth-oauthlib
   google-generativeai
   python-dotenv
   requests
   pytz
   cryptography
   ```

3. **Add error handling to imports in `streamlit_app.py`:**
   ```python
   try:
       from backend.gemini_service import GeminiService
       from backend.google_calendar_service import GoogleCalendarService
       from backend.oauth_handler import GoogleOAuthHandler
   except ImportError as e:
       st.error(f"Import error: {e}")
       st.stop()
   ```

### **Option 3: No packages.txt**

Sometimes Streamlit Cloud works better without any system packages:

1. **Delete or rename `packages.txt`:**
   ```bash
   mv packages.txt packages.txt.backup
   ```

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Remove packages.txt"
   git push origin main
   ```

## 🔧 **Common Deployment Errors & Solutions**

### **Error: "Unable to locate package"**
- **Solution**: Use minimal `packages.txt` or remove it entirely
- **Files to update**: `packages.txt`, `requirements.txt`

### **Error: "ModuleNotFoundError"**
- **Solution**: Check import statements and module structure
- **Fix**: Use absolute imports instead of relative imports

### **Error: "Package installation failed"**
- **Solution**: Simplify `requirements.txt` to essential packages only
- **Remove**: Version constraints that might conflict

### **Error: "Build failed"**
- **Solution**: Use the minimal single-file version
- **File**: `streamlit_app_minimal.py`

## 📋 **Deployment Checklist**

### **Before Deploying:**
- [ ] Minimal `requirements.txt` (3-5 packages max)
- [ ] Minimal or no `packages.txt`
- [ ] Single file app or proper import handling
- [ ] Secrets configured in Streamlit Cloud
- [ ] Repository pushed to GitHub

### **Streamlit Cloud Secrets:**
```toml
GEMINI_API_KEY = "AIzaSyBn-kcJcmzPzxqmu4U-nAQXpUiWa9XRWCQ"
```

### **After Deploying:**
- [ ] Check deployment logs for errors
- [ ] Test basic functionality
- [ ] Verify Gemini AI works
- [ ] Test chat interface

## 🎯 **Recommended Deployment Strategy**

1. **Start with minimal version** (`streamlit_app_minimal.py`)
2. **Use minimal requirements** (streamlit, google-generativeai, requests)
3. **No packages.txt** or minimal system packages
4. **Test deployment** and verify it works
5. **Gradually add features** once basic deployment works

## 🚀 **Quick Fix Commands**

```bash
# Option 1: Use minimal files
cp streamlit_app_minimal.py streamlit_app.py
cp requirements_minimal.txt requirements.txt
rm packages.txt

# Option 2: Backup and simplify
mv streamlit_app.py streamlit_app_full.py
mv requirements.txt requirements_full.txt
mv packages.txt packages_backup.txt

# Create minimal versions
echo "streamlit" > requirements.txt
echo "google-generativeai" >> requirements.txt
echo "requests" >> requirements.txt

# Commit and push
git add .
git commit -m "Minimal deployment configuration"
git push origin main
```

## 📞 **If Still Failing**

1. **Check Streamlit Cloud logs** for specific error messages
2. **Try deploying with just Streamlit** (remove all other dependencies)
3. **Use a completely fresh repository** with minimal code
4. **Contact Streamlit Cloud support** with specific error logs

## ✅ **Success Indicators**

- Deployment completes without errors
- App loads in browser
- Gemini AI responds to messages
- No import or dependency errors in logs

---

**🎯 Recommendation: Start with Option 1 (Minimal Configuration) for guaranteed deployment success!**
