"""
Script to fix Division questions that have the wrong topic (Multiplication).
All questions in Division levels (121-127) should have Division topic.
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

def fix_division_topics(dry_run=True):
    """
    Fix all Division questions to have the correct Division topic.
    """
    print("=" * 100)
    if dry_run:
        print("FIXING DIVISION QUESTION TOPICS (DRY RUN)")
    else:
        print("FIXING DIVISION QUESTION TOPICS")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Get all Division levels (121-127)
    division_levels = Level.objects.filter(
        level_number__gte=121,
        level_number__lte=127
    ).order_by('level_number')
    
    print(f"\nDivision levels found: {division_levels.count()}")
    
    total_fixed = 0
    
    for level in division_levels:
        print(f"\n{'=' * 100}")
        print(f"Level {level.level_number}: {level.title}")
        print(f"{'=' * 100}")
        
        # Get all questions in this level
        questions = Question.objects.filter(level=level)
        total_questions = questions.count()
        
        # Count questions with wrong topic
        wrong_topic_questions = questions.exclude(topic=division_topic).exclude(topic__isnull=True)
        wrong_count = wrong_topic_questions.count()
        
        # Count questions without topic
        no_topic_questions = questions.filter(topic__isnull=True)
        no_topic_count = no_topic_questions.count()
        
        # Count questions with correct topic
        correct_topic_questions = questions.filter(topic=division_topic)
        correct_count = correct_topic_questions.count()
        
        print(f"  Total questions: {total_questions}")
        print(f"  Questions with Division topic: {correct_count}")
        print(f"  Questions with wrong topic: {wrong_count}")
        print(f"  Questions without topic: {no_topic_count}")
        
        if wrong_count > 0:
            # Show what wrong topics they have
            wrong_topics = wrong_topic_questions.values_list('topic__name', flat=True).distinct()
            print(f"  Wrong topics found: {list(wrong_topics)}")
            
            # Fix them
            if not dry_run:
                fixed = wrong_topic_questions.update(topic=division_topic)
                print(f"  [FIXED] Updated {fixed} questions to Division topic")
                total_fixed += fixed
            else:
                print(f"  [WOULD FIX] Would update {wrong_count} questions to Division topic")
                total_fixed += wrong_count
        
        if no_topic_count > 0:
            # Fix questions without topic
            if not dry_run:
                fixed = no_topic_questions.update(topic=division_topic)
                print(f"  [FIXED] Updated {fixed} questions without topic to Division topic")
                total_fixed += fixed
            else:
                print(f"  [WOULD FIX] Would update {no_topic_count} questions without topic to Division topic")
                total_fixed += no_topic_count
        
        # Verify
        remaining_wrong = questions.exclude(topic=division_topic).exclude(topic__isnull=True).count()
        remaining_no_topic = questions.filter(topic__isnull=True).count()
        
        if remaining_wrong == 0 and remaining_no_topic == 0:
            print(f"  [OK] All questions now have Division topic")
        else:
            print(f"  [WARNING] Still {remaining_wrong} with wrong topic, {remaining_no_topic} without topic")
    
    print(f"\n{'=' * 100}")
    print(f"SUMMARY")
    print(f"{'=' * 100}")
    print(f"Total questions fixed: {total_fixed}")
    
    # Final verification
    print(f"\n{'=' * 100}")
    print("FINAL VERIFICATION")
    print(f"{'=' * 100}")
    
    division_levels = Level.objects.filter(
        level_number__gte=121,
        level_number__lte=127
    ).order_by('level_number')
    
    all_correct = True
    for level in division_levels:
        questions = Question.objects.filter(level=level)
        wrong = questions.exclude(topic=division_topic).exclude(topic__isnull=True).count()
        no_topic = questions.filter(topic__isnull=True).count()
        
        if wrong > 0 or no_topic > 0:
            all_correct = False
            print(f"Level {level.level_number}: {wrong} wrong topic, {no_topic} no topic")
        else:
            print(f"Level {level.level_number}: [OK] All questions have Division topic")
    
    if all_correct:
        print(f"\n[SUCCESS] All Division questions now have the correct topic!")
    else:
        print(f"\n[WARNING] Some questions still need fixing")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fix Division question topics')
    parser.add_argument('--execute', action='store_true', help='Actually update the database (default is dry-run)')
    args = parser.parse_args()
    
    fix_division_topics(dry_run=not args.execute)
    
    if not args.execute:
        print("\n[DRY RUN] This was a dry run. Use --execute to actually update the database.")
        print("Review the output above, then run with --execute to apply changes.\n")

