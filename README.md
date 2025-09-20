# CloudflareDDNS
A (decently) light-weight Cloudflare DDNS updater that automatically keeps a DNS A record in sync with your public IP.

Useful if you're hosting something at home.

## Features
- Automatically detects a change in your IPV4 address and reconfigures a DNS A record
- Supports configurable update intervals and debug logging
- Super cool

## Requirements
- Python 3
- Cloudflare API (with access to edit DNS records)
- (Optional) Docker

## Setup
1. Clone the Repository
```bash
git clone https://github.com/cyberahree/cloudflareddns.git
cd cloudflareddns
```

2. Create a .env file
```.env
CLOUDFLARE_DNS_RECORD=api.example.com
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
```

3. Install dependencies
```py
pip install -r requirements.txt
```

4. Run it!!
```bash
# start with default timer (1800s) and no debug
python main.py --autostart

# start with a custom timer, e.g., update every 60 seconds
python main.py --autostart --timer 60

# enable debug logging
python main.py --autostart --debug True
```

## Docker Usage
Use either `./start.sh` or `./start.ps1` (depending on your operating system, Linux/macOS or Windows PS respectively)

If a .env file does not already exist, one will be generated automatically; 
Fill this out first before you run it again

With Docker, the CLI options are passed after the image name:
```docker
# run with autostart and default timer
docker run --env-file .env cloudflare-ddns --autostart

# run with custom timer
docker run --env-file .env cloudflare-ddns --autostart --timer 60

# enable debug
docker run --env-file .env cloudflare-ddns --autostart --debug True
```
