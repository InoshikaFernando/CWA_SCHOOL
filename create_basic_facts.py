#!/usr/bin/env python
"""
Script to create Basic Facts topic structure with Addition levels.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Topic, Level

# Create Basic Facts topic
basic_facts_topic, created = Topic.objects.get_or_create(name="Basic facts")
print(f"{'Created' if created else 'Found'} topic: Basic facts")

# Create subtopics
subtopics = ["Addition", "Subtraction", "Multiplication", "Division"]
topic_objs = {}
for subtopic_name in subtopics:
    topic, created = Topic.objects.get_or_create(name=subtopic_name)
    topic_objs[subtopic_name] = topic
    print(f"{'Created' if created else 'Found'} subtopic: {subtopic_name}")

# Create Addition levels (starting from level_number 100 to avoid conflicts)
addition_levels = [
    (100, "Adding two single digits where values are less than 6"),
    (101, "Adding any 2 single digits"),
    (102, "Adding double digits where you don't have to carry over to the next place (like 14 + 35)"),
    (103, "Adding double digits where you have to carry for the next place (like 17 + 25)"),
    (104, "Adding two 3 digit numbers"),
    (105, "Adding two 4 digits"),
    (106, "Adding two 5 digits"),
]

addition_topic = topic_objs["Addition"]
for level_num, description in addition_levels:
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Addition Level {level_num - 99}: {description}"}
    )
    # Associate level with Addition topic
    level.topics.add(addition_topic)
    print(f"{'Created' if created else 'Found'} level {level_num}: {level.title}")

# Create Subtraction levels (starting from level_number 107)
subtraction_levels = [
    (107, "Subtracting from single digit (big number) a single digit (small number)"),
    (108, "Subtraction a single digit from a double digit (no carry over)"),
    (109, "Subtraction a single digit from a double digit (include carryover)"),
    (110, "Subtract double digit from a double digit (No negative answers)"),
    (111, "Subtraction double digit from a double digit (can result negative values)"),
    (112, "Subtract 3 digit"),
    (113, "Subtract 4 digit"),
]

subtraction_topic = topic_objs["Subtraction"]
for level_num, description in subtraction_levels:
    display_level = level_num - 106  # 107 -> 1, 108 -> 2, etc.
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Subtraction Level {display_level}: {description}"}
    )
    # Associate level with Subtraction topic
    level.topics.add(subtraction_topic)
    print(f"{'Created' if created else 'Found'} level {level_num}: {level.title}")

# Create Multiplication levels (starting from level_number 114)
multiplication_levels = [
    (114, "Single or doubel digit multiply by 1, 10"),
    (115, "Single or doubel digit multiply by 1, 10, 100"),
    (116, "Single or doubel digit multiply by 5, 10"),
    (117, "Single or doubel digit multiply by 2, 3, 5, 10"),
    (118, "doubel or triple digit multiply by 2, 3, 4, 5, 10"),
    (119, "doubel or triple digit multiply by 2, 3, 4, 5, 6, 7, 10"),
    (120, "triple digit multiply by 2, 3, 4, 5, 6, 7, 8, 9, 10"),
]

multiplication_topic = topic_objs["Multiplication"]
for level_num, description in multiplication_levels:
    display_level = level_num - 113  # 114 -> 1, 115 -> 2, etc.
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Multiplication Level {display_level}: {description}"}
    )
    # Associate level with Multiplication topic
    level.topics.add(multiplication_topic)
    print(f"{'Created' if created else 'Found'} level {level_num}: {level.title}")

# Create Division levels (starting from level_number 121)
# All the numbers should be able to divide by the divider
division_levels = [
    (121, "doubel digit (should be able to divide by 10) divide by 1, 10"),
    (122, "triple digit multiply (should be able to divide by 100) divide by 1, 10, 100"),
    (123, "triple or doubel digit divide by 5, 10"),
    (124, "triple or doubel digit divide by 2, 3, 5, 10"),
    (125, "doubel or triple digit divide by 2, 3, 4, 5, 10"),
    (126, "triple digit divide by 2, 3, 4, 5, 6, 7, 10"),
    (127, "triple digit divide by 2, 3, 4, 5, 6, 7, 8, 9, 10, 11"),
]

division_topic = topic_objs["Division"]
for level_num, description in division_levels:
    display_level = level_num - 120  # 121 -> 1, 122 -> 2, etc.
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Division Level {display_level}: {description}"}
    )
    # Associate level with Division topic
    level.topics.add(division_topic)
    print(f"{'Created' if created else 'Found'} level {level_num}: {level.title}")

print("\n✅ Basic Facts structure created successfully!")
print(f"   - Topic: Basic facts")
print(f"   - Subtopics: {', '.join(subtopics)}")
print(f"   - Addition levels: {len(addition_levels)} (Level numbers 100-106)")
print(f"   - Subtraction levels: {len(subtraction_levels)} (Level numbers 107-113)")
print(f"   - Multiplication levels: {len(multiplication_levels)} (Level numbers 114-120)")
print(f"   - Division levels: {len(division_levels)} (Level numbers 121-127)")

