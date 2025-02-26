#!/bin/bash

# Stop all running Docker containers
echo "Stopping no-code-architects running Docker containers..."
docker stop $(docker ps -a --filter ancestor=no-code-architects-toolkit:testing --format="{{.ID}}")

# Build the Docker image
echo "Building Docker image..."
docker build -t no-code-architects-toolkit:testing .

# Read variables from .variables file
echo "Reading environment variables..."
VARS=$(cat .env_variables.json)

# Function to escape JSON strings for bash
escape_json() {
    echo "$1" | sed 's/"/\\"/g'
}

# Build the docker run command with environment variables
CMD="docker run -p 8080:8080"

# Add environment variables from JSON
for key in $(echo "$VARS" | jq -r 'keys[]'); do
    value=$(echo "$VARS" | jq -r --arg k "$key" '.[$k]')
    
    # Handle nested JSON (specifically for GCP_SA_CREDENTIALS)
    if [[ "$key" == "GCP_SA_CREDENTIALS" ]]; then
        value=$(echo "$VARS" | jq -r --arg k "$key" '.[$k]')
        value=$(escape_json "$value")
    fi
    
    CMD="$CMD -e $key=\"$value\""
done

# Complete the command
CMD="$CMD no-code-architects-toolkit:testing"

# Run the Docker container
echo "Running Docker container..."
eval "$CMD"