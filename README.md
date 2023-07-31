# My Awesome Project

Behold My Awesome Project!

License: MIT

Run it with Uvicorn:

```bash
uvicorn backend.asgi:application --reload --host 0.0.0.0 --port 8000
```

```sh
# to backup database
docker compose --profile backup up
*** or ***
docker compose run --rm db-backup bash -c "pg_dump -h db -p 5436 -U postgres -d django_db > /backup/backup_$(date +%Y-%m-%d_%H:%M:%S).sql"

# to restore database
docker compose --profile restore up
*** or ***
docker compose run --rm db-restore bash -c "psql -h db -p 5436 -U postgres -c 'DROP DATABASE IF EXISTS django_db;' &&
  psql -h db -p 5436 -U postgres -c 'CREATE DATABASE django_db;' &&
  psql -h db -p 5436 -U postgres -d django_db < /backup/your_backup_file.sql"

```