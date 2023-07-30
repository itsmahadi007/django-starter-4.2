#!/bin/bash

# Define an array with the options
options=("Database" "Migrations")

# Ask the user what action they would like to perform
echo "Please choose operation:"
select operation in "${options[@]}"; do
    case $operation in
        # If the user wants to handle database
        "Database")
            # Define an array with the options
            db_options=("Backup" "Restore")

            # Ask the user what action they would like to perform
            echo "Please choose action:"
            select action in "${db_options[@]}"; do
                case $action in
                    # If the user wants to perform a backup
                    "Backup")
                        echo "Starting backup..."
                        # Run the Docker Compose command to execute the backup

                        docker compose -f ./docker-compose.yml run --rm db-backup bash -c "mkdir -p /backup/db_backup && pg_dump -h db_cf -p 5436 -U postgres -d croud_funding > /backup/db_backup/db_backup_$(date +%Y-%m-%d_%H:%M:%S).sql"

                        echo "Backup completed."
                        break
                        ;;
                    # If the user wants to perform a restore
                    "Restore")
                        # Print out all sql files in the backup directory
                        backups=()
                        for file in ./backup/db_backup/*.sql; do
                            backups+=("$file")
                        done


                        if [ ${#backups[@]} -eq 0 ]; then
                            echo "No backups available."
                            exit 1
                        fi

                        echo "Please choose a backup to restore:"
                        select backup_file in "${backups[@]}"; do
                            if [ -z "$backup_file" ]; then
                                echo "Invalid selection."
                                continue
                            fi

                            backup_file_name=$(basename $backup_file)

                            echo "Starting restore..."
                            # Attempt to drop and recreate the database

                            if ! docker compose -f ./docker-compose.yml run --rm db-restore bash -c "psql -h db_cf -p 5436 -U postgres -c 'DROP DATABASE IF EXISTS croud_funding;' && psql -h db_cf -p 5436 -U postgres -c 'CREATE DATABASE croud_funding;'" ; then
                                echo "Error while trying to drop and recreate the database. It might be in use. Please make sure all connections are closed and try again."
                                exit 1
                            fi

                            # If dropping and recreating the database was successful, restore from the backup file
                            docker compose -f ./docker-compose.yml run --rm db-restore bash -c "psql -h db_cf -p 5436 -U postgres -d croud_funding < /backup/db_backup/$backup_file_name"
                            echo "Restore completed."

                            break
                        done
                        break
                        ;;
                    # If the user input was neither 'Backup' nor 'Restore'
                    *)
                        echo "Invalid option. Please choose either 'Backup' or 'Restore'."
                        ;;
                esac
            done
            break
            ;;
        # If the user wants to handle migrations
        "Migrations")
            source_dir=./apps
            date_time=$(date +Y:%Y-M:%m-D:%d_%H-%M-%S)
            backup_folder="backup/migration_backups"
            target_dir="$backup_folder/migration_backup_$date_time"
            dirs=("users_management" "authentication" "core_study_care" "notification_manager")
            migration_options=("Backup" "Restore")
            echo "Please choose action:"
            select action in "${migration_options[@]}"; do
                case $action in
                    "Backup")
                        mkdir -p $target_dir
                        for dir in ${dirs[@]}; do
                            if [ -d "$source_dir/$dir/migrations" ]; then
                                mkdir -p "$target_dir/$dir/migrations"
                                cp -r "$source_dir/$dir/migrations/"* "$target_dir/$dir/migrations/"
                            fi
                        done
                        zip -r "$target_dir.zip" "$target_dir"
                        rm -r "$target_dir"
                        echo "Backup operation completed successfully. The backup has been saved as $target_dir.zip"
                        break
                        ;;
                    "Restore")
                        echo "Please choose a backup to restore:"
                        select ZIP_FILE in $backup_folder/*.zip; do
                            unzip $ZIP_FILE
                            extracted_dir=${ZIP_FILE%.zip}
                            for dir in ${dirs[@]}; do
                                if [ -d "$extracted_dir/$dir/migrations" ]; then
                                    cp -r "$extracted_dir/$dir/migrations/"* "$source_dir/$dir/migrations/"
                                fi
                            done
                            rm -r "$extracted_dir"
                            echo "Restoration operation completed successfully."
                            break
                        done
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 1 for Backup or 2 for Restore."
                        ;;
                esac
            done
            break
            ;;
        *)
            echo "Invalid option. Please choose either 'Database' or 'Migrations'."
            ;;
    esac
done
