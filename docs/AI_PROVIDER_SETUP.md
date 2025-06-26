# 🤖 AI Provider Configuration Guide

## Overview

Agentic Calendar supports multiple AI providers, giving you flexibility to choose the best AI service for your needs. You can switch between providers instantly through the sidebar interface.

## Supported AI Providers

### 🎯 Demo Mode (Default)
- **Cost**: Free
- **Setup Time**: 0 minutes
- **Features**: Simulated AI responses for testing and evaluation
- **Best For**: Testing, evaluation, demonstrations

### 🧠 Google Gemini
- **Cost**: Free tier available
- **Setup Time**: 2 minutes
- **Features**: Fast responses, good reasoning
- **Best For**: Free usage, quick responses

### 🤖 OpenAI GPT
- **Cost**: Pay-per-use
- **Setup Time**: 3 minutes
- **Features**: Reliable, widely used, excellent performance
- **Best For**: Production use, consistent quality

### 🎭 Anthropic Claude
- **Cost**: Pay-per-use
- **Setup Time**: 3 minutes
- **Features**: Advanced reasoning, safety-focused
- **Best For**: Complex conversations, detailed responses

## Quick Setup Guide

### Method 1: Using the Sidebar Interface (Recommended)

1. **Open the Application**
   - Navigate to http://localhost:8501
   - Look for the "🤖 AI Provider Settings" section in the sidebar

2. **Select Your Provider**
   - Choose from the dropdown menu
   - Demo Mode requires no setup

3. **Configure API Key** (for non-demo providers)
   - Enter your API key in the secure input field
   - Click "🔍 Test" to validate the key
   - Click "💾 Save & Use" to activate the provider

### Method 2: Environment Variables

Add to your `.env.local` file:

```env
# Choose your preferred AI providers
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

## Getting API Keys

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with "AIza...")

### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with "sk-...")

### Anthropic Claude
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign in to your Anthropic account
3. Navigate to API Keys
4. Create a new key
5. Copy the key (starts with "sk-ant-...")

## Usage Examples

### Switching Providers
1. Open the sidebar
2. Select a different provider from the dropdown
3. Enter the API key if required
4. Click "💾 Save & Use"
5. The change takes effect immediately

### Testing API Keys
1. Select a provider
2. Enter the API key
3. Click "🔍 Test"
4. Wait for validation result

### Demo Mode
- No configuration required
- Provides realistic simulated responses
- Perfect for testing and evaluation
- All features work with mock data

## Troubleshooting

### Common Issues

**"API key is invalid"**
- Double-check the API key format
- Ensure the key hasn't expired
- Verify you have sufficient credits/quota

**"Provider not responding"**
- Check your internet connection
- Verify the API service is operational
- Try switching to Demo Mode temporarily

**"Backend connection failed"**
- Ensure the FastAPI backend is running on port 8000
- Restart the backend: `cd backend_api && uvicorn main:app --reload --host 127.0.0.1 --port 8000`

### Getting Help

1. **Check the Status Dashboard**: Look for service indicators in the main interface
2. **Try Demo Mode**: Switch to demo mode to verify the interface works
3. **Restart Services**: Restart both backend and frontend
4. **Check Logs**: Look at the terminal output for error messages

## Best Practices

### For Development
- Start with Demo Mode for initial testing
- Use Gemini for free development and testing
- Keep API keys secure and never commit them to version control

### For Production
- Use OpenAI or Claude for reliable performance
- Monitor API usage and costs
- Set up proper error handling and fallbacks
- Consider rate limiting for high-traffic applications

### Security
- Store API keys in environment variables
- Use `.env.local` for local development
- Never expose API keys in client-side code
- Rotate API keys regularly

## Provider Comparison

| Feature | Demo | Gemini | OpenAI | Claude |
|---------|------|--------|--------|--------|
| Cost | Free | Free tier | Pay-per-use | Pay-per-use |
| Setup | None | 2 min | 3 min | 3 min |
| Speed | Instant | Fast | Medium | Medium |
| Quality | Simulated | Good | Excellent | Excellent |
| Reasoning | Basic | Good | Very Good | Excellent |
| Safety | N/A | Good | Good | Excellent |

## Advanced Configuration

### Custom Models
Some providers support different models:
- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Claude**: claude-3-haiku, claude-3-sonnet, claude-3-opus
- **Gemini**: gemini-pro, gemini-1.5-flash

### Environment Variables
```env
# Advanced configuration
OPENAI_MODEL=gpt-4
CLAUDE_MODEL=claude-3-sonnet-20240229
GEMINI_MODEL=gemini-1.5-flash
```

## Support

For additional help:
- Check the main documentation in the `docs/` folder
- Review the troubleshooting guide
- Test with Demo Mode first to isolate issues
