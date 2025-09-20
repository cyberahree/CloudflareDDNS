# Exit on any error
$ErrorActionPreference = "Stop"

$ImageName = "cloudflare-ddns"
$EnvFile = ".env"

# Create a sample .env file if it doesn't exist
if (-Not (Test-Path $EnvFile)) {
    Write-Host "Creating sample $EnvFile..."
    @"
# Cloudflare DDNS configuration
# Fill in the values below before running the container

# The DNS record you want to update, e.g. "api.example.com"
CLOUDFLARE_DNS_RECORD=

# Your Cloudflare API token with DNS edit permissions
CLOUDFLARE_API_TOKEN=
"@ | Out-File -Encoding UTF8 $EnvFile

    Write-Host "$EnvFile created. Please fill in the values and re-run this script."
    exit
}

# Build the Docker image
Write-Host "Building Docker image '$ImageName'..."
docker build -t $ImageName .

# Run the container with the env file
Write-Host "Running Docker container '$ImageName' with env file '$EnvFile'..."
docker run -d --env-file $EnvFile $ImageName
