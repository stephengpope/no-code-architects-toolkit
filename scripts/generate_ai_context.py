import os
from pathlib import Path

def get_file_structure(root_dir):
    file_structure = []
    # Directories to ignore
    ignore_dirs = {'.git', '.venv'}

    for root, dirs, files in os.walk(root_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        # Calculate the relative path from the root directory
        rel_path = os.path.relpath(root, root_dir)
        level = rel_path.count(os.sep)
        indent = ' ' * 4 * level
        file_structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            file_structure.append(f"{sub_indent}{f}")
    return '\n'.join(file_structure)

def read_readme(readme_path):
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "README.md file not found."

def generate_prompt(root_dir, readme_path):
    file_structure = get_file_structure(root_dir)
    readme_content = read_readme(readme_path)
    
    prompt = (
        "Act as an AI assistant to help develop the app with the below file structure:\n\n"
        f"{file_structure}\n\n"
        "Also consider the README.md file content, reproduced below:\n\n"
        f"{readme_content}"
    )
    return prompt

if __name__ == "__main__":
    # Assuming the script is located in the no-code-architects-toolkit directory
    root_directory = Path(__file__).parent.parent
    readme_path = root_directory / 'README.md'
    
    prompt = generate_prompt(root_directory, readme_path)
    
    # Define the output directory and file path
    output_dir = root_directory / 'scripts' / 'output'
    output_file = output_dir / 'ai-context.txt'
    
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the prompt to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(prompt)