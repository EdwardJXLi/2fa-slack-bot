# Slack 2FA Token Generator

A simple Slack app that generates 2FA tokens on demand directly within Slack using the `/2fa` command. The app supports multiple services and delivers tokens privately to the requesting user.

## Features

- Generate TOTP (Time-based One-Time Password) tokens directly in Slack
- Support for multiple services configured through environment variables
- Private responses (only visible to the requesting user)
- Easy to deploy locally or with Docker
- Lightweight and minimal dependencies

## How It Works

Users can trigger the app by typing `/2fa [service_name]` in any Slack channel where the app is installed. For example:

- `/2fa` - Lists all available services
- `/2fa github` - Generates a token for GitHub
- `/2fa email` - Generates a token for Email

The app looks for environment variables with the prefix `2FA_TOKEN_` (like `2FA_TOKEN_GITHUB`, `2FA_TOKEN_EMAIL`) and uses those secrets to generate the appropriate TOTP codes.

## Installation

### Prerequisites

- A Slack workspace where you can create apps
- Slack Bot Token and App Token
- Your TOTP secrets for each service you want to include

### Local Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/slack-2fa-app.git
cd slack-2fa-app
```

2. **Create and activate a virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install slack-bolt pyotp python-dotenv
```

3. **Create a Slack App**

   a. Go to https://api.slack.com/apps and click "Create New App"
   b. Choose "From scratch" and provide a name and workspace
   c. Navigate to "Socket Mode" and enable it
   d. Generate an app-level token with `connections:write` scope
   e. Go to "OAuth & Permissions" and add these Bot Token Scopes:
      - `commands`
      - `chat:write`
   f. Install the app to your workspace
   g. Create a slash command `/2fa` under the "Slash Commands" section

4. **Configure environment variables**

Create a `.env` file with your tokens and 2FA secrets:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
2FA_TOKEN_GITHUB=your-github-totp-secret
2FA_TOKEN_EMAIL=your-email-totp-secret
2FA_TOKEN_AWS=your-aws-totp-secret
# Add more services as needed
```

6. **Run the application**

```bash
# Make sure your virtual environment is activated
python app.py
```

### Docker Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/slack-2fa-app.git
cd slack-2fa-app
```

2. **Create your .env file** with the same content as in the local installation

3. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

4. **Check logs**

```bash
docker-compose logs -f
```

## Adding New Services

To add a new 2FA service:

1. Get the TOTP secret for the service (usually shown as a QR code or text during 2FA setup)
2. Add a new environment variable in your `.env` file with the pattern `2FA_TOKEN_SERVICENAME=your-secret`
3. Restart the app

The new service will be automatically detected and available via `/2fa servicename`.
