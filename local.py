import os
import json
import subprocess

# Read variables from .env_variables.json
with open('.env_variables.json') as f:
    vars = json.load(f)

# Function to escape JSON strings for bash
def escape_json(value):
    return value.replace('"', '\\"')

# Stop all running Docker containers
print("Stopping all running Docker containers...")
try:
    # List all container IDs
    result = subprocess.run("docker ps -aq", shell=True, check=True, capture_output=True, text=True)
    container_ids = result.stdout.strip().split('\n')
    
    # Stop each container
    for container_id in container_ids:
        if container_id:  # Ensure the container_id is not empty
            subprocess.run(f"docker stop {container_id}", shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error stopping containers: {e}")

# Build the Docker image
print("Building Docker image...")
subprocess.run("docker build -t no-code-architects-toolkit:testing .", shell=True, check=True)

# Build the docker run command with environment variables
cmd = "docker run -p 8080:8080"

# Add environment variables from JSON
for key, value in vars.items():
    # Handle nested JSON (specifically for GCP_SA_CREDENTIALS)
    if key == "GCP_SA_CREDENTIALS":
        value = escape_json(value)
    cmd += f' -e {key}="{value}"'

# Complete the command
cmd += " no-code-architects-toolkit:testing"

# Run the Docker container
print("Running Docker container...")
subprocess.run(cmd, shell=True, check=True)