#!/bin/bash

# Check if a folder was passed as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/folder"
    exit 1
fi

# Assign the folder path to a variable
FOLDER_PATH="$1"

# Check if the provided path is a directory
if [ ! -d "$FOLDER_PATH" ]; then
    echo "Error: $FOLDER_PATH is not a directory"
    exit 1
fi

# Find all .py files in the directory and its subdirectories
find "$FOLDER_PATH" -type f -name "*.py" | while read -r FILE; do
    echo "Contents of $FILE:"
    cat "$FILE"
    echo "---------------------------------"
done
