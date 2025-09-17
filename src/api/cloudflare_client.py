import requests

class CloudflareClient:
    def __init__(self, api_key, email):
        self.api_key = api_key
        self.email = email
        self.base_url = "https://api.cloudflare.com/client/v4"

    def get_zone_id(self, zone_name):
        """Get the zone ID for a given domain"""
        url = f"{self.base_url}/zones?name={zone_name}"
        headers = {
            "X-Auth-Email": self.email,
            "X-Auth-Key": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                return data['result'][0]['id']
        return None

    def check_zone_exists(self, zone_name):
        """Check if a zone exists in Cloudflare"""
        return self.get_zone_id(zone_name) is not None

    def create_dns_record(self, zone_id, record_type, name, content, ttl=1):
        """Create a DNS record in Cloudflare"""
        url = f"{self.base_url}/zones/{zone_id}/dns_records"
        headers = {
            "X-Auth-Email": self.email,
            "X-Auth-Key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl
        }
        
        # Handle MX records which need priority
        if record_type == "MX":
            parts = content.split(" ", 1)
            if len(parts) == 2:
                data["priority"] = int(parts[0])
                data["content"] = parts[1]
        
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200, response.json()

    def get_dns_records(self, zone_id):
        """Get all DNS records for a zone"""
        url = f"{self.base_url}/zones/{zone_id}/dns_records"
        headers = {
            "X-Auth-Email": self.email,
            "X-Auth-Key": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['result']
        return []