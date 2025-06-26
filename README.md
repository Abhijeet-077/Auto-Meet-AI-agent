# 📅 TailorTalk - AI Calendar Assistant

TailorTalk is an intelligent calendar assistant built with Streamlit that helps you schedule appointments using natural language conversation. It integrates with Google Calendar and uses Google's Gemini AI for natural language processing.

## ✨ Features

- **Natural Language Scheduling**: Chat with the AI to schedule appointments using everyday language
- **Google Calendar Integration**: Seamlessly connect to your Google Calendar for real-time availability checking
- **Smart Availability Detection**: Automatically finds free slots in your calendar
- **Event Creation**: Creates calendar events directly from your conversation
- **Beautiful UI**: Clean, modern interface built with Streamlit
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Calendar API enabled
- Gemini API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tailortalk
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**

   Navigate to `http://localhost:8501` to use the application.

## 🔧 Configuration

### Getting API Keys

#### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials
5. Add your domain/localhost to authorized origins
6. Copy the Client ID and Client Secret to your `.env` file

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Gemini AI API key | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Yes |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI (default: http://localhost:8501) | No |

## 🌐 Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Ensure required files are present**
   - `streamlit_app.py` (main application file)
   - `requirements.txt` (Python dependencies)
   - `packages.txt` (system packages, if needed)
   - `.streamlit/config.toml` (Streamlit configuration)
   - `.streamlit/secrets.toml.example` (secrets template)

### Step 2: Set Up Streamlit Cloud

1. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

2. **Sign in with GitHub**

3. **Click "New app"**

4. **Configure your app**
   - Repository: Select your GitHub repository
   - Branch: `main` (or your default branch)
   - Main file path: `streamlit_app.py`
   - App URL: Choose a custom URL (optional)

### Step 3: Configure Secrets

1. **In Streamlit Cloud, go to your app settings**

2. **Click on "Secrets"**

3. **Add your secrets in TOML format**
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"

   [google_oauth]
   client_id = "your_google_client_id_here"
   client_secret = "your_google_client_secret_here"
   redirect_uri = "https://your-app-name.streamlit.app"
   ```

### Step 4: Update Google OAuth Settings

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**

2. **Navigate to APIs & Services > Credentials**

3. **Edit your OAuth 2.0 Client**

4. **Add your Streamlit Cloud URL to Authorized redirect URIs**
   ```
   https://your-app-name.streamlit.app
   ```

5. **Save the changes**

### Step 5: Deploy

1. **Click "Deploy" in Streamlit Cloud**

2. **Wait for deployment to complete**

3. **Test your deployed application**

## 📱 Usage

1. **Open the application** in your browser

2. **Connect Google Calendar**
   - Click "Connect Google Calendar" in the sidebar
   - Authorize the application to access your calendar

3. **Start chatting**
   - Type natural language requests like:
     - "Schedule a meeting tomorrow at 2 PM"
     - "Find me a free slot next week for a 1-hour meeting"
     - "Book a doctor's appointment on Friday morning"

4. **Confirm appointments**
   - The AI will find available slots and ask for confirmation
   - Once confirmed, events are automatically created in your calendar

## 🛠️ Development

### Project Structure

```
tailortalk/
├── streamlit_app.py          # Main Streamlit application
├── backend/
│   ├── gemini_service.py     # Gemini AI integration
│   ├── google_calendar_service.py  # Google Calendar API
│   └── config.py             # Configuration management
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml.example  # Secrets template
├── requirements.txt          # Python dependencies
├── packages.txt             # System packages
├── .env.example             # Environment variables template
└── README.md               # This file
```

### Adding New Features

1. **Extend the Gemini Service** (`backend/gemini_service.py`)
   - Modify prompts for new conversation flows
   - Add new calendar operations

2. **Enhance Calendar Integration** (`backend/google_calendar_service.py`)
   - Add support for multiple calendars
   - Implement recurring events
   - Add meeting room booking

3. **Improve UI** (`streamlit_app.py`)
   - Add new components
   - Enhance styling
   - Add data visualization

## 🔒 Security

- **API Keys**: Never commit API keys to version control
- **OAuth**: Use secure OAuth 2.0 flow for Google Calendar access
- **HTTPS**: Always use HTTPS in production
- **Secrets**: Store sensitive data in Streamlit Cloud secrets or environment variables

## 🐛 Troubleshooting

### Common Issues

1. **"API key not configured" error**
   - Ensure `GEMINI_API_KEY` is set correctly
   - Check if the API key is valid and has proper permissions

2. **Google Calendar connection fails**
   - Verify OAuth credentials are correct
   - Check if Calendar API is enabled in Google Cloud Console
   - Ensure redirect URI matches your deployment URL

3. **Import errors**
   - Run `pip install -r requirements.txt` to install dependencies
   - Check Python version compatibility

4. **Streamlit Cloud deployment fails**
   - Check logs in Streamlit Cloud dashboard
   - Verify all required files are in the repository
   - Ensure secrets are properly configured

### Getting Help

- Check the [Streamlit documentation](https://docs.streamlit.io/)
- Review [Google Calendar API documentation](https://developers.google.com/calendar)
- Visit [Gemini API documentation](https://ai.google.dev/docs)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Google AI](https://ai.google.dev/) for the Gemini API
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration
