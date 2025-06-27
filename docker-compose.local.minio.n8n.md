# Local Development with MinIO and n8n

This setup provides a complete local development environment for the No Code Architect Toolkit with integrated MinIO S3-compatible storage and n8n workflow automation.

## What's Included

- **NCA Toolkit**: Built locally from source (no pre-built image required)
- **MinIO**: S3-compatible object storage with web console for local file management
- **n8n**: Workflow automation platform for connecting and orchestrating services
- **Custom Network**: All services communicate through a dedicated Docker network
- **Persistent Storage**: Data persists between container restarts

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- At least 2GB available RAM
- At least 5GB available disk space

---

## Quick Start

### 1. Prepare Environment Configuration

Copy the example environment file and customize it:

```bash
cp .env.local.minio.n8n.example .env.local.minio.n8n
```

Edit `.env.local.minio.n8n` with your preferred settings. The defaults work for most local development scenarios.

### 2. Start the Development Environment

```bash
docker compose -f docker-compose.local.minio.n8n.yml up -d
```

### 3. Access the Applications

Once all services are running, you can access:

- **NCA Toolkit API**: http://localhost:8080
- **n8n Workflow Interface**: http://localhost:5678
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin123`

### 4. Verify Setup

Test the NCA Toolkit API:

```bash
curl -H "x-api-key: local-dev-key-123" http://localhost:8080/v1/toolkit/test
```

---

## Environment Configuration

The `.env.local.minio.n8n` file contains all necessary configuration:

### Application Settings
```env
APP_NAME=NCAToolkit
APP_DEBUG=true
APP_DOMAIN=localhost:8080
APP_URL=http://localhost:8080
API_KEY=local-dev-key-123
```

### MinIO S3 Storage Settings
```env
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_REGION=us-east-1
S3_BUCKET_NAME=nca-toolkit-local
```

### n8n Configuration
```env
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://localhost:5678/
```

---

## Service Details

### NCA Toolkit (Port 8080)
- Built from local Dockerfile
- Connects to MinIO for file storage
- API accessible at http://localhost:8080
- Uses local development API key: `local-dev-key-123`

### MinIO (Ports 9000, 9001)
- **API Endpoint**: http://localhost:9000 (S3-compatible API)
- **Web Console**: http://localhost:9001
- **Bucket**: `nca-toolkit-local` (auto-created and configured as public)
- **Credentials**: minioadmin / minioadmin123

### n8n (Port 5678)
- **Web Interface**: http://localhost:5678
- **Webhook URL**: http://localhost:5678/
- **File Sharing**: `./local-files` directory mounted for easy file access
- Can connect to both NCA Toolkit and MinIO services

---

## Development Workflow

### Making Code Changes

1. **Edit source code** in your local directory
2. **Rebuild the NCA Toolkit container**:
   ```bash
   docker compose -f docker-compose.local.minio.n8n.yml build ncat
   docker compose -f docker-compose.local.minio.n8n.yml up -d
   ```

### Viewing Logs

```bash
# All services
docker compose -f docker-compose.local.minio.n8n.yml logs -f

# Specific service
docker compose -f docker-compose.local.minio.n8n.yml logs -f ncat
docker compose -f docker-compose.local.minio.n8n.yml logs -f minio
docker compose -f docker-compose.local.minio.n8n.yml logs -f n8n
```

### Managing Storage

#### Access MinIO Console
1. Open http://localhost:9001
2. Login with `minioadmin` / `minioadmin123`
3. Browse the `nca-toolkit-local` bucket
4. Upload/download files as needed

#### Reset MinIO Data
```bash
docker compose -f docker-compose.local.minio.n8n.yml down
docker volume rm no-code-architects-toolkit_minio_data
docker compose -f docker-compose.local.minio.n8n.yml up -d
```

---

## Service Communication

All services communicate through the `nca-network` Docker network:

- **n8n → NCA Toolkit**: `http://ncat:8080`
- **n8n → MinIO**: `http://minio:9000` (S3 API)
- **NCA Toolkit → MinIO**: `http://minio:9000` (internal network)

### n8n Integration with NCA Toolkit

#### Quick Test Setup

