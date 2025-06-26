# 🤖 Multi-AI Provider Configuration Guide

## Overview

Agentic Calendar now supports multiple AI providers, giving you the flexibility to choose your preferred AI service and use your own API quotas. The application seamlessly switches between providers while maintaining full functionality and conversation history.

## 🎯 Supported AI Providers

### 1. **🎯 Demo Mode** (Default)
- **Description**: Simulated AI responses for evaluation
- **API Key Required**: No
- **Cost**: Free
- **Use Case**: Academic evaluation, testing, demonstrations

### 2. **🤖 OpenAI** 
- **Models**: GPT-3.5 Turbo, GPT-4, GPT-4 Turbo Preview
- **API Key Required**: Yes
- **Cost**: Pay-per-use
- **Strengths**: Excellent general conversation, reliable responses
- **Get API Key**: [OpenAI API Keys](https://platform.openai.com/api-keys)

### 3. **🧠 Google Gemini**
- **Models**: Gemini Pro, Gemini Pro Vision
- **API Key Required**: Yes
- **Cost**: Generous free tier, then pay-per-use
- **Strengths**: Fast responses, good reasoning, free tier
- **Get API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4. **🎭 Anthropic Claude**
- **Models**: Claude 3 Haiku, Sonnet, Opus
- **API Key Required**: Yes
- **Cost**: Pay-per-use
- **Strengths**: Excellent reasoning, safety-focused, detailed responses
- **Get API Key**: [Anthropic Console](https://console.anthropic.com/)

## 🔧 Configuration Methods

### Method 1: Streamlit Cloud Secrets (Recommended for Deployment)

Add to your Streamlit Cloud app secrets:

```toml
# Demo mode (works without any API keys)
DEMO_MODE = "true"

# Optional: Add your preferred AI provider API keys
OPENAI_API_KEY = "sk-your-openai-key-here"
GEMINI_API_KEY = "your-gemini-key-here"
CLAUDE_API_KEY = "your-claude-key-here"

# Security
ENCRYPTION_KEY = "your-encryption-key-here"
```

### Method 2: Local Secrets File

Update `.streamlit/secrets.toml`:

```toml
# Multi-AI Provider Configuration
DEMO_MODE = "true"
OPENAI_API_KEY = "your-openai-key-here"
GEMINI_API_KEY = "your-gemini-key-here"
CLAUDE_API_KEY = "your-claude-key-here"
ENCRYPTION_KEY = "your-encryption-key-here"
```

### Method 3: Runtime Configuration (In-App)

Use the sidebar settings panel to:
1. Select your preferred AI provider
2. Enter API keys securely
3. Test API key validity
4. Switch providers instantly

## 🎮 How to Use

### Getting Started

1. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

2. **Access AI Provider Settings**
   - Look for the "🤖 AI Provider Settings" section in the sidebar
   - Choose your preferred provider from the dropdown

3. **Configure API Keys** (Optional)
   - Enter your API key in the secure input field
   - Click "🔍 Test" to validate the key
   - Click "💾 Save & Use" to activate the provider

4. **Start Chatting**
   - The chat interface shows which provider is active
   - All features work identically across providers
   - Conversation history is preserved when switching

### Provider Switching

#### Quick Switch
- Use the "⚡ Quick Switch" buttons in the sidebar
- Instantly switch between configured providers
- Conversation history is maintained

#### Full Configuration
- Select provider from dropdown
- Configure model selection (where available)
- Test and save API keys
- Switch with full control

## 🔐 Security Features

### Secure API Key Storage
- **Encryption**: API keys are encrypted using Fernet encryption
- **Session-Based**: Keys stored securely in Streamlit session state
- **No Persistence**: Keys don't persist between sessions (by design)
- **Fallback**: Graceful handling when encryption is unavailable

### Privacy Protection
- **Local Processing**: API keys never leave your environment
- **No Logging**: Sensitive data is not logged
- **Secure Transmission**: HTTPS for all API communications
- **Clear Function**: Easy way to clear all stored keys

## 🎯 Demo Mode Benefits

### Zero Configuration
- **Immediate Functionality**: Works without any setup
- **Full Feature Set**: All features available with simulated data
- **Academic Ready**: Perfect for evaluations and demonstrations
- **No Costs**: Completely free to use

### Realistic Simulation
- **Intelligent Responses**: Context-aware simulated AI responses
- **Meeting Scheduling**: Creates realistic demo calendar events
- **Calendar Integration**: Shows sample calendar data
- **OAuth Simulation**: Demonstrates authentication flow

## 🚀 Advanced Features

### Conversation Preservation
- **History Maintained**: Chat history preserved across provider switches
- **Context Aware**: Providers receive conversation context
- **Seamless Experience**: No interruption when switching providers

### Error Handling & Fallbacks
- **Automatic Fallback**: Falls back to demo mode on API errors
- **Detailed Error Messages**: Clear feedback on API issues
- **Rate Limit Handling**: Graceful handling of API limits
- **Quota Management**: Clear messages for quota exceeded scenarios

### Provider Status Monitoring
- **Real-time Status**: Live provider status indicators
- **Connection Health**: API key validation and health checks
- **Usage Feedback**: Clear indication of active provider
- **Quick Diagnostics**: Easy troubleshooting information

## 📊 Provider Comparison

| Feature | Demo Mode | OpenAI | Gemini | Claude |
|---------|-----------|---------|---------|---------|
| **Cost** | Free | Pay-per-use | Free tier + Pay | Pay-per-use |
| **Setup** | None | API Key | API Key | API Key |
| **Speed** | Instant | Fast | Very Fast | Fast |
| **Quality** | Simulated | Excellent | Very Good | Excellent |
| **Models** | N/A | Multiple | Multiple | Multiple |
| **Free Tier** | ✅ | ❌ | ✅ | ❌ |

## 🛠️ Troubleshooting

### Common Issues

#### API Key Not Working
1. **Verify Key Format**: Ensure correct API key format
2. **Check Permissions**: Verify API key has required permissions
3. **Test Connection**: Use the "🔍 Test" button
4. **Check Quotas**: Ensure you have available API credits

#### Provider Not Switching
1. **Save Configuration**: Click "💾 Save & Use" after entering key
2. **Refresh Page**: Sometimes requires a page refresh
3. **Check Console**: Look for error messages in browser console
4. **Clear Cache**: Clear browser cache if issues persist

#### Demo Mode Stuck
1. **Check API Keys**: Ensure valid API keys are configured
2. **Manual Switch**: Use provider selection dropdown
3. **Clear Keys**: Use "🗑️ Clear All API Keys" and reconfigure
4. **Restart App**: Restart the Streamlit application

### Error Messages

#### "Invalid API Key"
- **Cause**: API key is incorrect or expired
- **Solution**: Get a new API key from the provider's console

#### "Rate Limit Exceeded"
- **Cause**: Too many requests to the API
- **Solution**: Wait a few minutes or upgrade your API plan

#### "Quota Exceeded"
- **Cause**: API usage limits reached
- **Solution**: Add billing information or wait for quota reset

## 🎓 Best Practices

### For Academic Use
1. **Start with Demo Mode**: Perfect for evaluations
2. **Document Provider Used**: Note which AI provider for submissions
3. **Test All Features**: Verify functionality across providers
4. **Keep Fallback**: Always have demo mode as backup

### For Production Use
1. **Multiple Providers**: Configure multiple providers for redundancy
2. **Monitor Usage**: Keep track of API usage and costs
3. **Error Handling**: Implement proper error handling
4. **Security**: Use environment variables for API keys

### For Development
1. **Test Locally**: Test with demo mode first
2. **Gradual Rollout**: Add one provider at a time
3. **Monitor Performance**: Compare response times and quality
4. **User Feedback**: Collect feedback on provider preferences

## 🌟 Benefits Summary

### For Users
- ✅ **Choice**: Select your preferred AI provider
- ✅ **Cost Control**: Use your own API quotas
- ✅ **Quality**: Access to latest AI models
- ✅ **Reliability**: Multiple fallback options
- ✅ **Privacy**: Your API keys, your control

### For Developers
- ✅ **Flexibility**: Easy to add new providers
- ✅ **Maintainability**: Clean, modular architecture
- ✅ **Scalability**: Handles multiple providers efficiently
- ✅ **Robustness**: Comprehensive error handling
- ✅ **Security**: Encrypted key storage

### For Evaluators
- ✅ **No Setup**: Demo mode works immediately
- ✅ **Full Testing**: All features available for evaluation
- ✅ **Realistic**: High-quality simulated responses
- ✅ **Reliable**: No dependency on external APIs
- ✅ **Professional**: Production-quality implementation

---

**🎊 Enjoy the flexibility of multi-AI provider support in Agentic Calendar!**

*Built with excellence by [Abhijeet Swami](https://github.com/Abhijeet-077)* ✨
