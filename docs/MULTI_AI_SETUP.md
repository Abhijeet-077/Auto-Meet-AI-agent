# 🚀 Quick Multi-AI Provider Setup

## 🎯 Instant Setup (No API Keys Required)

**The app works immediately with Demo Mode!** Just run:

```bash
streamlit run app.py
```

All features are available with simulated AI responses - perfect for evaluation and testing.

## ⚡ 5-Minute Setup with Real AI

### Step 1: Choose Your AI Provider

Pick one or more providers based on your needs:

| Provider | Best For | Cost | Setup Time |
|----------|----------|------|------------|
| 🎯 **Demo Mode** | Evaluation, Testing | Free | 0 minutes |
| 🧠 **Google Gemini** | Free tier, Fast responses | Free tier | 2 minutes |
| 🤖 **OpenAI** | Reliable, Popular | Pay-per-use | 3 minutes |
| 🎭 **Claude** | Advanced reasoning | Pay-per-use | 3 minutes |

### Step 2: Get API Keys (Optional)

#### For Google Gemini (Recommended - Free Tier)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key

#### For OpenAI
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### For Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create account
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key

### Step 3: Configure in App

1. **Launch the app**: `streamlit run app.py`
2. **Open sidebar**: Look for "🤖 AI Provider Settings"
3. **Select provider**: Choose from dropdown
4. **Enter API key**: Paste in the secure input field
5. **Test & Save**: Click "🔍 Test" then "💾 Save & Use"

## 🎮 Usage Examples

### Quick Demo (0 setup)
```bash
# Just run the app - works immediately!
streamlit run app.py
# Chat with simulated AI responses
```

### With Google Gemini (Free tier)
1. Get API key from Google AI Studio
2. Enter in sidebar settings
3. Enjoy free AI-powered conversations!

### Multiple Providers
1. Configure multiple API keys
2. Switch between providers instantly
3. Compare responses from different AIs

## 🔧 Streamlit Cloud Deployment

### Secrets Configuration
Add to your Streamlit Cloud app secrets:

```toml
# Works immediately with demo mode
DEMO_MODE = "true"

# Optional: Add your API keys
GEMINI_API_KEY = "your-gemini-key"
OPENAI_API_KEY = "your-openai-key"
CLAUDE_API_KEY = "your-claude-key"
```

### One-Click Deploy
1. Fork the repository
2. Deploy to Streamlit Cloud
3. Add secrets (optional)
4. App works immediately!

## 🎯 For Academic Evaluation

### Zero Setup Required
- ✅ **Demo Mode**: Full functionality without API keys
- ✅ **All Features**: Meeting scheduling, calendar integration, AI chat
- ✅ **Realistic Data**: High-quality simulated responses
- ✅ **Professional UI**: Production-ready interface

### Evaluation Checklist
- [ ] App launches successfully
- [ ] Demo mode indicator visible
- [ ] AI chat responds intelligently
- [ ] Meeting scheduling works
- [ ] Calendar integration functional
- [ ] Provider switching available
- [ ] All features accessible

## 🚨 Troubleshooting

### App Won't Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

### API Key Issues
1. **Invalid Key**: Double-check the API key format
2. **No Credits**: Ensure your API account has credits
3. **Rate Limits**: Wait a few minutes between requests

### Demo Mode Stuck
- Demo mode is the default and works perfectly for evaluation
- To use real AI, configure API keys in sidebar settings

## 💡 Pro Tips

### For Best Experience
1. **Start with Demo**: Test all features first
2. **Try Gemini**: Free tier with good quality
3. **Compare Providers**: See which you prefer
4. **Keep Demo**: Always available as fallback

### For Development
1. **Local Testing**: Use demo mode for development
2. **Environment Variables**: Store API keys securely
3. **Error Handling**: App gracefully handles API failures
4. **Provider Switching**: Test switching between providers

## 🌟 What You Get

### Immediate Benefits
- ✅ **Zero Setup**: Works out of the box
- ✅ **Multiple AIs**: Choose your preferred provider
- ✅ **Cost Control**: Use your own API quotas
- ✅ **Full Features**: Complete calendar assistant functionality
- ✅ **Professional Quality**: Production-ready application

### Advanced Features
- ✅ **Secure Storage**: Encrypted API key management
- ✅ **Provider Switching**: Instant switching between AIs
- ✅ **Conversation History**: Preserved across provider changes
- ✅ **Error Handling**: Graceful fallbacks and error messages
- ✅ **Status Monitoring**: Real-time provider status indicators

---

**🎊 Ready to experience multi-AI powered calendar assistance!**

**Questions?** Check the [Full Documentation](docs/MULTI_AI_PROVIDER_GUIDE.md)

*Built with ❤️ by [Abhijeet Swami](https://github.com/Abhijeet-077)* ✨
