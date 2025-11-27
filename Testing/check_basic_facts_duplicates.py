#!/usr/bin/env python
"""
Check for Basic Facts duplicates - levels with multiple topic associations
that could cause them to appear multiple times on the website.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic

# Get Basic Facts topics
basic_facts_topic = Topic.objects.filter(name="Basic facts").first()
addition_topic = Topic.objects.filter(name="Addition").first()
subtraction_topic = Topic.objects.filter(name="Subtraction").first()
multiplication_topic = Topic.objects.filter(name="Multiplication").first()
division_topic = Topic.objects.filter(name="Division").first()
place_value_facts_topic = Topic.objects.filter(name="Place Value Facts").first()

basic_facts_topics = [t for t in [addition_topic, subtraction_topic, multiplication_topic, division_topic, place_value_facts_topic] if t]

print("=" * 100)
print("CHECKING FOR BASIC FACTS DUPLICATES")
print("=" * 100)
print()

# Get all Basic Facts levels
levels = Level.objects.filter(topics=basic_facts_topic).order_by('level_number')

print(f"Total Basic Facts levels: {levels.count()}")
print()

# Check for levels with multiple Basic Facts topic associations
duplicates = []
for level in levels:
    level_topics = level.topics.all()
    basic_facts_subtopics = [t for t in level_topics if t in basic_facts_topics]
    
    if len(basic_facts_subtopics) > 1:
        duplicates.append({
            'level': level,
            'level_num': level.level_number,
            'topics': [t.name for t in basic_facts_subtopics]
        })

if duplicates:
    print("=" * 100)
    print("DUPLICATES FOUND (levels with multiple Basic Facts topic associations):")
    print("=" * 100)
    for dup in duplicates:
        print(f"  Level {dup['level_num']}: {dup['level'].title}")
        print(f"    Topics: {', '.join(dup['topics'])}")
        print()
else:
    print("[OK] No duplicates found - each level has only one Basic Facts subtopic")
    print()

# Show all levels and their topics
print("=" * 100)
print("ALL BASIC FACTS LEVELS:")
print("=" * 100)
for level in levels:
    level_topics = [t.name for t in level.topics.all() if t in basic_facts_topics]
    print(f"  Level {level.level_number}: {', '.join(level_topics) if level_topics else 'NO SUBTOPIC'}")

