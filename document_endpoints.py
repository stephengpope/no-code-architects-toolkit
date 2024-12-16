import os
import sys
import json
import requests
from pathlib import Path

# The prompt template to send to Claude
CLAUDE_PROMPT = '''I am providing you with a Python file containing API endpoint definitions. Please read through the code, identify each endpoint, and generate detailed documentation for each in Markdown format as follows:
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

Here is the Python file to analyze:

{file_content}
'''

def call_claude_api(message: str, api_key: str) -> str:
    """Make a direct API call to Claude."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 4096,
        "temperature": 0,
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"API call failed with status {response.status_code}: {response.text}")
    
    return response.json()["content"][0]["text"]

def process_single_file(source_file: Path, output_path: Path, api_key: str):
    """Process a single Python file."""
    try:
        # Read the source file
        with open(source_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Create the full prompt
        message = CLAUDE_PROMPT.format(file_content=file_content)

        # Get documentation from Claude
        markdown_content = call_claude_api(message, api_key)

        # Create output file path
        if output_path.is_dir():
            output_file = output_path / source_file.with_suffix('.md').name
        else:
            output_file = output_path

        # Create necessary directories
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the markdown content (will overwrite if exists)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Generated documentation for: {source_file}")
        print(f"Output saved to: {output_file}")

    except Exception as e:
        print(f"Error processing {source_file}: {str(e)}", file=sys.stderr)

def process_directory(source_dir: Path, output_dir: Path, api_key: str):
    """Process all Python files in the source directory recursively."""
    # Walk through all files in source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                # Get the source file path
                source_file = Path(root) / file
                
                try:
                    # Calculate relative path to maintain directory structure
                    rel_path = source_file.relative_to(source_dir)
                    output_file = output_dir / rel_path.with_suffix('.md')

                    # Create necessary directories
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    # Process the file
                    process_single_file(source_file, output_file, api_key)

                except Exception as e:
                    print(f"Error processing {source_file}: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <source_path> <output_path> <api_key>")
        print("Note: source_path can be either a single .py file or a directory")
        sys.exit(1)
        
    source_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    api_key = sys.argv[3]

    # Validate source path exists
    if not source_path.exists():
        print(f"Error: Source path does not exist: {source_path}")
        sys.exit(1)

    # Validate source file is a Python file if it's a single file
    if source_path.is_file() and not source_path.suffix == '.py':
        print("Error: Source file must be a Python file (.py)")
        sys.exit(1)

    # Process based on source type
    if source_path.is_file():
        process_single_file(source_path, output_path, api_key)
    else:
        process_directory(source_path, output_path, api_key)

if __name__ == "__main__":
    main()