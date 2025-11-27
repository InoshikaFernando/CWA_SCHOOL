#!/usr/bin/env python
"""
Script to remove Basic Facts duplicates:
1. Remove extra levels that shouldn't exist (107-109 as Addition, 129, 130-139, 140-149)
2. Remove incorrect topic associations
3. Ensure only correct levels (100-132) are linked to Basic Facts topics

CORRECT RANGES:
- 100-106: Addition (7 levels)
- 107-113: Subtraction (7 levels)
- 114-120: Multiplication (7 levels)
- 121-127: Division (7 levels)
- 128-132: Place Value Facts (5 levels)
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question
import argparse

def remove_basic_facts_duplicates(dry_run=True, remove_extra_levels=False):
    """
    Remove Basic Facts duplicates:
    - Remove incorrect topic associations
    - Optionally remove extra levels that shouldn't exist
    
    Args:
        dry_run: If True, only show what would be done without making changes
        remove_extra_levels: If True, delete levels 129, 130-139, 140-149 (dangerous!)
    """
    print("=" * 100)
    print("REMOVING BASIC FACTS DUPLICATES")
    print("=" * 100)
    print()
    
    # Get Basic Facts topics
    basic_facts_topic = Topic.objects.filter(name="Basic facts").first()
    addition_topic = Topic.objects.filter(name="Addition").first()
    subtraction_topic = Topic.objects.filter(name="Subtraction").first()
    multiplication_topic = Topic.objects.filter(name="Multiplication").first()
    division_topic = Topic.objects.filter(name="Division").first()
    place_value_facts_topic = Topic.objects.filter(name="Place Value Facts").first()
    
    if not basic_facts_topic:
        print("[ERROR] Basic facts topic not found!")
        return
    
    print("[INFO] Correct Basic Facts level ranges:")
    print("  - Addition: 100-106 (7 levels)")
    print("  - Subtraction: 107-113 (7 levels)")
    print("  - Multiplication: 114-120 (7 levels)")
    print("  - Division: 121-127 (7 levels)")
    print("  - Place Value Facts: 128-132 (5 levels)")
    print()
    
    # Define correct associations
    correct_associations = {
        # Addition: 100-106
        **{i: [basic_facts_topic, addition_topic] for i in range(100, 107)},
        # Subtraction: 107-113
        **{i: [basic_facts_topic, subtraction_topic] for i in range(107, 114)},
        # Multiplication: 114-120
        **{i: [basic_facts_topic, multiplication_topic] for i in range(114, 121)},
        # Division: 121-127
        **{i: [basic_facts_topic, division_topic] for i in range(121, 128)},
        # Place Value Facts: 128-132
        **{i: [basic_facts_topic, place_value_facts_topic] for i in range(128, 133)},
    }
    
    # Get all Basic Facts levels (100-149)
    all_basic_facts_levels = Level.objects.filter(
        level_number__gte=100,
        level_number__lte=149
    ).order_by('level_number')
    
    print(f"[INFO] Found {all_basic_facts_levels.count()} Basic Facts levels (100-149)")
    print()
    
    issues_found = []
    extra_levels = []
    incorrect_associations = []
    
    # Check each level
    for level in all_basic_facts_levels:
        level_num = level.level_number
        current_topics = list(level.topics.all())
        current_topic_names = [t.name for t in current_topics]
        
        # Check if level is in correct range (100-132)
        if level_num not in correct_associations:
            # This is an extra level that shouldn't exist
            extra_levels.append({
                'level': level,
                'level_num': level_num,
                'topics': current_topic_names,
                'has_questions': Question.objects.filter(level=level).exists(),
                'question_count': Question.objects.filter(level=level).count()
            })
            continue
        
        # Check if level has correct topic associations
        expected_topics = correct_associations[level_num]
        expected_topic_names = [t.name for t in expected_topics if t]
        
        # Find incorrect associations
        incorrect_topics = [t for t in current_topics if t not in expected_topics]
        missing_topics = [t for t in expected_topics if t and t not in current_topics]
        
        if incorrect_topics or missing_topics:
            incorrect_associations.append({
                'level': level,
                'level_num': level_num,
                'current_topics': current_topic_names,
                'expected_topics': expected_topic_names,
                'incorrect_topics': [t.name for t in incorrect_topics],
                'missing_topics': [t.name for t in missing_topics if t]
            })
    
    # Report issues
    if extra_levels:
        print("=" * 100)
        print("EXTRA LEVELS (should not exist):")
        print("=" * 100)
        for item in extra_levels:
            print(f"  Level {item['level_num']}: {item['level'].title}")
            print(f"    Current topics: {', '.join(item['topics'])}")
            print(f"    Questions: {item['question_count']}")
            if item['has_questions']:
                print(f"    [WARNING] This level has questions! Be careful when removing.")
            print()
    else:
        print("[OK] No extra levels found (all levels are in correct range 100-132)")
        print()
    
    if incorrect_associations:
        print("=" * 100)
        print("INCORRECT TOPIC ASSOCIATIONS:")
        print("=" * 100)
        for item in incorrect_associations:
            print(f"  Level {item['level_num']}: {item['level'].title}")
            print(f"    Current topics: {', '.join(item['current_topics'])}")
            print(f"    Expected topics: {', '.join(item['expected_topics'])}")
            if item['incorrect_topics']:
                print(f"    [REMOVE] Incorrect topics: {', '.join(item['incorrect_topics'])}")
            if item['missing_topics']:
                print(f"    [ADD] Missing topics: {', '.join(item['missing_topics'])}")
            print()
    else:
        print("[OK] No incorrect topic associations found")
        print()
    
    if not extra_levels and not incorrect_associations:
        print("[OK] No duplicates found! Basic Facts structure is correct.")
        return
    
    if dry_run:
        print("=" * 100)
        print("[DRY RUN] This was a dry run. No changes were made.")
        print("         Run with --execute to actually perform the cleanup.")
        if extra_levels:
            print("         Use --remove-extra-levels to delete extra levels (DANGEROUS!).")
        return
    
    # Perform cleanup
    print("=" * 100)
    print("PERFORMING CLEANUP...")
    print("=" * 100)
    print()
    
    fixed_associations = 0
    removed_associations = 0
    added_associations = 0
    deleted_levels = 0
    
    # Fix incorrect topic associations
    for item in incorrect_associations:
        level = item['level']
        expected_topics = correct_associations[item['level_num']]
        current_topics = list(level.topics.all())
        
        # Remove incorrect topics
        for topic in current_topics:
            if topic not in expected_topics:
                level.topics.remove(topic)
                removed_associations += 1
                print(f"[FIXED] Removed '{topic.name}' from Level {item['level_num']}")
        
        # Add missing topics
        for topic in expected_topics:
            if topic and topic not in current_topics:
                level.topics.add(topic)
                added_associations += 1
                print(f"[FIXED] Added '{topic.name}' to Level {item['level_num']}")
        
        fixed_associations += 1
    
    # Handle extra levels
    if extra_levels:
        if remove_extra_levels:
            print()
            print("[WARNING] Removing extra levels...")
            for item in extra_levels:
                level = item['level']
                level_num = item['level_num']
                
                if item['has_questions']:
                    print(f"[SKIP] Level {level_num} has {item['question_count']} questions. Not deleting.")
                    # Just remove topic associations
                    for topic in level.topics.all():
                        level.topics.remove(topic)
                    print(f"[FIXED] Removed all topic associations from Level {level_num}")
                else:
                    # Safe to delete
                    level.delete()
                    deleted_levels += 1
                    print(f"[DELETED] Level {level_num} (no questions)")
        else:
            print()
            print("[INFO] Extra levels found but --remove-extra-levels not specified.")
            print("       Removing topic associations from extra levels...")
            for item in extra_levels:
                level = item['level']
                level_num = item['level_num']
                # Remove all topic associations
                for topic in list(level.topics.all()):
                    level.topics.remove(topic)
                print(f"[FIXED] Removed all topic associations from Level {level_num}")
    
    # Summary
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"  Levels with fixed associations: {fixed_associations}")
    print(f"  Topic associations removed: {removed_associations}")
    print(f"  Topic associations added: {added_associations}")
    if remove_extra_levels:
        print(f"  Extra levels deleted: {deleted_levels}")
    print()
    print("[OK] Cleanup complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Remove Basic Facts duplicates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform the cleanup (default is dry-run)')
    parser.add_argument('--remove-extra-levels', action='store_true',
                       help='Delete extra levels 129, 130-139, 140-149 (DANGEROUS - only if they have no questions)')
    
    args = parser.parse_args()
    
    remove_basic_facts_duplicates(
        dry_run=not args.execute,
        remove_extra_levels=args.remove_extra_levels
    )

