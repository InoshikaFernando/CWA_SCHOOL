#!/usr/bin/env python
"""
Script to restore a production database backup to local SQLite database
Usage: python restore_local_db.py <backup_file.json>
"""
import os
import sys
import django
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def restore_local_database(backup_file):
    """
    Restore a backup file to the local database
    """
    if not os.path.exists(backup_file):
        print(f"❌ ERROR: Backup file not found: {backup_file}")
        return False
    
    print("=" * 80)
    print("RESTORING DATABASE TO LOCAL")
    print("=" * 80)
    print(f"\nBackup file: {backup_file}")
    print(f"Local database: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database file: {settings.DATABASES['default'].get('NAME', 'N/A')}")
    
    # Confirm before proceeding
    print("\n⚠️  WARNING: This will replace all data in your local database!")
    confirm = input("Type 'YES' to continue: ")
    if confirm != 'YES':
        print("❌ Restore cancelled.")
        return False
    
    print("\n[INFO] Flushing existing data...")
    try:
        # Flush the database (clear all data)
        call_command('flush', '--noinput', verbosity=1)
        print("✅ Database flushed")
    except Exception as e:
        print(f"⚠️  Warning: Could not flush database: {e}")
        print("   Continuing anyway...")
    
    print("\n[INFO] Loading backup data...")
    print("       This may take a few minutes...\n")
    
    try:
        # Load the backup file
        call_command('loaddata', backup_file, verbosity=1)
        
        print("\n" + "=" * 80)
        print("RESTORE COMPLETE")
        print("=" * 80)
        print("✅ Database restored successfully!")
        print(f"\n💡 You can now run: python manage.py runserver")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Restore failed!")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Restore production database backup to local')
    parser.add_argument('backup_file', help='Path to the backup JSON file')
    args = parser.parse_args()
    
    success = restore_local_database(args.backup_file)
    sys.exit(0 if success else 1)

