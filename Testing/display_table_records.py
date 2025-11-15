#!/usr/bin/env python
"""
Display all records from a database table.
Usage: python Testing/display_table_records.py --table_name <table_name>
       python Testing/display_table_records.py --table_name maths_question
       python Testing/display_table_records.py --table_name maths_customuser --limit 10
"""
import os
import sys
import django
import argparse

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.apps import apps
from django.db import connection
from django.core.paginator import Paginator

def get_model_from_table_name(table_name):
    """Find the Django model that corresponds to a database table name"""
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            if model._meta.db_table == table_name:
                return model
    return None

def get_all_table_names():
    """Get all table names from the database"""
    with connection.cursor() as cursor:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        elif 'mysql' in connection.settings_dict['ENGINE']:
            cursor.execute("SHOW TABLES")
        elif 'postgresql' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        else:
            return []
        
        return [row[0] for row in cursor.fetchall()]

def display_table_records(table_name, limit=None, offset=0, format='table'):
    """Display all records from a table"""
    
    print("=" * 100)
    print(f"DISPLAYING RECORDS FROM TABLE: {table_name}")
    print("=" * 100)
    print()
    
    # Try to find the Django model
    model = get_model_from_table_name(table_name)
    
    if model:
        # Use Django ORM
        print(f"[INFO] Found Django model: {model.__name__}")
        print(f"[INFO] App: {model._meta.app_label}")
        print()
        
        # Get all records
        queryset = model.objects.all()
        total_count = queryset.count()
        
        print(f"[INFO] Total records: {total_count}")
        print()
        
        if total_count == 0:
            print("No records found in this table.")
            return
        
        # Apply limit and offset
        if limit:
            queryset = queryset[offset:offset+limit]
            print(f"[INFO] Showing records {offset+1} to {min(offset+limit, total_count)} of {total_count}")
        else:
            queryset = queryset[offset:]
            if offset > 0:
                print(f"[INFO] Showing records {offset+1} to {total_count} of {total_count}")
        
        print()
        
        # Get field names
        field_names = [f.name for f in model._meta.get_fields() if not f.auto_created]
        
        # Display records
        if format == 'table':
            display_as_table(queryset, field_names, model)
        elif format == 'json':
            display_as_json(queryset, field_names, model)
        else:
            display_as_list(queryset, field_names, model)
        
        if limit and offset + limit < total_count:
            print()
            print(f"[INFO] Showing {limit} of {total_count} records. Use --offset {offset+limit} to see more.")
    
    else:
        # Use raw SQL
        print(f"[INFO] No Django model found. Using raw SQL query.")
        print()
        
        with connection.cursor() as cursor:
            # Get column names
            if 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
            elif 'mysql' in connection.settings_dict['ENGINE']:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [row[0] for row in cursor.fetchall()]
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, [table_name])
                columns = [row[0] for row in cursor.fetchall()]
            else:
                print("[ERROR] Unsupported database engine")
                return
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            
            print(f"[INFO] Total records: {total_count}")
            print()
            
            if total_count == 0:
                print("No records found in this table.")
                return
            
            # Build query with limit
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
                print(f"[INFO] Showing records {offset+1} to {min(offset+limit, total_count)} of {total_count}")
            elif offset > 0:
                query += f" OFFSET {offset}"
                print(f"[INFO] Showing records {offset+1} to {total_count} of {total_count}")
            
            print()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Display as table
            display_raw_table(rows, columns)
            
            if limit and offset + limit < total_count:
                print()
                print(f"[INFO] Showing {limit} of {total_count} records. Use --offset {offset+limit} to see more.")

