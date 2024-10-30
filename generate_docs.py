import os
import sys
import requests

# Set up Anthropic API key from environment variables
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
api_url = "https://api.anthropic.com/v1/complete"  # Update if Claude's endpoint changes

# Prompt template to guide Claude
base_prompt = """
I am providing you with a Python file containing API endpoint definitions. Please read through the code, identify each endpoint, and generate detailed documentation for each in Markdown format as follows:

1. Overview: Describe the purpose of the endpoint.
2. Endpoint: Specify the URL path and HTTP method.
3. Request:
   - Headers: List any required headers, such as authentication headers.
   - Body Parameters: List the required and optional parameters, including the parameter type and purpose.
   - Example Request: Provide a sample request payload and a sample curl command.
4. Response:
   - Success Response: Show the status code, and provide an example JSON response for a successful request.
   - Error Responses: Include examples of common error status codes, with example JSON responses for each.
5. Error Handling: Describe common errors, like missing or invalid parameters, and indicate which status codes they produce.
6. Usage Notes: Any additional notes on using the endpoint effectively.
7. Common Issues: List any common issues a user might encounter.
8. Best Practices: Any recommended best practices for this endpoint.

Format the documentation with markdown headings, bullet points, and code blocks, and ensure it matches the following example structure:

# `/example-endpoint` API Documentation

## Overview
[Description of the endpoint's purpose]

...

Repeat this structure for each API endpoint you find in the Python file. Provide each endpoint’s documentation as a separate Markdown file, with file names corresponding to the endpoint (e.g., example-endpoint.md).
"""

# Function to generate documentation for a single Python file
def generate_documentation(file_path):
    # Read the content of the Python file
    with open(file_path, "r") as file:
        file_content = file.read()
    
    # Make a request to Claude
    headers = {
        "x-api-key": anthropic_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": base_prompt + "\n\n" + file_content,
        "model": "claude-2",  # or the specific Claude model version you are using
        "max_tokens_to_sample": 2000,
        "temperature": 0.5,
        "stop_sequences": ["\n\n"]
    }
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return

    # Retrieve the generated documentation text
    documentation = response.json().get("completion", "").strip()
    
    # Create a markdown file with the same base name as the Python file in the docs folder
    output_file = os.path.join("docs", f"{os.path.splitext(os.path.basename(file_path))[0]}.md")
    os.makedirs("docs", exist_ok=True)
    with open(output_file, "w") as doc_file:
        doc_file.write(documentation)
    
    print(f"Documentation for '{file_path}' saved to '{output_file}'.")


if __name__ == "__main__":
    file_path = sys.argv[1]
    generate_documentation(file_path)
