docker compose down
docker system prune -a --volumes
docker compose build
docker compose run app python manage.py makemigrations
docker compose run app python manage.py migrate
docker compose run app python manage.py sample
docker compose up -d
