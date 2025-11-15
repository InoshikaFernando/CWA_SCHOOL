#!/usr/bin/env python
"""
Generate comprehensive database documentation including all table relationships.
This should be run whenever models are changed to keep documentation up to date.

Usage: python Testing/generate_database_documentation.py
"""
import os
import sys
import django
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.apps import apps
from django.db import models

def get_field_type(field):
    """Get a human-readable field type"""
    if isinstance(field, models.ForeignKey):
        return f"ForeignKey -> {field.related_model.__name__}"
    elif isinstance(field, models.ManyToManyField):
        return f"ManyToMany -> {field.related_model.__name__}"
    elif isinstance(field, models.OneToOneField):
        return f"OneToOne -> {field.related_model.__name__}"
    else:
        return field.__class__.__name__

def get_field_constraints(field):
    """Get field constraints as a string"""
    constraints = []
    if field.null:
        constraints.append("null=True")
    if field.blank:
        constraints.append("blank=True")
    if hasattr(field, 'unique') and field.unique:
        constraints.append("unique=True")
    if hasattr(field, 'primary_key') and field.primary_key:
        constraints.append("primary_key=True")
    if hasattr(field, 'db_index') and field.db_index:
        constraints.append("db_index=True")
    if hasattr(field, 'default') and field.default is not models.NOT_PROVIDED:
        constraints.append(f"default={field.default}")
    return ", ".join(constraints) if constraints else "None"

