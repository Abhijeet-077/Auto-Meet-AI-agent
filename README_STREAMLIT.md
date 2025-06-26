# 🤖 Agentic Calendar - Multi-AI Provider Edition

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

> **AI-Powered Meeting Scheduler with Multi-Provider Support - Choose Your AI!**

## 🌟 NEW: Multi-AI Provider Support

**Choose your preferred AI provider or use them all!**

- 🎯 **Demo Mode** - Works immediately, no setup required
- 🤖 **OpenAI** - GPT-3.5/GPT-4 models
- 🧠 **Google Gemini** - Fast responses with free tier
- 🎭 **Anthropic Claude** - Advanced reasoning capabilities

**Switch between providers instantly while preserving conversation history!**

## 🚀 Quick Deploy to Streamlit Cloud

### One-Click Deployment
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file: `app.py`
6. Deploy!

### Demo Mode (No Setup Required)
The app works immediately with full demo functionality:
- ✅ AI-powered chat interface
- ✅ Meeting scheduling simulation
- ✅ Calendar integration demo
- ✅ OAuth flow simulation
- ✅ Professional UI/UX

## 🎯 Features

### 🤖 Multi-AI Provider System

- **🎯 Demo Mode**: Instant functionality with simulated AI responses
- **🤖 OpenAI Integration**: GPT-3.5 Turbo, GPT-4, GPT-4 Turbo Preview
- **🧠 Google Gemini**: Gemini Pro with generous free tier
- **🎭 Anthropic Claude**: Claude 3 Haiku, Sonnet, Opus models
- **⚡ Instant Switching**: Change providers without losing conversation
- **🔐 Secure Storage**: Encrypted API key management

### 📅 Calendar Integration

- Google Calendar OAuth simulation
- Meeting creation and verification
- Availability checking
- Event management

### 🎨 Modern Interface

- Professional, responsive design
- Real-time provider status indicators
- Interactive AI provider settings
- Mobile-optimized experience

### 🔐 Enterprise Security

- OAuth 2.0 authentication
- Encrypted API key storage
- Secure token management
- Privacy-focused design

## 🛠️ Configuration

### Demo Mode (Default)
No configuration needed! The app works immediately with simulated data.

### Multi-AI Provider Mode (Optional)

Add your preferred AI provider API keys in Streamlit Cloud secrets:

```toml
# Demo mode works without any keys
DEMO_MODE = "true"

# Optional: Add your AI provider keys
OPENAI_API_KEY = "sk-your-openai-key"
GEMINI_API_KEY = "your-gemini-key"
CLAUDE_API_KEY = "your-claude-key"

# Calendar integration (optional)
GOOGLE_CLIENT_ID = "your_client_id"
GOOGLE_CLIENT_SECRET = "your_client_secret"
```

### Quick Setup Guide

1. **Instant Demo**: No setup required - works immediately!
2. **Add AI Provider**: Choose OpenAI, Gemini, or Claude
3. **Get API Key**: Follow provider-specific instructions
4. **Configure in App**: Use sidebar settings or secrets
5. **Start Chatting**: Switch between providers instantly!

📖 **[Full Setup Guide →](docs/MULTI_AI_SETUP.md)**

## 📖 Usage

### For Evaluators
1. Visit the deployed app URL
2. No setup or API keys required
3. Test all features with demo data
4. Full functionality available immediately

### For Developers
1. Clone the repository
2. Deploy to Streamlit Cloud
3. Configure secrets for production use
4. Customize as needed

## 🎓 Academic Ready

Perfect for:
- ✅ Academic submissions
- ✅ Portfolio demonstrations
- ✅ Technical evaluations
- ✅ Professional showcases

## 📁 Project Structure

```
agentic-calendar/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── README.md                # This file
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # Secrets template
└── docs/                    # Documentation
```

## 🚀 Live Demo

**[Try Agentic Calendar Live →](https://your-app-name.streamlit.app)**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on Streamlit Cloud
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- **Streamlit** for the amazing deployment platform
- **Google Cloud** for AI and Calendar APIs
- **Open Source Community** for excellent libraries

---

**Built with ❤️ by [Abhijeet Swami](https://github.com/Abhijeet-077)**

*Ready for Streamlit Cloud deployment!* 🚀
