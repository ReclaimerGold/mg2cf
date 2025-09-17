# Docker and Deployment Guide

This document provides comprehensive instructions for building, running, and deploying the Automatic Mailgun application using Docker and GitHub Actions.

## 🐳 Docker Setup

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier local development)

### Quick Start

#### 1. Build and Run with Docker Compose (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd automatic-mailgun

# Start the application
docker-compose up --build

# The application will be available at http://localhost:5000
```

#### 2. Build and Run with Docker
```bash
# Build the image
docker build -t automatic-mailgun .

# Run the container
docker run -p 5000:5000 automatic-mailgun
```

#### 3. Use Pre-built Image from GitHub Container Registry
```bash
# Pull and run the latest release
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/automatic-mailgun:latest
```

### Environment Configuration

Create a `.env` file (copy from `.env.example`) to configure the application:

```bash
# Flask Configuration
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000

# Optional API Base URLs (use defaults if not specified)
# MAILGUN_API_BASE_URL=https://api.mailgun.net/v3
# CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4
```

### Development Commands

Use the provided development script for common tasks:

```bash
# Build Docker image
./dev.sh build

# Run with Docker Compose
./dev.sh run

# Run tests
./dev.sh test

# Run linting
./dev.sh lint

# Clean up Docker resources
./dev.sh clean

# Run in development mode (local Python)
./dev.sh dev
```

## 🚀 GitHub Actions CI/CD

The project includes a comprehensive CI/CD pipeline that:

### On Every Push/PR:
- **Tests** the application on Python 3.9, 3.10, and 3.11
- **Lints** the code with flake8
- **Builds** and tests the Docker image
- **Validates** the application starts correctly

### On Release (Tag Push):
- **Publishes** Docker images to GitHub Container Registry (ghcr.io)
- **Supports** multi-architecture builds (linux/amd64, linux/arm64)
- **Tags** images with version numbers and latest

### Creating a Release

1. **Create and push a tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create a GitHub release:**
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Select the tag you just created
   - Fill in the release notes
   - Publish the release

3. **The workflow will automatically:**
   - Build the Docker image
   - Push it to `ghcr.io/YOUR_USERNAME/automatic-mailgun:v1.0.0`
   - Also tag it as `latest`

### Using Released Images

After a release, you can use the published Docker images:

```bash
# Use specific version
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/automatic-mailgun:v1.0.0

# Use latest version
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/automatic-mailgun:latest
```

## 🔧 Configuration Details

### Docker Image Features:
- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for container monitoring
- **Multi-architecture support** (AMD64, ARM64)
- **Security scanning** in CI pipeline

### Application Configuration:
- **Environment-based configuration** for flexibility
- **Production-ready defaults** in Docker
- **Debug mode** disabled in production
- **Configurable host and port** binding

### Security Best Practices:
- Non-root container execution
- Minimal base image (Python slim)
- No secrets in image layers
- Environment variable configuration
- Health checks for monitoring

## 📊 Monitoring and Health Checks

The Docker image includes health checks that verify the application is responding:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' <container-name>
```

## 🐛 Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Use a different port
   docker run -p 5001:5000 automatic-mailgun
   ```

2. **Build failures:**
   ```bash
   # Clean Docker build cache
   docker system prune -f
   docker build --no-cache -t automatic-mailgun .
   ```

3. **Permission issues:**
   ```bash
   # Ensure the dev script is executable
   chmod +x dev.sh
   ```

4. **Container won't start:**
   ```bash
   # Check container logs
   docker logs <container-name>
   ```

### Development Environment:

For local development without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd src && python main.py
```

## 📝 Next Steps

1. **Customize** the GitHub workflow for your repository name
2. **Set up** GitHub Container Registry permissions
3. **Configure** secrets for production deployments
4. **Set up** monitoring and logging for production
5. **Consider** using a production WSGI server like Gunicorn

For production deployments, consider:
- Using a reverse proxy (nginx)
- Setting up SSL/TLS certificates
- Implementing log aggregation
- Setting up container orchestration (Kubernetes)
- Configuring persistent storage if needed