def generate_documentation():
    """Generate comprehensive database documentation"""
    
    output = []
    output.append("# Database Schema Documentation")
    output.append("")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    output.append("> **Note:** This document is auto-generated. Run `python Testing/generate_database_documentation.py` to update it.")
    output.append("")
    output.append("---")
    output.append("")
    
    # Get all models
    all_models = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            all_models.append(model)
    
    # Sort by app name and model name
    all_models.sort(key=lambda m: (m._meta.app_label, m._meta.model_name))
    
    output.append("## Table of Contents")
    output.append("")
    for model in all_models:
        model_name = model.__name__
        table_name = model._meta.db_table
        output.append(f"- [{model_name}](#{model_name.lower()}) - `{table_name}`")
    output.append("")
    output.append("---")
    output.append("")
    
    # Generate documentation for each model
    for model in all_models:
        model_name = model.__name__
        table_name = model._meta.db_table
        app_label = model._meta.app_label
        
        output.append(f"## {model_name}")
        output.append("")
        output.append(f"**App:** `{app_label}`")
        output.append(f"**Database Table:** `{table_name}`")
        output.append("")
        
        # Model description/docstring
        if model.__doc__:
            output.append(f"**Description:** {model.__doc__.strip()}")
            output.append("")
        
        # Fields
        output.append("### Fields")
        output.append("")
        output.append("| Field Name | Type | Constraints | Description |")
        output.append("|------------|------|-------------|-------------|")
        
        for field in model._meta.get_fields():
            if field.auto_created:
                continue  # Skip auto-created reverse relations
            
            field_name = field.name
            field_type = get_field_type(field)
            constraints = get_field_constraints(field)
            
            # Get help text or verbose name
            if hasattr(field, 'help_text') and field.help_text:
                description = field.help_text
            elif hasattr(field, 'verbose_name'):
                description = field.verbose_name
            else:
                description = ""
            
            # Handle relationships
            if isinstance(field, models.ForeignKey):
                related_name = field.related_query_name() if hasattr(field, 'related_query_name') else field.name
                if hasattr(field, 'related_name') and field.related_name:
                    description += f" (related_name: `{field.related_name}`)"
                description += f" → {field.related_model.__name__}"
            elif isinstance(field, models.ManyToManyField):
                if hasattr(field, 'related_name') and field.related_name:
                    description += f" (related_name: `{field.related_name}`)"
                description += f" → {field.related_model.__name__}"
            elif isinstance(field, models.OneToOneField):
                if hasattr(field, 'related_name') and field.related_name:
                    description += f" (related_name: `{field.related_name}`)"
                description += f" → {field.related_model.__name__}"
            
            output.append(f"| `{field_name}` | {field_type} | {constraints} | {description} |")
        
        output.append("")
        
        # Reverse relationships (related objects)
        reverse_relations = []
        for related_obj in model._meta.related_objects:
            if related_obj.related_model == model:
                continue
            reverse_relations.append(related_obj)
        
        if reverse_relations:
            output.append("### Reverse Relationships")
            output.append("")
            output.append("These relationships point TO this model:")
            output.append("")
            output.append("| From Model | Field Name | Type | Related Name |")
            output.append("|------------|------------|------|--------------|")
            
            for rel in reverse_relations:
                from_model = rel.related_model.__name__
                field_name = rel.field.name
                rel_type = get_field_type(rel.field)
                related_name = rel.get_accessor_name()
                
                output.append(f"| `{from_model}` | `{field_name}` | {rel_type} | `{related_name}` |")
            
            output.append("")
        
        # Many-to-many relationships
        m2m_fields = [f for f in model._meta.get_fields() if isinstance(f, models.ManyToManyField)]
        if m2m_fields:
            output.append("### Many-to-Many Relationships")
            output.append("")
            output.append("| Field Name | Related Model | Through Table | Related Name |")
            output.append("|------------|---------------|---------------|--------------|")
            
            for field in m2m_fields:
                field_name = field.name
                related_model = field.related_model.__name__
                through_table = field.remote_field.through._meta.db_table if field.remote_field.through else "auto-created"
                related_name = field.related_query_name() if hasattr(field, 'related_query_name') else field.name
                
                output.append(f"| `{field_name}` | `{related_model}` | `{through_table}` | `{related_name}` |")
            
            output.append("")
        
        # Meta options
        if model._meta.ordering:
            output.append(f"**Default Ordering:** {', '.join(model._meta.ordering)}")
            output.append("")
        
        if model._meta.unique_together:
            output.append(f"**Unique Together:** {model._meta.unique_together}")
            output.append("")
        
        if model._meta.indexes:
            output.append("**Indexes:**")
            for index in model._meta.indexes:
                output.append(f"- {index.fields}")
            output.append("")
        
        output.append("---")
        output.append("")
    
    # Relationship diagram
    output.append("## Relationship Diagram")
    output.append("")
    output.append("### Foreign Key Relationships")
    output.append("")
    output.append("```")
    
    for model in all_models:
        model_name = model.__name__
        fk_fields = [f for f in model._meta.get_fields() 
                    if isinstance(f, (models.ForeignKey, models.OneToOneField))]
        
        if fk_fields:
            for field in fk_fields:
                related_model = field.related_model.__name__
                output.append(f"{model_name} --|> {related_model} : {field.name}")
    
    output.append("```")
    output.append("")
    
    # Many-to-Many relationships
    output.append("### Many-to-Many Relationships")
    output.append("")
    output.append("```")
    
    for model in all_models:
        m2m_fields = [f for f in model._meta.get_fields() if isinstance(f, models.ManyToManyField)]
        if m2m_fields:
            for field in m2m_fields:
                related_model = field.related_model.__name__
                output.append(f"{model_name} }}o--o{{ {related_model} : {field.name}")
    
    output.append("```")
    output.append("")
    
    # Write to file
    doc_content = "\n".join(output)
    # Create documentation directory if it doesn't exist
    doc_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documentation")
    os.makedirs(doc_dir, exist_ok=True)
    doc_file = os.path.join(doc_dir, "DATABASE_SCHEMA.md")
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("=" * 80)
    print("DATABASE DOCUMENTATION GENERATED")
    print("=" * 80)
    print(f"Output file: {doc_file}")
    print(f"Models documented: {len(all_models)}")
    print()
    print("Documentation includes:")
    print("  - All models and their database table names")
    print("  - All fields with types and constraints")
    print("  - Foreign key relationships")
    print("  - Many-to-many relationships")
    print("  - Reverse relationships")
    print("  - Relationship diagrams")
    print()
    print("To update this documentation, run:")
    print("  python Testing/generate_database_documentation.py")
    print("=" * 80)

if __name__ == "__main__":
    generate_documentation()

