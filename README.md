# Mailgun DNS Setup

A modern web application for automating Mailgun domain configuration with Cloudflare DNS management.

## Features

- **Automatic Setup**: Connect your Cloudflare account and automatically create all DNS records needed for Mailgun
- **Manual Fallback**: If automatic setup isn't available, get a clear list of DNS records for manual configuration
- **Secure Processing**: API credentials are processed securely and never stored on the server
- **Professional UI**: Clean, modern interface built with Tailwind CSS

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd automatic-mailgun
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Open in Browser**
   Navigate to `http://localhost:5000`

### Option 2: Local Python Installation

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

### Option 3: Using Pre-built Docker Image

```bash
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/automatic-mailgun:latest
```

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
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore file
├── DOCKER.md               # Docker and deployment guide
├── DEVELOPMENT.md          # Developer extension guide
└── README.md               # This file
```

## Docker Deployment

### Building the Image
```bash
docker build -t automatic-mailgun .
```

### Running the Container
```bash
docker run -p 5000:5000 automatic-mailgun
```

### Using Docker Compose
```bash
docker-compose up --build
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `SECRET_KEY`: Flask secret key for session security
- `FLASK_ENV`: Set to `production` for production deployments
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to bind to (default: 5000)

## CI/CD

This project includes GitHub Actions workflows for:
- **Testing**: Runs on every push and pull request
- **Docker Build**: Tests Docker image builds
- **Release**: Publishes to GitHub Container Registry (ghcr.io) on new tags

To trigger a release:
1. Create a new tag: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. Create a GitHub release from the tag
```

## Security Notes

- API keys are only used during the setup process
- No credentials are stored permanently
- All communication uses HTTPS
- The application runs locally on your machine

## 📖 Additional Documentation

- **[Docker and Deployment Guide](DOCKER.md)** - Complete guide for Docker usage and CI/CD
- **[Development and Extension Guide](DEVELOPMENT.md)** - How to add new SMTP providers, DNS integrations, and extend the application
- **[Development Setup](DOCKER.md#development-environment)** - Local development instructions
- **[Release Process](DOCKER.md#creating-a-release)** - How to create and publish releases

## 🤝 Contributing

This project welcomes contributions! Whether you want to:

- Add support for new SMTP providers (SendGrid, Amazon SES, Postmark, etc.)
- Integrate additional DNS providers (cPanel, GoDaddy, Route 53, etc.)
- Improve the user interface
- Add new features or fix bugs

Please see the **[Development Guide](DEVELOPMENT.md)** for detailed instructions on extending the application.