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

# Create subtopics
subtopics = ["Addition", "Subtraction", "Multiplication", "Division", "Place Value Facts"]
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

# Create Place Value Facts levels (starting from level_number 128)
place_value_levels = [
    (128, "Combinations for 10 (e.g., 7 + 3 = ?, 4 + ? = 10)"),
    (129, "Combinations for 100 (e.g., 63 + 37 = 100, 40 + ? = 100)"),
    (130, "Combinations for 1000"),
    (131, "Combinations for 10,000"),
    (132, "Combinations for 100,000"),
]

place_value_topic = topic_objs["Place Value Facts"]
for level_num, description in place_value_levels:
    display_level = level_num - 127  # 128 -> 1, 129 -> 2, etc.
    level, created = Level.objects.get_or_create(
        level_number=level_num,
        defaults={'title': f"Place Value Facts Level {display_level}: {description}"}
    )
    # Update title if level already existed but title might be different
    if not created:
        level.title = f"Place Value Facts Level {display_level}: {description}"
        level.save()
    
    # Associate level with Place Value Facts topic (ensure it's added even if level existed)
    if place_value_topic not in level.topics.all():
        level.topics.add(place_value_topic)
        print(f"Associated level {level_num} with Place Value Facts")
    else:
        print(f"Level {level_num} already associated with Place Value Facts")
    
    print(f"{'Created' if created else 'Updated'} level {level_num}: {level.title}")

print("\n✅ Basic Facts structure created successfully!")
print(f"   - Topic: Basic facts")
print(f"   - Subtopics: {', '.join(subtopics)}")
print(f"   - Addition levels: {len(addition_levels)} (Level numbers 100-106)")
print(f"   - Subtraction levels: {len(subtraction_levels)} (Level numbers 107-113)")
print(f"   - Multiplication levels: {len(multiplication_levels)} (Level numbers 114-120)")
print(f"   - Division levels: {len(division_levels)} (Level numbers 121-127)")
print(f"   - Place Value Facts levels: {len(place_value_levels)} (Level numbers 128-132)")

# Final verification
print("\n📊 Verification:")
place_value_topic_check = Topic.objects.filter(name="Place Value Facts").first()
if place_value_topic_check:
    pv_levels = Level.objects.filter(topics=place_value_topic_check, level_number__gte=128, level_number__lte=132)
    print(f"   ✓ Place Value Facts topic exists")
    print(f"   ✓ Place Value Facts levels found: {pv_levels.count()} (expected 5)")
    if pv_levels.count() == 5:
        print(f"   ✓ All Place Value Facts levels are properly associated!")
    else:
        print(f"   ⚠️  Warning: Expected 5 levels but found {pv_levels.count()}")
        print(f"   Missing levels: {set(range(128, 133)) - set(pv_levels.values_list('level_number', flat=True))}")
else:
    print(f"   ⚠️  ERROR: Place Value Facts topic not found!")

