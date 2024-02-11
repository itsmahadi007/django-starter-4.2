#!/bin/bash

# Your source directory
SOURCE_DIR=./apps

# Your target directory
DATE_TIME=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FOLDER="backup_migrations"

# Ask the user which environment to operate on
echo "Select the environment:"
echo "1. Development"
echo "2. Production"
read -p "Enter your choice for environment (1 or 2): " env_choice

# Set environment-specific suffix for the file name
ENV_SUFFIX=""
if [ "$env_choice" = "1" ]; then
    ENV_SUFFIX="dev"
elif [ "$env_choice" = "2" ]; then
    ENV_SUFFIX="prod"
else
    echo "Invalid environment choice. Please enter 1 for Development or 2 for Production."
    exit 1
fi

TARGET_DIR="$BACKUP_FOLDER/migration_backup_${ENV_SUFFIX}_$DATE_TIME"

# The directories you want to handle
DIRS=("users_management" "authentication" "croud_founding" "notification_manager")

echo "Please choose operation:"
echo "1. Backup"
echo "2. Restore"
echo "3. Remove Migrations files"
read -p "Enter your choice (1, 2, or 3): " choice

case $choice in
    1)  # Backup operation
        # Create target directory if it doesn't exist
        mkdir -p $TARGET_DIR

        # Loop through each specified directory
        for dir in ${DIRS[@]}; do
            # Check if migrations subdirectory exists
            if [ -d "$SOURCE_DIR/$dir/migrations" ]; then
                # Create the directory structure in the target directory
                mkdir -p "$TARGET_DIR/$dir/migrations"

                # Copy the migrations directory
                cp -r "$SOURCE_DIR/$dir/migrations/"* "$TARGET_DIR/$dir/migrations/"
            fi
        done

        echo "Backup operation completed successfully."

        # Compress the backup directory
        zip -r "$TARGET_DIR.zip" "$TARGET_DIR"

        # Remove the original directory after compression
        rm -r "$TARGET_DIR"

        echo "Backup operation completed successfully. The backup has been saved as $TARGET_DIR.zip"
        ;;
    2)  # Restore operation
        echo "Please choose a backup to restore:"
        select ZIP_FILE in $BACKUP_FOLDER/*.zip; do
            # Extract the zip file
            unzip $ZIP_FILE

            # Get the name of the extracted directory
            EXTRACTED_DIR=${ZIP_FILE%.zip}

            # Loop through each specified directory
            for dir in ${DIRS[@]}; do
                # Check if migrations subdirectory exists in the extracted directory
                if [ -d "$EXTRACTED_DIR/$dir/migrations" ]; then
                    # Copy the migrations directory back to the source directory
                    cp -r "$EXTRACTED_DIR/$dir/migrations/"* "$SOURCE_DIR/$dir/migrations/"
                fi
            done

            # Remove the extracted directory after copying files
            rm -r "$EXTRACTED_DIR"

            echo "Restoration operation completed successfully."
            break
        done
        ;;
    3)  # Remove operation
        echo "Removing Files:"
        if [ -d "./media/" ] && [ "$(ls -A ./media/)" ]; then
          rm -r ./media/*
          echo "Deleted Media Files!"
        else
          echo "./media/ is empty or does not exist, skipping delete."
        fi

        for dir in ${DIRS[@]}; do
            if [ -d "$SOURCE_DIR/$dir/migrations" ]; then
                rm -r "$SOURCE_DIR/$dir/migrations/"*
                touch "$SOURCE_DIR/$dir/migrations/__init__.py"
            fi
        done
        echo "Migrations files removed and __init__.py files recreated successfully."
        ;;
    *)  # Invalid choice
        echo "Invalid choice. Please enter 1 for Backup or 2 for Restore."
        ;;
esac
