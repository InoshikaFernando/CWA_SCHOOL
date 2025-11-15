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
# Level 100-109: Addition
# Level 110-119: Subtraction
# Level 120-129: Multiplication
# Level 130-139: Division
# Level 140-149: Place Value Facts

# Addition levels
addition_topic, _ = Topic.objects.get_or_create(name="Addition")
for i in range(10):
    level_num = 100 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Addition Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    level.topics.add(basic_facts_topic)
    level.topics.add(addition_topic)

# Subtraction levels
subtraction_topic, _ = Topic.objects.get_or_create(name="Subtraction")
for i in range(10):
    level_num = 110 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Subtraction Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    level.topics.add(basic_facts_topic)
    level.topics.add(subtraction_topic)

# Multiplication levels
multiplication_topic, _ = Topic.objects.get_or_create(name="Multiplication")
for i in range(10):
    level_num = 120 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Multiplication Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    level.topics.add(basic_facts_topic)
    level.topics.add(multiplication_topic)

# Division levels
division_topic, _ = Topic.objects.get_or_create(name="Division")
for i in range(10):
    level_num = 130 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Division Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    level.topics.add(basic_facts_topic)
    level.topics.add(division_topic)

# Place Value Facts levels
place_value_facts_topic, _ = Topic.objects.get_or_create(name="Place Value Facts")
for i in range(10):
    level_num = 140 + i
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Basic Facts - Place Value Facts Level {i+1}"}
    )
    if created:
        print(f"Created level: {level.title} (Level {level_num})")
    level.topics.add(basic_facts_topic)
    level.topics.add(place_value_facts_topic)

print("\n[OK] Basic Facts topic structure created successfully!")
print(f"   - Basic Facts topic: {basic_facts_topic.name}")
print(f"   - Addition levels: 100-109")
print(f"   - Subtraction levels: 110-119")
print(f"   - Multiplication levels: 120-129")
print(f"   - Division levels: 130-139")
print(f"   - Place Value Facts levels: 140-149")

