# Database Backup and Restore Guide

This guide explains how to backup your production database and restore it locally.

## Method 1: Using Django's dumpdata/loaddata (Recommended)

This method works for any database type (MySQL, SQLite, PostgreSQL) and is the easiest approach.

### Step 1: Backup Production Database

**On your production server (PythonAnywhere):**

```bash
# SSH into your production server, then:
cd /home/yourusername/path/to/CWA_SCHOOL
python backup_production_db.py
```

This will create a backup file in the `backups/` directory with a timestamp, like:
- `backups/production_backup_20241215_143022.json`

### Step 2: Download the Backup File

**Option A: Using PythonAnywhere File Browser**
1. Log into PythonAnywhere
2. Go to Files tab
3. Navigate to `backups/` directory
4. Download the latest backup file

**Option B: Using SCP (from your local machine)**
```bash
scp yourusername@ssh.pythonanywhere.com:/home/yourusername/path/to/CWA_SCHOOL/backups/production_backup_*.json ./
```

### Step 3: Restore to Local Database

**On your local machine:**

```bash
# Make sure you're using SQLite locally (no MYSQL_HOST in .env)
# Then restore:
python restore_local_db.py backups/production_backup_20241215_143022.json
```

**Note:** The restore script will:
1. Ask for confirmation (type 'YES')
2. Flush your local database (delete all existing data)
3. Load the production data

## Method 2: Using mysqldump (MySQL-specific)

If you want a raw SQL dump instead of JSON:

### Step 1: Backup on Production

**On production server:**
```bash
# Get your MySQL credentials from .env or settings
mysqldump -u YOUR_MYSQL_USER -p YOUR_DATABASE_NAME > production_backup.sql
```

### Step 2: Restore to Local MySQL (if using Docker)

**If you're using MySQL locally with Docker:**
```bash
# Copy the SQL file into the container
docker cp production_backup.sql cwa_mysql:/tmp/backup.sql

# Restore
docker exec -i cwa_mysql mysql -u cwa_user -pcwa_password cwa_school < /tmp/backup.sql
```

**Or from your local machine:**
```bash
docker exec -i cwa_mysql mysql -u cwa_user -pcwa_password cwa_school < production_backup.sql
```

## Method 3: Manual Django Commands

### Backup on Production:
```bash
python manage.py dumpdata --indent 2 --exclude contenttypes --exclude sessions --output backup.json
```

### Restore Locally:
```bash
# Flush existing data
python manage.py flush --noinput

# Load backup
python manage.py loaddata backup.json
```

## Important Notes

1. **Media Files**: The database backup does NOT include uploaded images/files. You'll need to download the `media/` directory separately if you need the images.

2. **User Accounts**: If you restore production data locally, you'll have production user accounts. You may want to create a new superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. **Database Size**: Large databases may take several minutes to backup/restore. Be patient!

4. **Backup Regularly**: Consider setting up automated backups on production.

## Troubleshooting

### "No such file or directory" error
- Make sure the backup file path is correct
- Use absolute paths if relative paths don't work

### "IntegrityError" during restore
- This usually means there are foreign key constraints
- Try excluding more apps: `--exclude auth.permission --exclude admin.logentry`

### "Database is locked" error (SQLite)
- Close any other programs accessing the database
- Make sure Django development server is stopped

### Large backup files
- Compress the backup: `gzip backup.json` → `backup.json.gz`
- Decompress before loading: `gunzip backup.json.gz`

## Quick Commands Reference

```bash
# Backup production
python backup_production_db.py

# Restore locally
python restore_local_db.py backups/production_backup_YYYYMMDD_HHMMSS.json

# Manual backup
python manage.py dumpdata --indent 2 --output backup.json

# Manual restore
python manage.py flush --noinput && python manage.py loaddata backup.json
```

