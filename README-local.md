# Local Development Setup

This setup provides a local development environment for the No Code Architect Toolkit using Docker Compose with MinIO for S3-compatible storage.

## What's Included

- **NCA Toolkit**: Built locally from Dockerfile (no pre-built image)
- **MinIO**: S3-compatible object storage with web console
- **No SSL/Traefik**: Simplified setup for local development

## Quick Start

1. **Start the local environment:**
   ```bash
   docker compose -f docker-compose.local.yml up -d
   ```

2. **Access the applications:**
   - **NCA Toolkit**: http://localhost:8080
   - **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin123)

3. **View logs:**
   ```bash
   docker compose -f docker-compose.local.yml logs -f
   ```

4. **Stop the environment:**
   ```bash
   docker compose -f docker-compose.local.yml down
   ```

## Configuration

### Environment Variables
All configuration is in `.env.local`:
- **API_KEY**: `local-dev-key-123`
- **S3 Storage**: Configured for local MinIO instance
- **Debug Mode**: Enabled for development

### MinIO Setup
- **Access Key**: `minioadmin`
- **Secret Key**: `minioadmin123`
- **Bucket**: `nca-toolkit-local` (auto-created)
- **Endpoint**: `http://minio:9000` (internal) / `http://localhost:9000` (external)

## Data Persistence

- **Application storage**: Persisted in `storage` volume
- **Application logs**: Persisted in `logs` volume  
- **MinIO data**: Persisted in `minio_data` volume

## Troubleshooting

### Rebuild Application
```bash
docker compose -f docker-compose.local.yml build ncat
docker compose -f docker-compose.local.yml up -d
```

### Reset MinIO Data
```bash
docker compose -f docker-compose.local.yml down
docker volume rm no-code-architects-toolkit_minio_data
docker compose -f docker-compose.local.yml up -d
```

### View MinIO Bucket
1. Open http://localhost:9001
2. Login with `minioadmin` / `minioadmin123`
3. Browse the `nca-toolkit-local` bucket

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   NCA Toolkit   │    │     MinIO       │
│   localhost:8080│────│  localhost:9000 │
│                 │    │  (S3 API)       │
└─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │  MinIO Console  │
                       │  localhost:9001 │
                       └─────────────────┘
```

The setup uses a custom Docker network (`nca-network`) for service communication and exposes only necessary ports to the host.