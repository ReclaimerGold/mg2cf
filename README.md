# 📧 Mailgun DNS Setup Tool

A simple, modern web application that automatically configures DNS records for Mailgun email delivery. Perfect for home labs, small businesses, or anyone who wants to set up professional email delivery without the hassle of manual DNS configuration.

## ✨ What This Does

This tool automatically:
- ✅ Creates the necessary DNS records for Mailgun email delivery
- ✅ Sets up SPF, DKIM, and MX records correctly
- ✅ Validates your domain configuration
- ✅ Provides a clean web interface for easy setup

**No more copying and pasting DNS records manually!**

## 🏠 Perfect for Home Labs

Whether you're running a home server, self-hosted applications, or just want reliable email delivery for your projects, this tool makes it dead simple to get Mailgun working with your domain.

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker installed on your system
- A domain name (can be a subdomain)
- Mailgun account (free tier available)
- Cloudflare account (free tier available)

### 1. Get Your API Keys

**Mailgun API Key:**
1. Go to [Mailgun Dashboard](https://app.mailgun.com/)
2. Navigate to Settings → API Keys
3. Copy your Private API key (starts with "key-")

**Cloudflare API Key:**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Click on your profile icon → My Profile → API Tokens
3. Find "Global API Key" and click "View"
4. Copy the API key and note your account email

### 2. Run the Application

**Option A: One-Command Start**
```bash
docker run -p 5000:5000 ghcr.io/reclaimergold/mg2cf:latest
```

**Option B: Build from Source**
```bash
# Clone the repository
git clone https://github.com/ReclaimerGold/mg2cf.git
cd mg2cf

# Start with Docker Compose
docker-compose up -d
```

### 3. Access the Web Interface

Open your browser and go to: `http://localhost:5000`

### 4. Configure Your Domain

1. Enter your domain name (e.g., `mail.yourdomain.com`)
2. Paste your Mailgun API key
3. Paste your Cloudflare API key and email
4. Click "Set Up Domain"

That's it! The tool will automatically create all the necessary DNS records.

## 🔧 Advanced Setup Options

## 🔧 Advanced Setup Options

### Using Docker Compose (Recommended for Production)

1. **Create a project directory:**
   ```bash
   mkdir mailgun-setup && cd mailgun-setup
   ```

2. **Create a `docker-compose.yml` file:**
   ```yaml
   version: '3.8'
   services:
     mailgun-setup:
       image: ghcr.io/reclaimergold/mg2cf:latest
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
         - SECRET_KEY=your-random-secret-key-here
       restart: unless-stopped
   ```

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```

### Environment Variables

You can configure the application using environment variables:

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this

# Application settings
FLASK_ENV=production          # Use 'development' for debugging
HOST=0.0.0.0                 # Host to bind to
PORT=5000                    # Port to run on

# Optional API base URLs (usually don't need to change)
MAILGUN_API_BASE_URL=https://api.mailgun.net/v3
CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4
```

### Running Behind a Reverse Proxy

If you're running this behind nginx or traefik:

**nginx example:**
```nginx
server {
    listen 80;
    server_name mailgun-setup.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Traefik labels (docker-compose):**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.mailgun-setup.rule=Host(`mailgun-setup.yourdomain.com`)"
```

## 🛠️ Local Development Setup

If you want to modify the code or run it without Docker:

```bash
# Clone the repository
git clone https://github.com/ReclaimerGold/mg2cf.git
cd mg2cf

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd src && python main.py
```

## 🔒 Security & Privacy

- **No Data Storage**: API keys are only used during setup and never stored
- **Local Processing**: All operations happen on your server
- **HTTPS Ready**: Works behind SSL termination proxies
- **Non-Root Container**: Docker image runs as non-privileged user
- **Security Headers**: Includes basic security headers

## 📋 Supported DNS Providers

Currently supported:
- ✅ **Cloudflare** (Primary support)

Want more providers? Check out our [Development Guide](DEVELOPMENT.md) to see how easy it is to add:
- cPanel/WHM
- GoDaddy
- Route 53
- NameCheap
- And more!

## 🎯 Use Cases

Perfect for:
- **Home Lab Enthusiasts**: Get professional email delivery for your projects
- **Small Business**: Set up reliable email without hiring a developer
- **Self-Hosted Apps**: Add email functionality to your applications
- **Learning**: Understand how email DNS records work
- **Automation**: Integrate into your infrastructure automation

## 🚨 Troubleshooting

### Common Issues

**"Port 5000 already in use"**
```bash
# Use a different port
docker run -p 8080:5000 ghcr.io/reclaimergold/mg2cf:latest
# Then access via http://localhost:8080
```

**"Cloudflare API Error"**
- Make sure you're using the Global API Key, not a token
- Verify your email address is correct
- Check that your domain is actually managed by Cloudflare

**"Mailgun Domain Not Found"**
- The tool will create the domain for you automatically
- Make sure your API key has the correct permissions

**"DNS Records Not Created"**
- Check that your Cloudflare zone exists for the domain
- Verify API permissions allow DNS modifications

### Getting Help

1. Check the browser console for errors (F12 → Console)
2. Look at container logs: `docker logs <container-name>`
3. Open an issue on GitHub with details

## 🔄 Updates & Maintenance

### Updating to Latest Version

```bash
# Pull latest image
docker pull ghcr.io/reclaimergold/mg2cf:latest

# Restart your container
docker-compose down && docker-compose up -d
```

### Backup & Recovery

Since this tool doesn't store data, there's nothing to backup! Just keep your API keys safe.

## ⚡ Performance & Scaling

- **Lightweight**: Alpine Linux base image (~50MB)
- **Fast**: Typically completes setup in under 30 seconds
- **Resource Efficient**: Runs comfortably on Raspberry Pi
- **Stateless**: Can be easily replicated or moved

## 📊 Monitoring

The container includes health checks. You can monitor it with:

```bash
# Check container health
docker ps

# View detailed health status
docker inspect <container-name> | grep -A 10 Health
```

For production monitoring, the `/` endpoint returns HTTP 200 when healthy.

## 📁 Project Structure

```
mg2cf/
├── src/                     # Application source code
│   ├── main.py              # Flask application entry point
│   ├── templates/           # HTML templates
│   ├── api/                 # External API clients
│   ├── models/              # Data models
│   └── utils/               # Utility functions
├── tests/                   # Automated tests
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📖 Additional Resources

- **[Production Readiness Guide](PRODUCTION.md)** - Complete production deployment checklist
- **[Docker Deployment Guide](DOCKER.md)** - Advanced Docker configurations and CI/CD
- **[Development Guide](DEVELOPMENT.md)** - Add new providers and extend functionality
- **[GitHub Repository](https://github.com/ReclaimerGold/mg2cf)** - Source code and issues

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Quick Wins
- 🐛 **Report bugs** or suggest improvements
- 📝 **Improve documentation** or add examples
- 🌍 **Add translations** for international users

### Major Contributions
- 🔌 **Add DNS providers** (GoDaddy, Route 53, etc.)
- 📧 **Add SMTP providers** (SendGrid, Amazon SES, etc.)
- 🎨 **Improve the user interface**
- ⚡ **Performance optimizations**

See our [Development Guide](DEVELOPMENT.md) for detailed instructions.

## ⭐ Star This Project

If this tool saves you time, please star the repository! It helps others discover it.

## 📄 License

This project is open source and available under the [MIT License](LICENSE.md).

---

**Made with ❤️ for the home lab community**

Need help? Open an issue on GitHub or check our troubleshooting guide above!