1. **Access n8n**: Open http://localhost:5678
2. **Create a new workflow**
3. **Add an HTTP Request node** with these settings:
   - **Method**: GET
   - **URL**: `http://ncat:8080/v1/toolkit/test`
   - **Headers**: 
     - Key: `x-api-key`
     - Value: `local-dev-key-123`

#### Example: Testing the Toolkit Connection

**HTTP Request Node Configuration:**
```json
{
  "method": "GET",
  "url": "http://ncat:8080/v1/toolkit/test",
  "headers": {
    "x-api-key": "local-dev-key-123"
  }
}
```

**Expected Response:**
```json
{
  "message": "NCA Toolkit is working correctly",
  "status": "success"
}
```

#### Example: Media Processing Workflow

**HTTP Request Node for Media Transcription:**
```json
{
  "method": "POST",
  "url": "http://ncat:8080/v1/media/transcribe",
  "headers": {
    "x-api-key": "local-dev-key-123",
    "Content-Type": "application/json"
  },
  "body": {
    "media_url": "https://example.com/audio.mp3",
    "language": "en",
    "response_format": "json"
  }
}
```

#### All Available NCA Toolkit Endpoints

Use the base URL `http://ncat:8080` with any of the API endpoints documented in the main README:

- `http://ncat:8080/v1/toolkit/test` - Test connection
- `http://ncat:8080/v1/media/transcribe` - Transcribe audio/video
- `http://ncat:8080/v1/video/caption` - Add captions to videos
- `http://ncat:8080/v1/image/screenshot/webpage` - Screenshot web pages
- And all other endpoints listed in the main documentation

#### Tips for n8n Integration

1. **Always use the internal network URL**: `http://ncat:8080` (not `http://localhost:8080`)
2. **Include the API key header**: `x-api-key: local-dev-key-123`
3. **For file uploads**: Use the MinIO integration or webhook URLs for large files
4. **Error handling**: Add error handling nodes to manage API timeouts or failures

---

## Data Persistence

The following data persists between container restarts:

- **Application Storage**: `storage` volume (`/app/storage`)
- **Application Logs**: `logs` volume (`/app/logs`)
- **MinIO Data**: `minio_data` volume
- **n8n Workflows**: `n8n_data` volume (`/home/node/.n8n`)
- **Shared Files**: `./local-files` directory

---

## Troubleshooting

### Services Won't Start
```bash
# Check service status
docker compose -f docker-compose.local.minio.n8n.yml ps

# View error logs
docker compose -f docker-compose.local.minio.n8n.yml logs
```

### Port Conflicts
If ports 8080, 5678, 9000, or 9001 are already in use, modify the port mappings in `docker-compose.local.minio.n8n.yml`:

```yaml
ports:
  - "8081:8080"  # Change 8080 to 8081
```

### MinIO Bucket Issues
The `minio-init` service automatically creates and configures the bucket. If issues occur:

```bash
# Restart the init service
docker compose -f docker-compose.local.minio.n8n.yml restart minio-init

# Check init logs
docker compose -f docker-compose.local.minio.n8n.yml logs minio-init
```

### API Authentication Errors
Ensure you're using the correct API key from `.env.local.minio.n8n`:
- Default: `local-dev-key-123`
- Header: `x-api-key: local-dev-key-123`

---

## Stopping the Environment

```bash
# Stop all services
docker compose -f docker-compose.local.minio.n8n.yml down

# Stop and remove volumes (deletes all data)
docker compose -f docker-compose.local.minio.n8n.yml down -v
```

---

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NCA Toolkit   │    │       n8n       │    │     MinIO       │
│   localhost:8080│◄──►│   localhost:5678│◄──►│  localhost:9000 │
│                 │    │                 │    │  (S3 API)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                      ┌─────────────────┐
                      │  MinIO Console  │
                      │  localhost:9001 │
                      └─────────────────┘
                                 │
                      ┌─────────────────┐
                      │  nca-network    │
                      │ (Docker Bridge) │
                      └─────────────────┘
```

This setup provides a complete local development environment with file storage, workflow automation, and the NCA Toolkit API all working together seamlessly.