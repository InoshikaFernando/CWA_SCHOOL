"""
Script to check all Division-related levels and fix any mismatches.
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

def check_all_division_levels():
    """
    Check all levels that might be Division-related.
    """
    print("=" * 100)
    print("CHECKING ALL DIVISION-RELATED LEVELS")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Check levels 121-139 (where Division might be)
    print(f"\n{'=' * 100}")
    print("LEVELS 121-139 (POTENTIAL DIVISION LEVELS)")
    print(f"{'=' * 100}")
    print(f"\n{'Level':<10} {'Title':<60} {'Linked Topics':<40} {'Questions':<15} {'Division Qs':<15}")
    print("-" * 100)
    
    for level_num in range(121, 140):
        try:
            level = Level.objects.get(level_number=level_num)
            linked_topics = [t.name for t in level.topics.all()]
            total_questions = level.questions.count()
            division_questions = level.questions.filter(topic=division_topic).count()
            
            is_division_linked = 'Division' in linked_topics
            status = "[DIVISION]" if is_division_linked else "[OTHER]"
            
            print(f"{level_num:<10} {level.title[:58]:<60} {', '.join(linked_topics)[:38]:<40} {total_questions:<15} {division_questions:<15} {status}")
        except Level.DoesNotExist:
            print(f"{level_num:<10} {'[DOES NOT EXIST]':<60} {'':<40} {'':<15} {'':<15}")
    
    # Summary
    print(f"\n{'=' * 100}")
    print("SUMMARY")
    print(f"{'=' * 100}")
    
    # Levels linked to Division
    division_linked_levels = Level.objects.filter(
        topics=division_topic,
        level_number__gte=121,
        level_number__lte=139
    ).order_by('level_number')
    
    print(f"\nLevels linked to Division topic (121-139): {division_linked_levels.count()}")
    for level in division_linked_levels:
        print(f"  - Level {level.level_number}: {level.title}")
    
    # Levels with Division questions
    levels_with_division_questions = Level.objects.filter(
        questions__topic=division_topic,
        level_number__gte=121,
        level_number__lte=139
    ).distinct().order_by('level_number')
    
    print(f"\nLevels with Division questions (121-139): {levels_with_division_questions.count()}")
    for level in levels_with_division_questions:
        div_q_count = level.questions.filter(topic=division_topic).count()
        print(f"  - Level {level.level_number}: {div_q_count} Division questions")
    
    # Check for mismatches
    print(f"\n{'=' * 100}")
    print("MISMATCHES")
    print(f"{'=' * 100}")
    
    # Levels with Division questions but not linked to Division topic
    mismatched = []
    for level in levels_with_division_questions:
        if 'Division' not in [t.name for t in level.topics.all()]:
            mismatched.append(level)
            print(f"  [MISMATCH] Level {level.level_number} has Division questions but is NOT linked to Division topic")
    
    # Levels linked to Division topic but no Division questions
    for level in division_linked_levels:
        div_q_count = level.questions.filter(topic=division_topic).count()
        if div_q_count == 0:
            print(f"  [MISMATCH] Level {level.level_number} is linked to Division topic but has NO Division questions")

if __name__ == '__main__':
    check_all_division_levels()

