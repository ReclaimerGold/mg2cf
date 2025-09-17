import requests
import base64

class MailgunClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mailgun.net/v3"
        
    def create_domain(self, domain_name):
        """Create a new domain in Mailgun"""
        url = f"{self.base_url}/domains"
        auth = ('api', self.api_key)
        data = {
            'name': domain_name,
            'smtp_password': 'supersecretpassword123',  # You might want to generate this
        }
        
        response = requests.post(url, auth=auth, data=data)
        return response.status_code == 200, response.json()
    
    def get_domain(self, domain_name):
        """Get domain information from Mailgun"""
        url = f"{self.base_url}/domains/{domain_name}"
        auth = ('api', self.api_key)
        
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                return True, response.json()
            else:
                print(f"Mailgun API error for domain {domain_name}: {response.status_code} - {response.text}")
                return False, {"error": response.text}
        except Exception as e:
            print(f"Exception when getting domain {domain_name}: {str(e)}")
            return False, {"error": str(e)}
    
    def list_domains(self):
        """List all domains in the Mailgun account"""
        url = f"{self.base_url}/domains"
        auth = ('api', self.api_key)
        
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                return True, response.json()
            else:
                print(f"Mailgun API error listing domains: {response.status_code} - {response.text}")
                return False, {"error": response.text}
        except Exception as e:
            print(f"Exception when listing domains: {str(e)}")
            return False, {"error": str(e)}
    
    def get_domain_dns_records(self, domain):
        """Get the DNS records for a domain from Mailgun
        Returns (success: bool, dns_records: dict)"""
        try:
            print(f"Attempting to get DNS records for domain: {domain}")
            url = f"{self.api_base}/domains/{domain}"
            
            response = requests.get(url, auth=('api', self.api_key), timeout=30)
            print(f"Mailgun API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Received data keys: {list(data.keys()) if data else 'No data'}")
                
                if 'domain' in data:
                    domain_info = data['domain']
                    dns_records = {
                        'mx': domain_info.get('mx_records', []),
                        'txt': domain_info.get('txt_records', []),
                        'cname': domain_info.get('cname_records', [])
                    }
                    print(f"DNS records found - MX: {len(dns_records['mx'])}, TXT: {len(dns_records['txt'])}, CNAME: {len(dns_records['cname'])}")
                    return True, dns_records
                else:
                    print("No 'domain' key in response data")
                    return False, {}
            elif response.status_code == 404:
                print(f"Domain {domain} not found in Mailgun (404)")
                return False, {}
            else:
                print(f"Error getting domain DNS records: {response.status_code} - {response.text}")
                return False, {}
                
        except requests.exceptions.RequestException as e:
            print(f"Request exception getting domain DNS records: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"Unexpected error getting domain DNS records: {str(e)}")
            return False, {}
    
    def verify_domain(self, domain_name):
        """Verify domain DNS settings"""
        url = f"{self.base_url}/domains/{domain_name}/verify"
        auth = ('api', self.api_key)
        
        response = requests.put(url, auth=auth)
        return response.status_code == 200, response.json()
