import requests
import json
import os

def get_user_input():
    """
    Gets the necessary API keys and domain name from the user.
    It first checks for environment variables, and if not found,
    prompts the user for input.
    """
    print("Loading configuration...")
    mailgun_api_key = os.environ.get("MAILGUN_API_KEY")
    cloudflare_api_key = os.environ.get("CLOUDFLARE_API_KEY")
    cloudflare_email = os.environ.get("CLOUDFLARE_EMAIL")
    
    if mailgun_api_key:
        print("✓ Mailgun API Key found in environment variables.")
    else:
        print("✗ Mailgun API Key not found. Please provide it.")
        mailgun_api_key = input("Enter your Mailgun API Key: ")

    if cloudflare_api_key:
        print("✓ Cloudflare API Key found in environment variables.")
    else:
        print("✗ Cloudflare API Key not found. Please provide it.")
        cloudflare_api_key = input("Enter your Cloudflare API Key: ")

    if cloudflare_email:
        print(f"✓ Cloudflare Email found in environment variables.")
    else:
        print("✗ Cloudflare Email not found. Please provide it.")
        cloudflare_email = input("Enter your Cloudflare Email: ")
        
    domain_name = input("\nEnter the domain you want to set up (e.g., example.com): ")
    
    return mailgun_api_key, cloudflare_api_key, cloudflare_email, domain_name

def get_mailgun_domain_details(api_key, domain_name):
    """Fetches details for an existing Mailgun domain."""
    print(f"Fetching details for existing Mailgun domain: {domain_name}...")
    try:
        response = requests.get(
            f"https://api.mailgun.net/v3/domains/{domain_name}",
            auth=("api", api_key)
        )
        response.raise_for_status()
        print("Successfully fetched domain details.")
        # The domain details are nested under the 'domain' key in the response
        return response.json().get('domain')
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching Mailgun domain details: {err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred while fetching domain details: {e}")
        return None

def create_mailgun_domain(api_key, domain_name):
    """
    Creates a new domain in Mailgun or fetches details if it already exists.
    """
    mailgun_domain = f"mg.{domain_name}"
    print(f"\nAttempting to create Mailgun domain: {mailgun_domain}...")
    
    try:
        response = requests.post(
            "https://api.mailgun.net/v3/domains",
            auth=("api", api_key),
            data={"name": mailgun_domain}
        )
        response.raise_for_status()
        print("Mailgun domain created successfully.")
        return mailgun_domain, response.json()
    except requests.exceptions.HTTPError as err:
        if "already exists" in str(err).lower():
            print("The domain already exists in Mailgun.")
            # If the domain exists, we must fetch its records via a GET request.
            domain_details = get_mailgun_domain_details(api_key, mailgun_domain)
            return mailgun_domain, domain_details
        
        print(f"Error creating Mailgun domain: {err}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return None, None


def get_cloudflare_zone_id(api_key, email, domain_name):
    """
    Retrieves the Cloudflare Zone ID for the given domain.
    """
    print(f"\nFinding Cloudflare zone for {domain_name}...")
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones?name={domain_name}",
            headers=headers
        )
        response.raise_for_status()
        zones = response.json().get("result", [])
        if zones:
            print("✓ Cloudflare zone found.")
            return zones[0]["id"]
        else:
            print("✗ Cloudflare zone not found.")
            return None
    except requests.exceptions.HTTPError as err:
        print(f"Error finding Cloudflare zone: {err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return None

def add_dns_records_to_cloudflare(api_key, email, zone_id, mailgun_dns_records):
    """
    Adds the necessary DNS records from Mailgun to Cloudflare.
    """
    print("\nAdding DNS records to Cloudflare...")
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }

    # Extracting sending and receiving DNS records
    dns_records_to_add = mailgun_dns_records.get('sending_dns_records', []) + mailgun_dns_records.get('receiving_dns_records', [])

    for record in dns_records_to_add:
        record_type = record.get("record_type")
        name = record.get("name")
        value = record.get("value")
        
        # Cloudflare uses 'content' for the record value
        data = {
            "type": record_type,
            "name": name,
            "content": value,
            "ttl": 3600 # 1 hour
        }
        
        # Special handling for MX records
        if record_type == "MX":
            # Mailgun API provides priority and value as separate fields for MX records.
            data["priority"] = int(record.get("priority", 10)) # Default to 10 if not found
            data["content"] = value # The 'value' is the server address

        try:
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            print(f"  ✓ Successfully added {record_type} record for {name}")
        except requests.exceptions.HTTPError as err:
            # Check if the record already exists
            if "already exists" in str(err).lower():
                 print(f"  - DNS record for {name} already exists.")
            else:
                print(f"  ✗ Error adding DNS record for {name}: {err}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ A network error occurred while adding DNS record for {name}: {e}")


def verify_mailgun_domain(api_key, domain_name):
    """
    Initiates the verification process for the Mailgun domain and prints the result.
    """
    print(f"\nInitiating verification for {domain_name}...")
    try:
        response = requests.put(
            f"https://api.mailgun.net/v3/domains/{domain_name}/verify",
            auth=("api", api_key)
        )
        response.raise_for_status()
        print("✓ Verification initiated successfully.")
        print("\nVerification result:")
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Error initiating verification: {err}")
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred during verification: {e}")


def main():
    """
    Main function to orchestrate the domain setup process.
    """
    mailgun_api_key, cloudflare_api_key, cloudflare_email, domain_name = get_user_input()

    mailgun_domain, mailgun_response = create_mailgun_domain(mailgun_api_key, domain_name)

    if mailgun_domain and mailgun_response:
        zone_id = get_cloudflare_zone_id(cloudflare_api_key, cloudflare_email, domain_name)
        if zone_id:
            add_dns_records_to_cloudflare(cloudflare_api_key, cloudflare_email, zone_id, mailgun_response)
            verify_mailgun_domain(mailgun_api_key, mailgun_domain)

if __name__ == "__main__":
    main()
