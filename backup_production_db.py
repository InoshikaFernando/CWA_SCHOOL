#!/usr/bin/env python
"""
Script to backup production database using Django's dumpdata command
This creates a JSON fixture file that can be loaded into any database (MySQL, SQLite, etc.)
"""
import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def backup_production_database():
    """
    Backup the production database to a JSON file
    This should be run on the production server
    """
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'production_backup_{timestamp}.json')
    
    print("=" * 80)
    print("BACKING UP PRODUCTION DATABASE")
    print("=" * 80)
    print(f"\nBackup file: {backup_file}")
    print(f"Database: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database name: {settings.DATABASES['default'].get('NAME', 'N/A')}")
    print("\n[INFO] Starting backup...")
    print("       This may take a few minutes depending on database size...\n")
    
    try:
        # Dump all data to JSON file
        # Exclude contenttypes and sessions to avoid conflicts
        call_command(
            'dumpdata',
            '--indent', '2',
            '--exclude', 'contenttypes',
            '--exclude', 'sessions',
            '--exclude', 'admin.logentry',
            '--output', backup_file,
            verbosity=1
        )
        
        # Get file size
        file_size = os.path.getsize(backup_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print("\n" + "=" * 80)
        print("BACKUP COMPLETE")
        print("=" * 80)
        print(f"✅ Backup file created: {backup_file}")
        print(f"📦 File size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        print(f"\n💡 To download this file from production:")
        print(f"   1. Use SFTP/SCP to download: {backup_file}")
        print(f"   2. Or use PythonAnywhere file browser to download")
        print(f"\n💡 To restore locally:")
        print(f"   python restore_local_db.py {backup_file}")
        print("=" * 80)
        
        return backup_file
        
    except Exception as e:
        print(f"\n❌ ERROR: Backup failed!")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    backup_file = backup_production_database()
    if backup_file:
        sys.exit(0)
    else:
        sys.exit(1)

