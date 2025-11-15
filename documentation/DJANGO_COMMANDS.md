# Django Management Commands

## Migration Commands

### Create Migrations
```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migrations for a specific app
python manage.py makemigrations maths

# Create empty migration file
python manage.py makemigrations --empty maths

# Create migration with custom name
python manage.py makemigrations maths --name migration_name
```

### Apply Migrations
```bash
# Apply all pending migrations
python manage.py migrate

# Apply migrations for a specific app
python manage.py migrate maths

# Apply a specific migration
python manage.py migrate maths 0001_initial

# Show migration status without applying
python manage.py migrate --plan
```

### Rollback Migrations
```bash
# Rollback last migration for an app
python manage.py migrate maths zero

# Rollback to a specific migration
python manage.py migrate maths 0003_migration_name
```

### Migration Utilities
```bash
# Show migration status
python manage.py showmigrations

# Show migration status for specific app
python manage.py showmigrations maths

# List all migrations
python manage.py showmigrations --list
```

## Database Commands

### Database Operations
```bash
# Create database tables from models
python manage.py migrate

# Reset database (WARNING: deletes all data)
python manage.py flush

# Dump data to JSON
python manage.py dumpdata --indent 2 --output db_export.json

# Load data from JSON
python manage.py loaddata db_export.json

# Dump specific app
python manage.py dumpdata maths --indent 2

# Load specific fixture
python manage.py loaddata db_export_utf8.json
```

## Development Commands

### Run Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8000

# Run on specific IP and port
python manage.py runserver 0.0.0.0:8000
```

### Shell Commands
```bash
# Open Django shell
python manage.py shell

# Run Python code from command line
python manage.py shell -c "from maths.models import Level; print(Level.objects.count())"
```

### Admin Commands
```bash
# Create superuser
python manage.py createsuperuser

# Change password for user
python manage.py changepassword username
```

## Static Files

```bash
# Collect static files
python manage.py collectstatic

# Collect static files without confirmation
python manage.py collectstatic --no-input

# Clear collected static files
python manage.py collectstatic --clear
```

## Docker Commands (if using Docker)

```bash
# Run migrations in Docker
docker compose exec web python manage.py migrate

# Create migrations in Docker
docker compose exec web python manage.py makemigrations

# Run shell in Docker
docker compose exec web python manage.py shell

# Run any Django command in Docker
docker compose exec web python manage.py <command>
```

## Common Workflow

```bash
# 1. After changing models, create migrations
python manage.py makemigrations

# 2. Review the generated migration file (in migrations folder)

# 3. Apply migrations
python manage.py migrate

# 4. If using Docker
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```


