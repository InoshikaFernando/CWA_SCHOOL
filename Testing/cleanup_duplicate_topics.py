#!/usr/bin/env python
"""
Clean up duplicate topics in the database
This script:
1. Finds topics with duplicate names
2. Consolidates them by keeping one topic and merging the rest
3. Updates all questions and level associations
4. Deletes duplicate topics
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Topic, Question, Level
from collections import defaultdict

def cleanup_duplicate_topics(dry_run=True):
    """
    Clean up duplicate topics
    
    Args:
        dry_run: If True, only show what would be done without making changes
    """
    
    print("[INFO] Finding duplicate topics...\n")
    
    # Group topics by name
    topics_by_name = defaultdict(list)
    all_topics = Topic.objects.all()
    
    for topic in all_topics:
        topics_by_name[topic.name].append(topic)
    
    # Find duplicates
    duplicates = {name: topics for name, topics in topics_by_name.items() if len(topics) > 1}
    
    if not duplicates:
        print("[OK] No duplicate topics found!")
        return
    
    print(f"[INFO] Found {len(duplicates)} topic name(s) with duplicates:\n")
    
    for topic_name, topics in duplicates.items():
        print(f"  '{topic_name}': {len(topics)} occurrences")
        for topic in topics:
            question_count = Question.objects.filter(topic=topic).count()
            level_count = topic.levels.count()
            print(f"    Topic ID {topic.id}: {question_count} questions, {level_count} level associations")
        print()
    
    if dry_run:
        print("[DRY RUN] This was a dry run. No changes were made.")
        print("         Run with dry_run=False to actually perform the cleanup.")
        return
    
    print("[INFO] Starting cleanup...\n")
    
    total_merged = 0
    total_questions_updated = 0
    total_levels_updated = 0
    total_deleted = 0
    
    for topic_name, topics in duplicates.items():
        print(f"[INFO] Processing duplicates for '{topic_name}'...")
        
        # Choose the topic to keep (prefer the one with the most questions)
        # If tied, prefer the one with the lowest ID (oldest)
        topics_with_counts = []
        for topic in topics:
            question_count = Question.objects.filter(topic=topic).count()
            topics_with_counts.append((topic, question_count))
        
        # Sort by question count (descending), then by ID (ascending)
        topics_with_counts.sort(key=lambda x: (-x[1], x[0].id))
        
        topic_to_keep = topics_with_counts[0][0]
        topics_to_merge = [t for t, _ in topics_with_counts[1:]]
        
        print(f"  [KEEP] Topic ID {topic_to_keep.id} (has {topics_with_counts[0][1]} questions)")
        
        # Merge each duplicate into the main topic
        for duplicate_topic in topics_to_merge:
            print(f"  [MERGE] Merging Topic ID {duplicate_topic.id} into Topic ID {topic_to_keep.id}...")
            
            # Update all questions that reference the duplicate topic
            questions_to_update = Question.objects.filter(topic=duplicate_topic)
            question_count = questions_to_update.count()
            if question_count > 0:
                questions_to_update.update(topic=topic_to_keep)
                print(f"    [OK] Updated {question_count} question(s)")
                total_questions_updated += question_count
            
            # Update all level associations
            levels_to_add = duplicate_topic.levels.all()
            level_count = levels_to_add.count()
            if level_count > 0:
                for level in levels_to_add:
                    if not topic_to_keep.levels.filter(pk=level.pk).exists():
                        topic_to_keep.levels.add(level)
                print(f"    [OK] Added {level_count} level association(s)")
                total_levels_updated += level_count
            
            # Delete the duplicate topic
            duplicate_topic.delete()
            print(f"    [OK] Deleted duplicate Topic ID {duplicate_topic.id}")
            total_deleted += 1
            total_merged += 1
        
        print()
    
    print("[SUMMARY]")
    print(f"  Topics merged: {total_merged}")
    print(f"  Questions updated: {total_questions_updated}")
    print(f"  Level associations updated: {total_levels_updated}")
    print(f"  Duplicate topics deleted: {total_deleted}")
    print("\n[OK] Cleanup complete!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up duplicate topics in the database')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually perform the cleanup (default is dry run)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 60)
        print()
    
    cleanup_duplicate_topics(dry_run=dry_run)
    
    if dry_run:
        print()
        print("=" * 60)
        print("To actually perform the cleanup, run:")
        print("  python cleanup_duplicate_topics.py --execute")
        print("=" * 60)

