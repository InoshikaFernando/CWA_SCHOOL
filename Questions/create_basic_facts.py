#!/usr/bin/env python
"""
Script to create Basic Facts topic structure with Addition levels.
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Topic, Level

# Create Basic Facts topic
basic_facts_topic, created = Topic.objects.get_or_create(name="Basic facts")
print(f"{'Created' if created else 'Found'} topic: Basic facts")

# Create levels for Basic Facts (level_number >= 100)
# CORRECT RANGES (matching generate_basic_facts_questions.py and practice_extras.py):
# Level 100-106: Addition (7 levels)
# Level 107-113: Subtraction (7 levels)
# Level 114-120: Multiplication (7 levels)
# Level 121-127: Division (7 levels)
# Level 128-132: Place Value Facts (5 levels)

# Addition levels (100-106)
addition_topic, _ = Topic.objects.get_or_create(name="Addition")
for i in range(7):
    level_num = 100 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Addition Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    # Only add topics if not already associated
    if not level.topics.filter(id=basic_facts_topic.id).exists():
        level.topics.add(basic_facts_topic)
    if not level.topics.filter(id=addition_topic.id).exists():
        level.topics.add(addition_topic)

# Subtraction levels (107-113)
subtraction_topic, _ = Topic.objects.get_or_create(name="Subtraction")
for i in range(7):
    level_num = 107 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Subtraction Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    # Only add topics if not already associated
    if not level.topics.filter(id=basic_facts_topic.id).exists():
        level.topics.add(basic_facts_topic)
    if not level.topics.filter(id=subtraction_topic.id).exists():
        level.topics.add(subtraction_topic)

# Multiplication levels (114-120)
multiplication_topic, _ = Topic.objects.get_or_create(name="Multiplication")
for i in range(7):
    level_num = 114 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Multiplication Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    # Only add topics if not already associated
    if not level.topics.filter(id=basic_facts_topic.id).exists():
        level.topics.add(basic_facts_topic)
    if not level.topics.filter(id=multiplication_topic.id).exists():
        level.topics.add(multiplication_topic)

# Division levels (121-127)
division_topic, _ = Topic.objects.get_or_create(name="Division")
for i in range(7):
    level_num = 121 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Division Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    # Only add topics if not already associated
    if not level.topics.filter(id=basic_facts_topic.id).exists():
        level.topics.add(basic_facts_topic)
    if not level.topics.filter(id=division_topic.id).exists():
        level.topics.add(division_topic)

# Place Value Facts levels (128-132)
place_value_facts_topic, _ = Topic.objects.get_or_create(name="Place Value Facts")
for i in range(5):
    level_num = 128 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Place Value Facts Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    # Only add topics if not already associated
    if not level.topics.filter(id=basic_facts_topic.id).exists():
        level.topics.add(basic_facts_topic)
    if not level.topics.filter(id=place_value_facts_topic.id).exists():
        level.topics.add(place_value_facts_topic)

print("\n[OK] Basic Facts topic structure created successfully!")
print(f"   - Basic Facts topic: {basic_facts_topic.name}")
print(f"   - Addition levels: 100-106 (7 levels)")
print(f"   - Subtraction levels: 107-113 (7 levels)")
print(f"   - Multiplication levels: 114-120 (7 levels)")
print(f"   - Division levels: 121-127 (7 levels)")
print(f"   - Place Value Facts levels: 128-132 (5 levels)")

