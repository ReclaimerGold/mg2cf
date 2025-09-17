from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
# from utils.config import load_config
from api.cloudflare_client import CloudflareClient
from api.mailgun_client import MailgunClient
import os
import secrets

app = Flask(__name__)

# Security configuration
secret_key = os.environ.get('SECRET_KEY')
if not secret_key or secret_key == 'dev-secret-key-change-in-production':
    if os.environ.get('FLASK_ENV') == 'development':
        secret_key = 'dev-secret-key-change-in-production'
    else:
        # Generate a random secret key for production if none provided
        secret_key = secrets.token_hex(32)
        print("WARNING: No SECRET_KEY environment variable set. Generated random key.")

app.secret_key = secret_key

# Security headers
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:; font-src 'self' data:;"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/security-verification')
def security_verification():
    return render_template('security_verification.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        # Get form data
        domain = request.form.get('domain')
        mailgun_api_key = request.form.get('mailgun_api_key')
        cloudflare_api_key = request.form.get('cloudflare_api_key')
        cloudflare_email = request.form.get('cloudflare_email')
        
        if not all([domain, mailgun_api_key, cloudflare_api_key, cloudflare_email]):
            flash('All fields are required', 'error')
            return render_template('setup.html')
        
        try:
            # Try to find Cloudflare zone
            cf_client = CloudflareClient(cloudflare_api_key, cloudflare_email)
            zone_id = cf_client.get_zone_id(domain)
            
            if zone_id:
                # Zone found, proceed with automatic setup
                return redirect(url_for('automatic_setup', 
                                      domain=domain, 
                                      mailgun_api_key=mailgun_api_key,
                                      cloudflare_api_key=cloudflare_api_key,
                                      cloudflare_email=cloudflare_email,
                                      zone_id=zone_id))
            else:
                # Zone not found, show manual entry
                return redirect(url_for('manual_setup', 
                                      domain=domain, 
                                      mailgun_api_key=mailgun_api_key))
                
        except Exception as e:
            flash(f'Error connecting to Cloudflare: {str(e)}', 'error')
            return render_template('setup.html')
    
    return render_template('setup.html')

@app.route('/automatic-setup')
def automatic_setup():
    domain = request.args.get('domain')
    mailgun_api_key = request.args.get('mailgun_api_key')
    cloudflare_api_key = request.args.get('cloudflare_api_key')
    cloudflare_email = request.args.get('cloudflare_email')
    zone_id = request.args.get('zone_id')
    
    return render_template('automatic_setup.html', 
                         domain=domain,
                         mailgun_api_key=mailgun_api_key,
                         cloudflare_api_key=cloudflare_api_key,
                         cloudflare_email=cloudflare_email,
                         zone_id=zone_id)

@app.route('/api/perform-automatic-setup', methods=['POST'])
def perform_automatic_setup():
    """API endpoint to perform the actual automatic setup"""
    data = request.json
    domain = data.get('domain')
    mailgun_api_key = data.get('mailgun_api_key')
    cloudflare_api_key = data.get('cloudflare_api_key')
    cloudflare_email = data.get('cloudflare_email')
    zone_id = data.get('zone_id')
    
    try:
        # Initialize clients
        mg_client = MailgunClient(mailgun_api_key)
        cf_client = CloudflareClient(cloudflare_api_key, cloudflare_email)
        
        # Create mailgun domain
        mailgun_domain = f"mg.{domain}"
        success, domain_info = mg_client.create_domain(mailgun_domain)
        
        if not success:
            return jsonify({'success': False, 'error': 'Failed to create Mailgun domain'})
        
        # Get DNS records
        success, dns_records = mg_client.get_domain_dns_records(mailgun_domain)
        
        if not success:
            return jsonify({'success': False, 'error': 'Failed to get DNS records'})
        
        # Create DNS records in Cloudflare
        created_records = []
        for record in dns_records:
            success, result = cf_client.create_dns_record(
                zone_id, 
                record['type'], 
                record['name'], 
                record['value']
            )
            created_records.append({
                'record': record,
                'success': success,
                'result': result
            })
        
        return jsonify({
            'success': True, 
            'domain_info': domain_info,
            'dns_records': created_records
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/manual-setup')
def manual_setup():
    domain = request.args.get('domain')
    mailgun_api_key = request.args.get('mailgun_api_key')
    
    # Get DNS records from Mailgun API
    dns_records = get_mailgun_dns_records(domain, mailgun_api_key)
    
    return render_template('manual_setup.html', domain=domain, dns_records=dns_records)

def get_mailgun_dns_records(domain, api_key):
    """Get the required DNS records from Mailgun API"""
    try:
        mg_client = MailgunClient(api_key)
        
        # List all domains to help with debugging
        success, domains_info = mg_client.list_domains()
        if success and 'items' in domains_info:
            print(f"Available domains in Mailgun account:")
            for domain_item in domains_info['items']:
                print(f"  - {domain_item.get('name', 'Unknown')}")
        
        # Try different domain formats
        domain_variants = [
            domain,                    # exactly as entered
            f"mg.{domain}",           # with mg. prefix  
            f"mail.{domain}",         # with mail. prefix
            f"email.{domain}",        # with email. prefix
        ]
        
        for domain_variant in domain_variants:
            print(f"Trying domain variant: {domain_variant}")
            success, dns_records = mg_client.get_domain_dns_records(domain_variant)
            
            if success and dns_records:
                print(f"Successfully found DNS records for: {domain_variant}")
                return dns_records
            elif success:
                print(f"Domain {domain_variant} found but no DNS records returned")
        
        print("No domain variants worked, returning fallback records")
        return get_fallback_dns_records(domain)
            
    except Exception as e:
        print(f"Exception in get_mailgun_dns_records: {str(e)}")
        # Return fallback records if there's an error
        return get_fallback_dns_records(domain)

def get_fallback_dns_records(domain):
    """Fallback DNS records if Mailgun API is not available"""
    return [
        {
            'type': 'TXT',
            'name': f'mg.{domain}',
            'value': 'v=spf1 include:mailgun.org ~all',
            'description': 'SPF Record'
        },
        {
            'type': 'TXT', 
            'name': f'krs._domainkey.mg.{domain}',
            'value': 'k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...(contact Mailgun for actual DKIM key)',
            'description': 'DKIM Record'
        },
        {
            'type': 'CNAME',
            'name': f'email.mg.{domain}',
            'value': 'mailgun.org',
            'description': 'Tracking Record'
        },
        {
            'type': 'MX',
            'name': f'mg.{domain}',
            'value': '10 mxa.mailgun.org',
            'description': 'MX Record'
        },
        {
            'type': 'MX',
            'name': f'mg.{domain}',
            'value': '10 mxb.mailgun.org',
            'description': 'MX Record (Backup)'
        }
    ]

if __name__ == "__main__":
    # Get configuration from environment variables
    debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(debug=debug, host=host, port=port)