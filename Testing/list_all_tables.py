#!/usr/bin/env python
"""
List all database tables with their record counts and structure.
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.apps import apps
from django.db import connection
from django.db.models import Count

def list_all_tables():
    """List all database tables with counts and structure"""
    
    print("=" * 100)
    print("DATABASE TABLES OVERVIEW")
    print("=" * 100)
    print()
    
    # Get all models
    all_models = apps.get_models()
    
    # Group by app
    models_by_app = {}
    for model in all_models:
        app_label = model._meta.app_label
        if app_label not in models_by_app:
            models_by_app[app_label] = []
        models_by_app[app_label].append(model)
    
    total_tables = 0
    total_records = 0
    
    # Display tables by app
    for app_label in sorted(models_by_app.keys()):
        models = models_by_app[app_label]
        print(f"APP: {app_label.upper()}")
        print("=" * 100)
        
        for model in sorted(models, key=lambda m: m._meta.db_table):
            table_name = model._meta.db_table
            total_tables += 1
            
            try:
                count = model.objects.count()
                total_records += count
            except Exception as e:
                count = f"Error: {str(e)}"
            
            print(f"\nTable: {table_name}")
            print(f"  Model: {model.__name__}")
            print(f"  Records: {count}")
            
            # Show fields
            fields = model._meta.get_fields()
            field_info = []
            for field in fields:
                if hasattr(field, 'name'):
                    field_type = field.__class__.__name__
                    if hasattr(field, 'max_length') and field.max_length:
                        field_type += f"({field.max_length})"
                    field_info.append(f"    - {field.name}: {field_type}")
            
            if field_info:
                print("  Fields:")
                for info in field_info[:10]:  # Show first 10 fields
                    print(info)
                if len(field_info) > 10:
                    print(f"    ... and {len(field_info) - 10} more fields")
        
        print()
    
    # Summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total tables: {total_tables}")
    print(f"Total records: {total_records}")
    print()
    
    # Show raw SQL tables (in case there are tables not in Django models)
    print("Raw Database Tables (from SQL):")
    print("-" * 100)
    with connection.cursor() as cursor:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        elif 'mysql' in connection.settings_dict['ENGINE']:
            cursor.execute("SHOW TABLES")
        else:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        
        raw_tables = [row[0] for row in cursor.fetchall()]
        for table in raw_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error counting - {str(e)}")
    
    print("=" * 100)

if __name__ == "__main__":
    list_all_tables()

