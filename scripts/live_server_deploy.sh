#!/bin/bash

# Function to run development commands
run_dev() {
    docker compose -f docker-compose.yml run --rm app python manage.py makemigrations
    docker compose -f docker-compose.yml run --rm app python manage.py migrate
    docker compose -f docker-compose.yml run --rm app python manage.py collectstatic --noinput
    docker compose -f docker-compose.yml run --rm app python manage.py sample
}

# Function to run production commands
run_prod() {
    docker compose -f docker-compose.yml run --rm app python manage.py makemigrations
    docker compose -f docker-compose.yml run --rm app python manage.py migrate
    docker compose -f docker-compose.yml run --rm app python manage.py collectstatic --noinput
    docker compose -f docker-compose.yml run --rm app python manage.py sample
}

# Asking user for environment choice
echo "Choose the environment to run: [dev/prod]"
read environment

# Running commands based on the choice
if [ "$environment" = "dev" ]; then
    docker compose -f docker-compose.yml down
    docker system prune -a --volumes
    docker compose -f docker-compose.yml build
    run_dev
elif [ "$environment" = "prod" ]; then
    docker compose -f docker-compose.yml down
    docker system prune -a --volumes
    docker compose -f docker-compose.yml build
    run_prod
else
    echo "Invalid input. Please type 'dev' or 'prod'."
    exit 1
fi

# Starting the containers
if [ "$environment" = "dev" ]; then
    docker compose -f docker-compose.yml up -d
else
    docker compose -f docker-compose.yml up -d
fi