def display_as_table(queryset, field_names, model):
    """Display records in a table format"""
    records = list(queryset)
    
    if not records:
        print("No records to display.")
        return
    
    # Calculate column widths
    col_widths = {}
    for field_name in field_names:
        col_widths[field_name] = len(field_name)
        for record in records:
            try:
                value = getattr(record, field_name, None)
                if value is None:
                    value_str = "None"
                elif hasattr(value, '__str__'):
                    value_str = str(value)
                else:
                    value_str = repr(value)
                col_widths[field_name] = max(col_widths[field_name], len(value_str))
            except:
                pass
        # Limit column width
        col_widths[field_name] = min(col_widths[field_name], 50)
    
    # Print header
    header = " | ".join(f"{name:<{col_widths[name]}}" for name in field_names)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for record in records:
        row_values = []
        for field_name in field_names:
            try:
                value = getattr(record, field_name, None)
                if value is None:
                    value_str = "None"
                elif hasattr(value, '__str__'):
                    value_str = str(value)
                else:
                    value_str = repr(value)
                # Truncate long values
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                row_values.append(f"{value_str:<{col_widths[field_name]}}")
            except Exception as e:
                row_values.append(f"<Error: {str(e)[:30]}>")
        
        print(" | ".join(row_values))

def display_as_list(queryset, field_names, model):
    """Display records as a list"""
    records = list(queryset)
    
    for idx, record in enumerate(records, 1):
        print(f"\n--- Record {idx} ---")
        for field_name in field_names:
            try:
                value = getattr(record, field_name, None)
                print(f"  {field_name}: {value}")
            except Exception as e:
                print(f"  {field_name}: <Error: {str(e)}>")

def display_as_json(queryset, field_names, model):
    """Display records as JSON-like format"""
    import json
    records = []
    for record in queryset:
        record_dict = {}
        for field_name in field_names:
            try:
                value = getattr(record, field_name, None)
                # Convert datetime and other non-serializable types
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                record_dict[field_name] = value
            except:
                record_dict[field_name] = None
        records.append(record_dict)
    
    print(json.dumps(records, indent=2, default=str))

def display_raw_table(rows, columns):
    """Display raw SQL results as a table"""
    if not rows:
        print("No records to display.")
        return
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = len(col)
        for row in rows:
            col_idx = columns.index(col)
            value_str = str(row[col_idx]) if row[col_idx] is not None else "None"
            col_widths[col] = max(col_widths[col], len(value_str))
        col_widths[col] = min(col_widths[col], 50)
    
    # Print header
    header = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        row_values = []
        for col in columns:
            col_idx = columns.index(col)
            value_str = str(row[col_idx]) if row[col_idx] is not None else "None"
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            row_values.append(f"{value_str:<{col_widths[col]}}")
        print(" | ".join(row_values))

def list_all_tables():
    """List all available tables"""
    print("=" * 100)
    print("AVAILABLE TABLES")
    print("=" * 100)
    print()
    
    tables = get_all_table_names()
    
    # Try to match with Django models
    models_by_table = {}
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            models_by_table[model._meta.db_table] = model
    
    print(f"{'Table Name':<40} {'Django Model':<30} {'App':<20}")
    print("-" * 100)
    
    for table in sorted(tables):
        if table in models_by_table:
            model = models_by_table[table]
            print(f"{table:<40} {model.__name__:<30} {model._meta.app_label:<20}")
        else:
            print(f"{table:<40} {'<No Model>':<30} {'<N/A>':<20}")
    
    print()
    print(f"Total tables: {len(tables)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Display all records from a database table',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available tables
  python Testing/display_table_records.py --list
  
  # Display all records from a table
  python Testing/display_table_records.py --table_name maths_question
  
  # Display with limit
  python Testing/display_table_records.py --table_name maths_customuser --limit 10
  
  # Display with offset (pagination)
  python Testing/display_table_records.py --table_name maths_question --limit 20 --offset 20
  
  # Display in JSON format
  python Testing/display_table_records.py --table_name maths_question --format json
  
  # Display as list
  python Testing/display_table_records.py --table_name maths_question --format list
        """
    )
    parser.add_argument('--table_name', type=str,
                       help='Name of the database table to display')
    parser.add_argument('--limit', type=int,
                       help='Maximum number of records to display')
    parser.add_argument('--offset', type=int, default=0,
                       help='Number of records to skip (for pagination)')
    parser.add_argument('--format', type=str, choices=['table', 'list', 'json'], default='table',
                       help='Output format: table (default), list, or json')
    parser.add_argument('--list', action='store_true',
                       help='List all available tables')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_tables()
    elif args.table_name:
        display_table_records(args.table_name, args.limit, args.offset, args.format)
    else:
        parser.print_help()
        print("\n[ERROR] Please provide --table_name or use --list to see available tables")

