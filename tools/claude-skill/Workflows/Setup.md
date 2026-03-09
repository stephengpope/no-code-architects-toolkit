---
workflow: setup
purpose: Authenticate with NCA Toolkit API and save credentials to ~/.nca-toolkit/config
---

# Setup & Authenticate

**Purpose:** Connect to an NCA Toolkit API instance by validating credentials and saving them to the local config file.

## Steps

### Step 1: Check if already configured

```bash
python3 tools/nca.py config
```

If config exists and user wants to keep it, skip to testing.

### Step 2: Run interactive setup

Ask the user for their API URL and API key, then run:

```bash
python3 tools/nca.py connect
```

This will:
1. Prompt for the API URL (e.g., `https://nca-toolkit-xxxxx.run.app`)
2. Prompt for the API key
3. Validate by calling the `/v1/toolkit/test` endpoint
4. Save credentials to `~/.nca-toolkit/config` with 600 permissions

### Step 3: Verify connectivity

```bash
python3 tools/nca.py test
```

### Step 4: Show saved config

```bash
python3 tools/nca.py config
```

## Config File

Credentials are stored at `~/.nca-toolkit/config` in INI format:

```ini
[default]
api_url = "https://your-nca-instance.run.app"
api_key = "your_api_key"
```

- File permissions: `600` (owner read/write only)
- Directory permissions: `700` (owner only)
- Supports multiple profiles via `--profile <name>`

## Non-Interactive Setup

For automation, set environment variables instead:

```bash
export NCA_API_URL=https://your-nca-instance.run.app
export NCA_API_KEY=your_api_key
```

Environment variables take priority over the config file.

## Multiple Profiles

```bash
python3 tools/nca.py connect --profile staging
python3 tools/nca.py connect --profile production
```
