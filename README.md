# Mailgun DNS Setup

A modern web application for automating Mailgun domain configuration with Cloudflare DNS management.

## Features

- **Automatic Setup**: Connect your Cloudflare account and automatically create all DNS records needed for Mailgun
- **Manual Fallback**: If automatic setup isn't available, get a clear list of DNS records for manual configuration
- **Secure Processing**: API credentials are processed securely and never stored on the server
- **Professional UI**: Clean, modern interface built with Tailwind CSS

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   cd src
   python main.py
   ```

3. **Open in Browser**
   Navigate to `http://localhost:5000`

## API Keys Required

### Mailgun
- Go to Mailgun Dashboard → Settings → API Keys
- Copy your API key (starts with "key-")

### Cloudflare
- Go to Cloudflare Dashboard → My Profile → API Tokens → Global API Key
- Copy your Global API Key and account email

## How It Works

1. **Enter Credentials**: Provide your domain name and API keys
2. **Zone Detection**: The app checks if your domain exists in Cloudflare
3. **Automatic Setup**: If found, DNS records are created automatically
4. **Manual Setup**: If not found, you get a formatted list for manual entry

## Project Structure

```
├── src/
│   ├── main.py              # Flask application entry point
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base template with styling
│   │   ├── index.html       # Landing page
│   │   ├── setup.html       # Configuration form
│   │   ├── automatic_setup.html  # Auto setup progress
│   │   └── manual_setup.html     # Manual setup instructions
│   ├── api/                 # API client modules
│   │   ├── cloudflare_client.py  # Cloudflare API integration
│   │   └── mailgun_client.py     # Mailgun API integration
│   ├── models/              # Data models
│   ├── utils/               # Utility functions
│   └── static/              # Static assets (CSS, JS, images)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Security Notes

- API keys are only used during the setup process
- No credentials are stored permanently
- All communication uses HTTPS
- The application runs locally on your machine