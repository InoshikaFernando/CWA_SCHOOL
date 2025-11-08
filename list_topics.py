#!/usr/bin/env python
"""
List all topics in the database with their details
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Topic, Question, Level
from collections import Counter

def list_all_topics():
    """List all topics with their details"""
    
    print("[INFO] Fetching all topics from database...\n")
    
    all_topics = Topic.objects.all().order_by('name', 'id')
    
    if not all_topics.exists():
        print("[INFO] No topics found in database.")
        return
    
    print(f"[INFO] Found {all_topics.count()} topic(s):\n")
    print("=" * 80)
    print(f"{'ID':<6} {'Name':<30} {'Questions':<12} {'Levels':<12} {'Duplicate?'}")
    print("=" * 80)
    
    # Count topic names to find duplicates
    topic_names = [topic.name for topic in all_topics]
    name_counts = Counter(topic_names)
    
    for topic in all_topics:
        question_count = Question.objects.filter(topic=topic).count()
        level_count = topic.levels.count()
        is_duplicate = name_counts[topic.name] > 1
        duplicate_marker = "YES" if is_duplicate else ""
        
        print(f"{topic.id:<6} {topic.name:<30} {question_count:<12} {level_count:<12} {duplicate_marker}")
    
    print("=" * 80)
    
    # Show duplicate summary
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    if duplicates:
        print(f"\n[WARNING] Found {len(duplicates)} topic name(s) with duplicates:")
        for topic_name, count in duplicates.items():
            print(f"  '{topic_name}': {count} occurrences")
            topics = Topic.objects.filter(name=topic_name)
            topic_ids = [str(t.id) for t in topics]
            print(f"    Topic IDs: {', '.join(topic_ids)}")
    else:
        print("\n[OK] No duplicate topic names found!")
    
    # Show topics with no questions
    topics_without_questions = []
    for topic in all_topics:
        if Question.objects.filter(topic=topic).count() == 0:
            topics_without_questions.append(topic)
    
    if topics_without_questions:
        print(f"\n[INFO] Found {len(topics_without_questions)} topic(s) with no questions:")
        for topic in topics_without_questions:
            print(f"  - ID {topic.id}: '{topic.name}'")
    
    # Show topics with no level associations
    topics_without_levels = []
    for topic in all_topics:
        if topic.levels.count() == 0:
            topics_without_levels.append(topic)
    
    if topics_without_levels:
        print(f"\n[INFO] Found {len(topics_without_levels)} topic(s) with no level associations:")
        for topic in topics_without_levels:
            print(f"  - ID {topic.id}: '{topic.name}'")

if __name__ == "__main__":
    list_all_topics()

