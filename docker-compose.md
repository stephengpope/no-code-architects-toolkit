# Install No Code Architect Toolkit with Docker

Installation of No Code Architect Toolkit with Docker offers the following advantages:
- Install No Code Architect Toolkit in a clean environment.
- Simplify the setup process.
- Avoid compatibility issues across different operating systems with Docker's consistent environment.

> **Info**  
> If your domain/subdomain is already pointed to the server, start at step 2.  
> If you have already installed Docker and Docker-Compose, start at step 3.

---

## 1. DNS Setup

Point your domain/subdomain to the server. Add an A record to route the domain/subdomain accordingly:

- **Type**: A  
- **Name**: The desired domain/subdomain  
- **IP Address**: `<IP_OF_YOUR_SERVER>`  

---

## 2. Install Docker

This can vary depending on the Linux distribution used. Below are instructions for Ubuntu:

### Set up Docker's APT Repository

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to APT sources:
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Install the Docker Packages

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

## 3. Create Docker Compose File

Create a `docker-compose.yml` file and paste the following configuration:

### With SSL Support
Enables SSL/TLS for secure, encrypted communications. Ideal for those wanting a hands-off approach to SSL setup.

```yaml
services:
  traefik:
    image: "traefik"
    restart: unless-stopped
    command:
      - "--api=true"
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.mytlschallenge.acme.tlschallenge=true"
      - "--certificatesresolvers.mytlschallenge.acme.email=${SSL_EMAIL}"
      - "--certificatesresolvers.mytlschallenge.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - traefik_data:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro
  ncat:
    image: stephengpope/no-code-architects-toolkit:latest
    env_file:
      - .env
    labels:
      - traefik.enable=true
      - traefik.http.routers.ncat.rule=Host(`${APP_DOMAIN}`)
      - traefik.http.routers.ncat.tls=true
      - traefik.http.routers.ncat.entrypoints=web,websecure
      - traefik.http.routers.ncat.tls.certresolver=mytlschallenge
    volumes:
      - storage:/var/www/html/storage/app
      - logs:/var/www/html/storage/logs
    restart: unless-stopped

volumes:
  traefik_data:
    driver: local
  storage:
    driver: local
  logs:
    driver: local
```

---

## 4. Create `.env` File

Create an `.env` file and configure it accordingly:

```env
# The name of your application.
APP_NAME=NCAToolkit

# Debug mode setting. Set to `false` for production environments.
APP_DEBUG=false

# Your app's domain or subdomain, without the 'http://' or 'https://' prefix.
APP_DOMAIN=example.com

# Full application URL is automatically configured; no modification required.
APP_URL=https://${APP_DOMAIN}

# SSL settings
SSL_EMAIL=user@example.com

# API_KEY
# Purpose: Used for API authentication.
# Requirement: Mandatory.
API_KEY=your_api_key_here

# s3 Compatible Storage Env Vars
#
#S3_ACCESS_KEY=your_access_key
#S3_SECRET_KEY=your_secret_key
#S3_ENDPOINT_URL=https://your-endpoint-url
#S3_REGION=your-region
#S3_BUCKET_NAME=your-bucket-name


# Google Cloud Storage Env Variables
#
# GCP_SA_CREDENTIALS
# Purpose: The JSON credentials for the GCP Service Account.
# Requirement: Mandatory if using GCP storage.
#GCP_SA_CREDENTIALS=/path/to/your/gcp/service_account.json

# GCP_BUCKET_NAME
# Purpose: The name of the GCP storage bucket.
# Requirement: Mandatory if using GCP storage.
#GCP_BUCKET_NAME=your_gcp_bucket_name

# STORAGE_PATH
# Purpose: The base path for storage operations.
# Default: GCP
# Requirement: Optional.
#STORAGE_PATH=GCP

```

---

## 5. Start Docker Compose

Start No Code Architect Toolkit  using the following command:

```bash
docker compose up -d
```

To view logs in real time:

```bash
docker compose logs -f
```

To stop the containers:

```bash
docker compose stop
```

To restart and reload env vars

# First update your .env file with the correct values
# Then run:

```bash
docker compose up -d --force-recreate ncat
```

---

## 6. Done

No Code Architect Toolkit is now accessible through the specified APP_URL. For example:  
[https://example.com](https://example.com)
