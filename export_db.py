#!/usr/bin/env python
"""
Script to export database with proper UTF-8 encoding
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.core import serializers
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
import json

# Get all models
all_models = []
for app_config in apps.get_app_configs():
    all_models.extend(app_config.get_models())

# Serialize all data to JSON string first
json_string = ""
for model in all_models:
    try:
        objects = model.objects.all()
        if objects.exists():
            json_string += serializers.serialize('json', objects, ensure_ascii=False)
            json_string += "\n"
    except Exception as e:
        print(f"Warning: Could not serialize {model._meta.label}: {e}")

# Parse and reformat with proper indentation
if json_string.strip():
    # Parse each line (each model's serialization)
    all_data = []
    for line in json_string.strip().split('\n'):
        if line.strip():
            try:
                parsed = json.loads(line)
                if isinstance(parsed, list):
                    all_data.extend(parsed)
                else:
                    all_data.append(parsed)
            except:
                pass
    
    # Write to file with UTF-8 encoding
    output_file = 'db_export_utf8.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder)
    
    print(f"✅ Database exported successfully to {output_file}")
    print(f"   Total objects exported: {len(all_data)}")
else:
    print("⚠️  No data to export")

