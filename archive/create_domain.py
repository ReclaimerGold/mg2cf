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

def display_dns_records_table(mailgun_dns_records, domain_name):
    """
    Displays DNS records in a formatted table for manual application if needed.
    """
    print("\n" + "="*80)
    print("DNS RECORDS FOR MANUAL APPLICATION")
    print("="*80)
    print(f"{'TYPE':<6} {'NAME':<35} {'PRIORITY':<8} {'VALUE':<30}")
    print("-"*80)
    
    # Process sending DNS records
    for record in mailgun_dns_records.get('sending_dns_records', []):
        record_type = record.get("record_type", "")
        name = record.get("name", "")
        value = record.get("value", "")
        priority = record.get("priority", "")
        
        # Truncate long values for display
        display_value = value[:30] + "..." if len(value) > 30 else value
        print(f"{record_type:<6} {name:<35} {priority:<8} {display_value:<30}")
    
    # Process receiving DNS records (MX records)
    for record in mailgun_dns_records.get('receiving_dns_records', []):
        record_type = record.get("record_type", "")
        # MX records use the main domain as the name
        name = f"mg.{domain_name}"
        value = record.get("value", "")
        priority = record.get("priority", "")
        
        display_value = value[:30] + "..." if len(value) > 30 else value
        print(f"{record_type:<6} {name:<35} {priority:<8} {display_value:<30}")
    
    print("-"*80)
    print("Note: Full record values may be truncated for display. Check the verification")
    print("output above for complete values.")
    print("="*80)

def add_dns_records_to_cloudflare(api_key, email, zone_id, mailgun_dns_records, domain_name):
    """
    Adds the necessary DNS records from Mailgun to Cloudflare.
    """
    print("\nAdding DNS records to Cloudflare...")
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }

    # Process sending DNS records
    sending_records = mailgun_dns_records.get('sending_dns_records', [])
    receiving_records = mailgun_dns_records.get('receiving_dns_records', [])
    
    print(f"\nProcessing {len(sending_records)} sending DNS records...")
    for record in sending_records:
        record_type = record.get("record_type")
        name = record.get("name")
        value = record.get("value")
        
        if not name or not value:
            print(f"  ⚠ Skipping incomplete record: {record}")
            continue
        
        # Cloudflare uses 'content' for the record value
        data = {
            "type": record_type,
            "name": name,
            "content": value,
            "ttl": 3600 # 1 hour
        }

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
                print(f"    Record data: {data}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ A network error occurred while adding DNS record for {name}: {e}")

    print(f"\nProcessing {len(receiving_records)} receiving DNS records (MX)...")
    for record in receiving_records:
        record_type = record.get("record_type")
        # For MX records, the name should be the mailgun domain
        name = f"mg.{domain_name}"
        value = record.get("value")
        priority = record.get("priority")
        
        if not value:
            print(f"  ⚠ Skipping incomplete MX record: {record}")
            continue
        
        # Special handling for MX records
        data = {
            "type": record_type,
            "name": name,
            "content": value,
            "priority": int(priority) if priority else 10,
            "ttl": 3600 # 1 hour
        }

        try:
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            print(f"  ✓ Successfully added {record_type} record for {name} (priority: {priority})")
        except requests.exceptions.HTTPError as err:
            # Check if the record already exists
            if "already exists" in str(err).lower():
                 print(f"  - DNS record for {name} already exists.")
            else:
                print(f"  ✗ Error adding DNS record for {name}: {err}")
                print(f"    Record data: {data}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ A network error occurred while adding DNS record for {name}: {e}")


def verify_mailgun_domain(api_key, domain_name):
    """
    Initiates the verification process for the Mailgun domain and prints the result.
    """
    print(f"\n{'='*60}")
    print("MAILGUN DOMAIN VERIFICATION")
    print(f"{'='*60}")
    print(f"Initiating verification for {domain_name}...")
    try:
        response = requests.put(
            f"https://api.mailgun.net/v3/domains/{domain_name}/verify",
            auth=("api", api_key)
        )
        response.raise_for_status()
        result = response.json()
        
        print("✓ Verification initiated successfully.")
        
        # Display domain status
        domain_info = result.get('domain', {})
        print(f"\nDomain Status:")
        print(f"  Name: {domain_info.get('name', 'N/A')}")
        print(f"  State: {domain_info.get('state', 'N/A')}")
        print(f"  Created: {domain_info.get('created_at', 'N/A')}")
        print(f"  Type: {domain_info.get('type', 'N/A')}")
        
        # Display sending DNS record status
        print(f"\nSending DNS Records Status:")
        for record in result.get('sending_dns_records', []):
            status_icon = "✓" if record.get('is_active') else "⚠"
            print(f"  {status_icon} {record.get('record_type', '')} - {record.get('name', '')} - Valid: {record.get('valid', 'unknown')}")
        
        # Display receiving DNS record status  
        print(f"\nReceiving DNS Records Status:")
        for record in result.get('receiving_dns_records', []):
            status_icon = "✓" if record.get('is_active') else "⚠"
            print(f"  {status_icon} {record.get('record_type', '')} - {record.get('value', '')} (Priority: {record.get('priority', 'N/A')}) - Valid: {record.get('valid', 'unknown')}")
        
        print(f"\n{'='*60}")
        print("Note: DNS propagation may take up to 24-48 hours.")
        print("You can check verification status later using the Mailgun dashboard.")
        print(f"{'='*60}")
        
        # Still show full JSON for debugging if needed
        print(f"\nFull verification response (for debugging):")
        print(json.dumps(result, indent=2))
        
    except requests.exceptions.HTTPError as err:
        print(f"✗ Error initiating verification: {err}")
    except requests.exceptions.RequestException as e:
        print(f"✗ A network error occurred during verification: {e}")


def main():
    """
    Main function to orchestrate the domain setup process.
    """
    print("🚀 MAILGUN DOMAIN SETUP AUTOMATION")
    print("=" * 50)
    
    mailgun_api_key, cloudflare_api_key, cloudflare_email, domain_name = get_user_input()

    mailgun_domain, mailgun_response = create_mailgun_domain(mailgun_api_key, domain_name)

    if mailgun_domain and mailgun_response:
        zone_id = get_cloudflare_zone_id(cloudflare_api_key, cloudflare_email, domain_name)
        if zone_id:
            add_dns_records_to_cloudflare(cloudflare_api_key, cloudflare_email, zone_id, mailgun_response, domain_name)
            verify_mailgun_domain(mailgun_api_key, mailgun_domain)
            # Display DNS records table for manual reference
            display_dns_records_table(mailgun_response, domain_name)
            
            print("\n" + "🎉" * 20)
            print("SETUP COMPLETED!")
            print("🎉" * 20)
            print(f"✓ Mailgun domain '{mailgun_domain}' has been configured")
            print(f"✓ DNS records have been added to Cloudflare for '{domain_name}'")
            print(f"✓ Domain verification has been initiated")
            print("\nNext steps:")
            print("1. Wait for DNS propagation (24-48 hours)")
            print("2. Check verification status in Mailgun dashboard")
            print("3. Test email sending once verification is complete")
            print("\nIf automatic DNS addition failed, use the table above for manual configuration.")
        else:
            print("\n❌ Could not find Cloudflare zone. Please check your domain configuration.")
    else:
        print("\n❌ Failed to create or retrieve Mailgun domain. Please check your API key and try again.")

if __name__ == "__main__":
    main()
