#!/bin/bash
set -e

IMAGE_NAME="cloudflare-ddns"
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Creating sample $ENV_FILE..."
    cat <<EOL > "$ENV_FILE"
# Cloudflare DDNS configuration
# Fill in the values below before running the container

# The DNS record you want to update, e.g. "api.example.com"
CLOUDFLARE_DNS_RECORD=

# Your Cloudflare API token with DNS edit permissions
CLOUDFLARE_API_TOKEN=
EOL
    echo "$ENV_FILE created. Please fill in the values and re-run this script."
    exit 0
fi

docker build -t $IMAGE_NAME .
docker run -d --env-file "${ENV_FILE}" "${IMAGE_NAME} --autostart"
