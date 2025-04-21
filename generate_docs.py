# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import sys
import json
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta

def load_config():
    """Load configuration from env_shell.json file."""
    config_path = Path(__file__).parent / '.env_shell.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('ANTHROPIC_API_KEY'), config.get('API_DOC_OUTPUT_DIR')
    except FileNotFoundError:
        print(f"Error: Configuration file not found at: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file: {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        sys.exit(1)

def load_app_context():
    """Load the app.py file from the root of the repository."""
    try:
        # Get the root directory by going up from the current file's location
        root_dir = Path(__file__).parent.parent
        app_path = Path(__file__).parent / 'app.py'
        
        if not app_path.exists():
            print("Warning: app.py not found in repository root. Documentation will be generated without API context.")
            return None
            
        with open(app_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not load app.py: {str(e)}")
        return None

# The prompt template to send to Claude
CLAUDE_PROMPT = '''

    I am providing you with a Python file containing API endpoint definitions.
    
    First, here is the main application context from app.py that shows how the API is structured and handled:

** app.py below

{app_context}

** app.py DONE

    Now, please read through the following endpoint code and analyze it in the context of the main application:

**endpoint below

{file_content}

    Please generate detailed documentation in Markdown format as follows:

    1. Overview: Describe the purpose of the endpoint and how it fits into the overall API structure shown in app.py.
    2. Endpoint: Specify the URL path and HTTP method.
    3. Request:
    - Headers: List any required headers, such as the x-api-key headers.
    - Body Parameters: List the required and optional parameters, including the parameter type and purpose.
    - Specifically study the validate_payload directive in the routes file to build the documentation
    - Example Request: Provide a sample request payload and a sample curl command.
    4. Response:
    - Success Response: Reference the endpoint and general response from the app.py to show a full sample response from the api
    - Error Responses: Include examples of common error status codes, with example JSON responses for each.
    5. Error Handling: 
    - Describe common errors, like missing or invalid parameters, and indicate which status codes they produce
    - Include any specific error handling from the main application context
    6. Usage Notes: Any additional notes on using the endpoint effectively.
    7. Common Issues: List any common issues a user might encounter.
    8. Best Practices: Any recommended best practices for this endpoint.
    
    Format the documentation with markdown headings, bullet points, and code blocks.
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

def should_skip_doc_generation(output_file: Path, force: bool = False) -> bool:
    """
    Check if documentation was updated in the last 24 hours.
    
    Args:
        output_file: Path to the output markdown file
        force: If True, always return False to force generation
        
    Returns:
        bool: True if file was updated in the last 24 hours and not forced, False otherwise
    """
    # If force flag is provided, never skip
    if force:
        return False
        
    if not output_file.exists():
        return False
        
    # Get file modification time
    mod_time = datetime.fromtimestamp(output_file.stat().st_mtime)
    
    # Check if file was modified in the last 24 hours
    time_threshold = datetime.now() - timedelta(hours=24)
    
    return mod_time > time_threshold

def process_single_file(source_file: Path, output_path: Path, api_key: str, force: bool = False):
    """
    Process a single Python file.
    
    Args:
        source_file: Path to the source Python file
        output_path: Path to output the markdown file
        api_key: Anthropic API key
        force: If True, generate docs even if they were updated recently
    """
    try:
        # Create output file path
        if output_path.is_dir():
            output_file = output_path / source_file.with_suffix('.md').name
        else:
            output_file = output_path
            
        # Check if docs were recently updated
        if should_skip_doc_generation(output_file, force):
            print(f"Skipping {source_file} - documentation updated within the last 24 hours")
            return
            
        # Read the source file
        with open(source_file, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Load app.py context
        app_context = load_app_context()
        if app_context is None:
            app_context = "No app.py context available."

        # Create the full prompt
        message = CLAUDE_PROMPT.format(
            app_context=app_context,
            file_content=file_content
        )

        # Get documentation from Claude
        markdown_content = call_claude_api(message, api_key)

        # Create necessary directories
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the markdown content (will overwrite if exists)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Generated documentation for: {source_file}")
        print(f"Output saved to: {output_file}")

    except Exception as e:
        print(f"Error processing {source_file}: {str(e)}", file=sys.stderr)

def process_directory(source_dir: Path, output_dir: Path, api_key: str, force: bool = False):
    """Process all Python files in the source directory recursively."""
    # Track statistics
    total_files = 0
    processed_files = 0
    skipped_files = 0
    error_files = 0
    
    start_time = time.time()
    
    # Walk through all files in source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                # Get the source file path
                source_file = Path(root) / file
                total_files += 1
                
                try:
                    # Calculate relative path to maintain directory structure
                    rel_path = source_file.relative_to(source_dir)
                    output_file = output_dir / rel_path.with_suffix('.md')

                    # Create necessary directories
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Check if we should skip this file
                    if should_skip_doc_generation(output_file, force):
                        print(f"Skipping {source_file} - documentation updated within the last 24 hours")
                        skipped_files += 1
                        continue

                    # Process the file
                    process_single_file(source_file, output_file, api_key, force)
                    processed_files += 1

                except Exception as e:
                    print(f"Error processing {source_file}: {str(e)}", file=sys.stderr)
                    error_files += 1
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\nDocumentation Generation Summary:")
    print(f"Total Python files found: {total_files}")
    print(f"Files processed: {processed_files}")
    print(f"Files skipped (updated in last 24h): {skipped_files}")
    print(f"Files with errors: {error_files}")
    print(f"Total time: {elapsed_time:.2f} seconds")

def main():
    # Check if --force flag is provided
    force_generation = False
    source_path_arg = None
    
    for arg in sys.argv[1:]:
        if arg == "--force":
            force_generation = True
        else:
            source_path_arg = arg
    
    if not source_path_arg:
        print("Usage: python script.py <source_path> [--force]")
        print("Note: source_path can be either a single .py file or a directory")
        print("Options:")
        print("  --force: Generate documentation even if it was updated within 24 hours")
        print("\nPlease ensure .env_shell.json exists in the same directory with:")
        print("  ANTHROPIC_API_KEY: Your Anthropic API key")
        print("  API_DOC_OUTPUT_DIR: Directory where documentation will be saved")
        sys.exit(1)

    # Load configuration from JSON file
    api_key, output_dir = load_config()

    # Validate configuration
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in configuration file")
        sys.exit(1)

    if not output_dir:
        print("Error: API_DOC_OUTPUT_DIR not found in configuration file")
        sys.exit(1)

    output_path = Path(output_dir)
        
    # Get and validate source path
    source_path = Path(source_path_arg)
    
    if not source_path.exists():
        print(f"Error: Source path does not exist: {source_path}")
        sys.exit(1)

    if source_path.is_file() and not source_path.suffix == '.py':
        print("Error: Source file must be a Python file (.py)")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Starting documentation generation...")
    print(f"Source: {source_path}")
    print(f"Output: {output_path}")
    if force_generation:
        print(f"Force flag enabled: Will generate all documentation regardless of last update time.\n")
    else:
        print(f"Note: Files updated within the last 24 hours will be skipped (use --force to override).\n")
    
    # Process based on source type
    if source_path.is_file():
        # For a single file
        output_file = output_path / source_path.with_suffix('.md').name if output_path.is_dir() else output_path
        
        # Check if should skip
        if should_skip_doc_generation(output_file, force_generation):
            print(f"Skipping {source_path} - documentation updated within the last 24 hours")
        else:
            process_single_file(source_path, output_path, api_key, force_generation)
    else:
        process_directory(source_path, output_path, api_key, force_generation)

if __name__ == "__main__":
    main()