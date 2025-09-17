def load_config(env_file='.env'):
    """Load configuration from a .env file."""
    config = {}
    try:
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    except FileNotFoundError:
        print(f"Warning: {env_file} not found. Using default configuration.")
    return config

def get_api_keys(config):
    """Retrieve API keys from the configuration."""
    return {
        'MAILGUN_API_KEY': config.get('MAILGUN_API_KEY'),
        'CLOUDFLARE_API_KEY': config.get('CLOUDFLARE_API_KEY'),
        'CLOUDFLARE_EMAIL': config.get('CLOUDFLARE_EMAIL')
    }