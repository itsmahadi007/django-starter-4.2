#!/bin/bash

# Specify the folder where backups are stored
BACKUP_FOLDER="./backup_database"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_FOLDER

# Function to load environment variables and set Docker Compose file
load_env_and_set_compose_file() {
    if [ -f "$1" ]; then
        while read -r line || [[ -n "$line" ]]; do
            if [[ "$line" =~ ^[[:space:]]*# ]]; then continue; fi
            export "$line"
        done < "$1"
        if [ "$2" = "dev" ]; then
            COMPOSE_FILE="docker-compose.dev.yml"
        else
            COMPOSE_FILE="docker-compose.prod.yml"
        fi
    else
        echo "Environment file $1 not found!"
        exit 1
    fi
}

# Ask the user which environment to operate on
echo "Select the environment:"
echo "1. Development"
echo "2. Production"
read -p "Enter your choice for environment (1 or 2): " env_choice

# Set environment-specific variables
ENV_SUFFIX=""
if [ "$env_choice" = "1" ]; then
    load_env_and_set_compose_file ".env.dev" "dev"
    ENV_SUFFIX="dev"
    ENV_BACKUP_SUFFIX="dev_db_backup"
    ENV_RESTORE_SUFFIX="dev_db_restore"
elif [ "$env_choice" = "2" ]; then
    load_env_and_set_compose_file ".env.prod" "prod"
    ENV_SUFFIX="prod"
    ENV_BACKUP_SUFFIX="prod_db_backup"
    ENV_RESTORE_SUFFIX="prod_db_restore"
else
    echo "Invalid environment choice. Please enter 1 for Development or 2 for Production."
    exit 1
fi

# Ask the user what action they would like to perform
echo "Please choose operation:"
echo "1. Backup"
echo "2. Restore"
read -p "Enter your choice (1 or 2): " action_choice

# Perform the action based on user input
case $action_choice in
    1)  # Backup operation
        echo "Starting backup..."
        BACKUP_FILE="$BACKUP_FOLDER/backup_${ENV_SUFFIX}_$(date +%Y-%m-%d_%H-%M-%S).sql"
        docker compose -f $COMPOSE_FILE run --rm $ENV_BACKUP_SUFFIX bash -c "pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > /backup/$(basename $BACKUP_FILE)"
        echo "Backup completed. File saved as $BACKUP_FILE"
        ;;
    2)  # Restore operation
        echo "Please choose a backup to restore:"
        select BACKUP_FILE in $BACKUP_FOLDER/*.sql; do
            if [ ! -f "$BACKUP_FILE" ]; then
                echo "File does not exist, try again."
                continue
            fi
            echo "Starting restore..."

            if ! docker compose -f $COMPOSE_FILE run --rm $ENV_RESTORE_SUFFIX bash -c "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c 'DROP DATABASE IF EXISTS $DB_NAME;' && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c 'CREATE DATABASE $DB_NAME;'" ; then
                echo "Error while trying to drop and recreate the database. It might be in use. Please make sure all connections are closed and try again."
                exit 1
            fi

            BACKUP_FILE_NAME=$(basename $BACKUP_FILE)
            docker compose -f $COMPOSE_FILE run --rm $ENV_RESTORE_SUFFIX bash -c "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < /backup/$BACKUP_FILE_NAME"

            echo "Restore completed."
            break
        done
        ;;
    *)  # Invalid choice
        echo "Invalid choice. Please enter 1 for Backup or 2 for Restore."
        ;;
esac

# To use this script:
# 1. Make sure it has execute permissions:
#       chmod +x backup_restore.sh
# 2. Run the script using:
#       ./backup_restore.sh
# 3. Follow the on-screen instructions
