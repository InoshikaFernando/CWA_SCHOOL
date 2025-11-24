"""
Script to backfill topics for existing Basic Facts questions.
Assigns topics based on level numbers.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Topic, Level
from django.db.models import Count
import argparse

def backfill_basic_facts_topics(dry_run=True):
    """
    Backfill topics for Basic Facts questions based on their level numbers.
    
    Level ranges:
    - 100-109: Addition
    - 110-119: Subtraction
    - 120-129: Multiplication
    - 121-127: Division (from generate script)
    - 130-139: Division (from create script)
    - 140-149: Place Value Facts
    """
    print("=" * 100)
    print("BACKFILLING TOPICS FOR BASIC FACTS QUESTIONS")
    print("=" * 100)
    
    if dry_run:
        print("\n[DRY RUN MODE] - No changes will be made to the database")
    else:
        print("\n[EXECUTE MODE] - Changes will be saved to the database")
    
    # Get all Basic Facts questions (levels 100-149)
    basic_facts_questions = Question.objects.filter(
        level__level_number__gte=100,
        level__level_number__lte=149
    ).select_related('level', 'topic')
    
    total_questions = basic_facts_questions.count()
    print(f"\nTotal Basic Facts questions found: {total_questions}")
    
    if total_questions == 0:
        print("\n[INFO] No Basic Facts questions found")
        return
    
    # Get topics
    addition_topic = Topic.objects.filter(name="Addition").first()
    subtraction_topic = Topic.objects.filter(name="Subtraction").first()
    multiplication_topic = Topic.objects.filter(name="Multiplication").first()
    division_topic = Topic.objects.filter(name="Division").first()
    place_value_topic = Topic.objects.filter(name="Place Value Facts").first()
    
    # Check which topics exist
    missing_topics = []
    if not addition_topic:
        missing_topics.append("Addition")
    if not subtraction_topic:
        missing_topics.append("Subtraction")
    if not multiplication_topic:
        missing_topics.append("Multiplication")
    if not division_topic:
        missing_topics.append("Division")
    if not place_value_topic:
        missing_topics.append("Place Value Facts")
    
    if missing_topics:
        print(f"\n[WARNING] Missing topics: {', '.join(missing_topics)}")
        print("Please run Questions/create_basic_facts.py first to create topics")
        return
    
    # Statistics
    stats = {
        'no_topic': 0,
        'wrong_topic': 0,
        'correct_topic': 0,
        'updated': 0,
        'skipped': 0
    }
    
    # Process each question
    print(f"\n{'=' * 100}")
    print("PROCESSING QUESTIONS")
    print(f"{'=' * 100}")
    
    for question in basic_facts_questions:
        level_num = question.level.level_number if question.level else None
        
        if not level_num:
            stats['skipped'] += 1
            continue
        
        # Determine correct topic based on level number
        correct_topic = None
        if 100 <= level_num <= 109:
            correct_topic = addition_topic
        elif 110 <= level_num <= 119:
            correct_topic = subtraction_topic
        elif 120 <= level_num <= 129:
            correct_topic = multiplication_topic
        elif 121 <= level_num <= 127 or 130 <= level_num <= 139:
            # Division can be in both ranges
            correct_topic = division_topic
        elif 140 <= level_num <= 149:
            correct_topic = place_value_topic
        else:
            stats['skipped'] += 1
            continue
        
        current_topic = question.topic
        
        if not current_topic:
            stats['no_topic'] += 1
            if not dry_run:
                question.topic = correct_topic
                question.save()
                stats['updated'] += 1
        elif current_topic != correct_topic:
            stats['wrong_topic'] += 1
            if not dry_run:
                question.topic = correct_topic
                question.save()
                stats['updated'] += 1
        else:
            stats['correct_topic'] += 1
    
    # Print summary
    print(f"\n{'=' * 100}")
    print("SUMMARY")
    print(f"{'=' * 100}")
    print(f"Questions without topic: {stats['no_topic']}")
    print(f"Questions with wrong topic: {stats['wrong_topic']}")
    print(f"Questions with correct topic: {stats['correct_topic']}")
    print(f"Questions skipped: {stats['skipped']}")
    
    if not dry_run:
        print(f"\nQuestions updated: {stats['updated']}")
        print(f"[SUCCESS] Topics backfilled successfully!")
    else:
        print(f"\nQuestions that would be updated: {stats['no_topic'] + stats['wrong_topic']}")
        print(f"[DRY RUN] Run with --execute to apply changes")
    
    # Show breakdown by level range
    print(f"\n{'=' * 100}")
    print("BREAKDOWN BY LEVEL RANGE")
    print(f"{'=' * 100}")
    
    level_ranges = [
        (100, 109, "Addition"),
        (110, 119, "Subtraction"),
        (120, 129, "Multiplication"),
        (121, 127, "Division"),
        (130, 139, "Division"),
        (140, 149, "Place Value Facts")
    ]
    
    for min_level, max_level, topic_name in level_ranges:
        questions_in_range = basic_facts_questions.filter(
            level__level_number__gte=min_level,
            level__level_number__lte=max_level
        )
        
        no_topic_count = questions_in_range.filter(topic__isnull=True).count()
        correct_topic_count = questions_in_range.filter(topic__name=topic_name).count()
        wrong_topic_count = questions_in_range.exclude(topic__name=topic_name).exclude(topic__isnull=True).count()
        
        print(f"\nLevels {min_level}-{max_level} ({topic_name}):")
        print(f"  Total questions: {questions_in_range.count()}")
        print(f"  Without topic: {no_topic_count}")
        print(f"  With correct topic: {correct_topic_count}")
        print(f"  With wrong topic: {wrong_topic_count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backfill topics for Basic Facts questions')
    parser.add_argument('--execute', action='store_true', help='Execute the backfill (default is dry-run)')
    args = parser.parse_args()
    
    backfill_basic_facts_topics(dry_run=not args.execute)

