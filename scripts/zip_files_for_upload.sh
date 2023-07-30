# zip -r ../Archive.zip $(find . -type d \( -name "venv" -o -name "__pycache__" -o -name ".git" \) -prune -o -type f -print)


#!/bin/bash

# Remove the old Archive.zip if it exists
rm -f ./Archive.zip
# Find and zip files individually, excluding certain directories
find . -type d \( -name "venv" -o -name "__pycache__" -o -name ".git" -o -name "all_backup" -o -name "dbbackup" \) -prune -o -type f -exec zip -r ./Archive.zip {} \;
