# Developer Extension Guide

This guide provides detailed instructions for developers who want to extend the Automatic Mailgun application with additional SMTP providers, DNS integrations, or other enhancements.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Adding SMTP Providers](#adding-smtp-providers)
- [Adding DNS Providers](#adding-dns-providers)
- [Database Integration](#database-integration)
- [API Enhancements](#api-enhancements)
- [Frontend Improvements](#frontend-improvements)
- [Testing Extensions](#testing-extensions)
- [Deployment Considerations](#deployment-considerations)

## 🏗️ Architecture Overview

The application follows a modular architecture that makes it easy to extend:

```
src/
├── main.py              # Flask routes and main application logic
├── api/                 # External API client modules
│   ├── cloudflare_client.py
│   ├── mailgun_client.py
│   └── [new_provider_client.py]  # Add new providers here
├── models/              # Data models and structures
│   ├── dns_record.py
│   └── [smtp_config.py]      # Add new models here
├── utils/               # Utility functions and configuration
│   ├── config.py
│   └── [provider_factory.py] # Add factory patterns here
└── templates/           # HTML templates
```

### Key Design Patterns:

1. **Client Pattern** - Each external service has its own client class
2. **Model Pattern** - Data structures are separated from business logic
3. **Factory Pattern** - Use for creating provider instances dynamically
4. **Template Pattern** - Consistent UI across different providers

## 📧 Adding SMTP Providers

### 1. Supported SMTP Providers to Consider:

- **SendGrid** - Popular email delivery service
- **Amazon SES** - AWS Simple Email Service
- **Postmark** - Developer-focused email delivery
- **SparkPost** - Enterprise email delivery
- **SMTP2GO** - Global email delivery network
- **Elastic Email** - Cost-effective email platform

### 2. Implementation Steps:

#### Step 1: Create the Client Module

Create `src/api/sendgrid_client.py`:

```python
import requests
from typing import List, Dict, Optional
from models.dns_record import DNSRecord

class SendGridClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sendgrid.com/v3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def verify_domain(self, domain: str) -> bool:
        """Verify if domain exists in SendGrid"""
        try:
            response = requests.get(
                f"{self.base_url}/whitelabel/domains",
                headers=self.headers
            )
            response.raise_for_status()
            domains = response.json()
            return any(d['domain'] == domain for d in domains)
        except requests.RequestException:
            return False
    
    def get_dns_records(self, domain: str) -> List[DNSRecord]:
        """Get required DNS records for SendGrid domain authentication"""
        # Implementation specific to SendGrid's domain authentication
        records = [
            DNSRecord(
                type="CNAME",
                name=f"em{self._get_subdomain_id()}.{domain}",
                value="u{user_id}.wl{whitelabel_id}.sendgrid.net",
                description="SendGrid Domain Authentication"
            ),
            # Add other required records...
        ]
        return records
    
    def create_domain_authentication(self, domain: str) -> Dict:
        """Create domain authentication in SendGrid"""
        payload = {
            "domain": domain,
            "automatic_security": True,
            "custom_spf": True,
            "default": True
        }
        response = requests.post(
            f"{self.base_url}/whitelabel/domains",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
```

#### Step 2: Create Configuration Model

Create `src/models/smtp_config.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from models.dns_record import DNSRecord

@dataclass
class SMTPConfig:
    provider: str
    domain: str
    api_key: str
    dns_records: List[DNSRecord]
    verification_status: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "domain": self.domain,
            "dns_records": [record.to_dict() for record in self.dns_records],
            "verification_status": self.verification_status,
            "created_at": self.created_at
        }
```

#### Step 3: Create Provider Factory

Create `src/utils/provider_factory.py`:

```python
from api.mailgun_client import MailgunClient
from api.sendgrid_client import SendGridClient
# Import other providers...

class SMTPProviderFactory:
    @staticmethod
    def create_client(provider: str, api_key: str, **kwargs):
        providers = {
            'mailgun': MailgunClient,
            'sendgrid': SendGridClient,
            # Add other providers...
        }
        
        if provider not in providers:
            raise ValueError(f"Unsupported SMTP provider: {provider}")
        
        return providers[provider](api_key, **kwargs)
    
    @staticmethod
    def get_supported_providers():
        return ['mailgun', 'sendgrid']  # Add others as implemented
```

#### Step 4: Update Main Application

Update `src/main.py` to support multiple providers:

```python
from utils.provider_factory import SMTPProviderFactory

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        domain = request.form.get('domain')
        smtp_provider = request.form.get('smtp_provider')  # New field
        smtp_api_key = request.form.get('smtp_api_key')
        dns_provider = request.form.get('dns_provider', 'cloudflare')
        
        try:
            # Create SMTP client using factory
            smtp_client = SMTPProviderFactory.create_client(
                smtp_provider, 
                smtp_api_key
            )
            
            # Get required DNS records
            dns_records = smtp_client.get_dns_records(domain)
            
            # Continue with existing logic...
            
        except Exception as e:
            flash(f'Error with {smtp_provider}: {str(e)}', 'error')
            return render_template('setup.html')
```

## 🌐 Adding DNS Providers

### 1. Potential DNS Providers:

- **cPanel/WHM** - Popular web hosting control panel
- **GoDaddy** - Domain registrar with DNS management
- **Route 53** - AWS DNS service
- **NameCheap** - Domain registrar and DNS provider
- **DigitalOcean** - Cloud DNS service
- **Cloudways** - Managed hosting DNS

### 2. Implementation Example - cPanel Integration:

#### Step 1: Create cPanel Client

Create `src/api/cpanel_client.py`:

```python
import requests
import json
from typing import List, Optional
from models.dns_record import DNSRecord

class CPanelClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Get zone information for domain"""
        try:
            response = self.session.get(
                f"{self.base_url}/execute/DNS/parse_zone",
                params={"domain": domain}
            )
            response.raise_for_status()
            data = response.json()
            return domain if data.get("status") == 1 else None
        except requests.RequestException:
            return None
    
    def create_dns_record(self, domain: str, dns_record: DNSRecord) -> bool:
        """Create a DNS record in cPanel"""
        try:
            params = {
                "domain": domain,
                "name": dns_record.name,
                "type": dns_record.type,
                "record": dns_record.value,
                "ttl": dns_record.ttl or 14400
            }
            
            response = self.session.get(
                f"{self.base_url}/execute/DNS/mass_edit_zone",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return data.get("status") == 1
            
        except requests.RequestException as e:
            print(f"Error creating DNS record: {e}")
            return False
    
    def list_dns_records(self, domain: str) -> List[dict]:
        """List existing DNS records"""
        try:
            response = self.session.get(
                f"{self.base_url}/execute/DNS/parse_zone",
                params={"domain": domain}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("record", [])
        except requests.RequestException:
            return []
```

#### Step 2: Create DNS Provider Factory

Create `src/utils/dns_factory.py`:

```python
from api.cloudflare_client import CloudflareClient
from api.cpanel_client import CPanelClient

class DNSProviderFactory:
    @staticmethod
    def create_client(provider: str, **credentials):
        if provider == 'cloudflare':
            return CloudflareClient(
                credentials['api_key'],
                credentials['email']
            )
        elif provider == 'cpanel':
            return CPanelClient(
                credentials['base_url'],
                credentials['username'],
                credentials['password']
            )
        else:
            raise ValueError(f"Unsupported DNS provider: {provider}")
    
    @staticmethod
    def get_required_fields(provider: str) -> List[str]:
        fields = {
            'cloudflare': ['api_key', 'email'],
            'cpanel': ['base_url', 'username', 'password'],
            'godaddy': ['api_key', 'api_secret'],
            'route53': ['access_key', 'secret_key', 'region']
        }
        return fields.get(provider, [])
```

### 3. GoDaddy Integration Example:

```python
class GoDaddyClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.godaddy.com/v1"
        self.headers = {
            "Authorization": f"sso-key {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Check if domain exists in GoDaddy"""
        try:
            response = requests.get(
                f"{self.base_url}/domains/{domain}",
                headers=self.headers
            )
            return domain if response.status_code == 200 else None
        except requests.RequestException:
            return None
    
    def create_dns_record(self, domain: str, dns_record: DNSRecord) -> bool:
        """Create DNS record in GoDaddy"""
        try:
            record_data = [{
                "type": dns_record.type,
                "name": dns_record.name.replace(f".{domain}", ""),
                "data": dns_record.value,
                "ttl": dns_record.ttl or 3600
            }]
            
            response = requests.patch(
                f"{self.base_url}/domains/{domain}/records",
                headers=self.headers,
                json=record_data
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
```

## 🗄️ Database Integration

For production use, consider adding database support:

### 1. Add Database Models

Create `src/models/database.py`:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Domain(Base):
    __tablename__ = 'domains'
    
    id = Column(Integer, primary_key=True)
    domain_name = Column(String(255), unique=True, nullable=False)
    smtp_provider = Column(String(50), nullable=False)
    dns_provider = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DNSRecordHistory(Base):
    __tablename__ = 'dns_records'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, nullable=False)
    record_type = Column(String(10), nullable=False)
    record_name = Column(String(255), nullable=False)
    record_value = Column(Text, nullable=False)
    created_successfully = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
```

### 2. Update Requirements

Add to `requirements.txt`:
```
sqlalchemy>=1.4.0
alembic>=1.8.0
psycopg2-binary>=2.9.0  # For PostgreSQL
```

## 🔧 API Enhancements

### 1. REST API Endpoints

Create `src/api/rest_endpoints.py`:

```python
from flask import Blueprint, jsonify, request
from utils.provider_factory import SMTPProviderFactory
from utils.dns_factory import DNSProviderFactory

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/providers/smtp', methods=['GET'])
def get_smtp_providers():
    """Get list of supported SMTP providers"""
    return jsonify({
        'providers': SMTPProviderFactory.get_supported_providers()
    })

@api_bp.route('/providers/dns', methods=['GET'])
def get_dns_providers():
    """Get list of supported DNS providers"""
    return jsonify({
        'providers': ['cloudflare', 'cpanel', 'godaddy']
    })

@api_bp.route('/domain/setup', methods=['POST'])
def setup_domain_api():
    """API endpoint for domain setup"""
    data = request.get_json()
    
    try:
        smtp_client = SMTPProviderFactory.create_client(
            data['smtp_provider'],
            data['smtp_api_key']
        )
        
        dns_records = smtp_client.get_dns_records(data['domain'])
        
        return jsonify({
            'success': True,
            'dns_records': [record.to_dict() for record in dns_records]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
```

### 2. Webhook Support

Add webhook endpoints for provider notifications:

```python
@api_bp.route('/webhooks/<provider>', methods=['POST'])
def webhook_handler(provider: str):
    """Handle webhooks from various providers"""
    data = request.get_json()
    
    # Process webhook based on provider
    if provider == 'mailgun':
        # Handle Mailgun webhook
        pass
    elif provider == 'sendgrid':
        # Handle SendGrid webhook
        pass
    
    return jsonify({'status': 'received'})
```

## 🎨 Frontend Improvements

### 1. Dynamic Provider Selection

Update `src/templates/setup.html`:

```html
<!-- Add provider selection -->
<div class="form-group">
    <label for="smtp_provider">SMTP Provider:</label>
    <select id="smtp_provider" name="smtp_provider" required>
        <option value="mailgun">Mailgun</option>
        <option value="sendgrid">SendGrid</option>
        <option value="ses">Amazon SES</option>
    </select>
</div>

<div class="form-group">
    <label for="dns_provider">DNS Provider:</label>
    <select id="dns_provider" name="dns_provider" required>
        <option value="cloudflare">Cloudflare</option>
        <option value="cpanel">cPanel</option>
        <option value="godaddy">GoDaddy</option>
    </select>
</div>

<script>
// Dynamic form fields based on provider selection
document.getElementById('dns_provider').addEventListener('change', function() {
    const provider = this.value;
    const credentialsDiv = document.getElementById('dns-credentials');
    
    // Update form fields based on provider
    if (provider === 'cpanel') {
        credentialsDiv.innerHTML = `
            <input type="url" name="cpanel_url" placeholder="cPanel URL" required>
            <input type="text" name="cpanel_username" placeholder="Username" required>
            <input type="password" name="cpanel_password" placeholder="Password" required>
        `;
    }
    // Add other provider fields...
});
</script>
```

### 2. Progress Indicators

Add real-time progress updates using WebSockets or AJAX:

```javascript
// Progress tracking for DNS record creation
function trackProgress(domainId) {
    const eventSource = new EventSource(`/api/v1/domain/${domainId}/progress`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateProgressBar(data.progress, data.message);
        
        if (data.complete) {
            eventSource.close();
            showCompletionMessage(data.success);
        }
    };
}
```

## 🧪 Testing Extensions

### 1. Provider-Specific Tests

Create `tests/test_providers.py`:

```python
import pytest
from unittest.mock import Mock, patch
from api.sendgrid_client import SendGridClient
from api.cpanel_client import CPanelClient

class TestSendGridClient:
    def setup_method(self):
        self.client = SendGridClient("test_api_key")
    
    @patch('requests.get')
    def test_verify_domain_success(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [{"domain": "example.com"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.verify_domain("example.com")
        assert result is True
    
    @patch('requests.get')
    def test_verify_domain_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException()
        
        result = self.client.verify_domain("example.com")
        assert result is False

class TestCPanelClient:
    def setup_method(self):
        self.client = CPanelClient(
            "https://example.com:2083",
            "username",
            "password"
        )
    
    # Add cPanel-specific tests...
```

### 2. Integration Tests

Create comprehensive integration tests:

```python
class TestProviderIntegration:
    @pytest.mark.integration
    def test_full_smtp_dns_workflow(self):
        """Test complete workflow with multiple providers"""
        # This would require test accounts or mock services
        pass
```

## 🚀 Deployment Considerations

### 1. Environment Configuration

Update `.env.example` for new providers:

```bash
# SMTP Provider Settings
DEFAULT_SMTP_PROVIDER=mailgun
SENDGRID_API_KEY=your_sendgrid_key
MAILGUN_API_KEY=your_mailgun_key

# DNS Provider Settings
DEFAULT_DNS_PROVIDER=cloudflare
CLOUDFLARE_API_KEY=your_cloudflare_key
CLOUDFLARE_EMAIL=your_email
CPANEL_URL=https://your-cpanel-url:2083
CPANEL_USERNAME=your_username
CPANEL_PASSWORD=your_password

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### 2. Docker Updates

Update `Dockerfile` for additional dependencies:

```dockerfile
# Add any provider-specific system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

### 3. Monitoring and Logging

Add structured logging for provider operations:

```python
import logging
import structlog

logger = structlog.get_logger()

class ProviderLogger:
    @staticmethod
    def log_provider_operation(provider: str, operation: str, domain: str, success: bool, details: dict = None):
        logger.info(
            "provider_operation",
            provider=provider,
            operation=operation,
            domain=domain,
            success=success,
            details=details or {}
        )
```

## 📋 Development Checklist

When adding a new provider, ensure you:

- [ ] Create client class with consistent interface
- [ ] Add comprehensive error handling
- [ ] Write unit tests for all methods
- [ ] Update factory classes
- [ ] Add configuration validation
- [ ] Update templates and forms
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Add logging and monitoring
- [ ] Test with real provider accounts
- [ ] Update Docker configuration if needed
- [ ] Add provider to CI/CD pipeline

## 🤝 Contributing Guidelines

### 1. Code Standards
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to all public methods
- Maintain test coverage above 80%

### 2. Provider Integration Standards
- Implement consistent error handling
- Use proper HTTP status codes
- Add rate limiting considerations
- Implement retry logic for transient failures
- Validate all inputs before API calls

### 3. Security Considerations
- Never log API keys or sensitive data
- Validate all user inputs
- Use environment variables for credentials
- Implement proper authentication for API endpoints
- Add CSRF protection for web forms

This guide provides a solid foundation for extending the application. Each new provider should follow these patterns to maintain consistency and reliability across the codebase.
