"""
Script to check what Division levels are linked to Division topic.
This will help identify why the website shows many levels.
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

def check_division_levels_production():
    """
    Check all levels linked to Division topic - this is what the website shows.
    """
    print("=" * 100)
    print("CHECKING ALL LEVELS LINKED TO DIVISION TOPIC")
    print("(These are what appear on the website)")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Get ALL levels linked to Division topic (this is what the website queries)
    division_levels = Level.objects.filter(
        topics=division_topic
    ).order_by('level_number')
    
    print(f"\nTotal levels linked to Division topic: {division_levels.count()}")
    
    if division_levels.count() == 0:
        print("\n[INFO] No levels linked to Division topic")
        return
    
    print(f"\n{'=' * 100}")
    print("ALL LEVELS LINKED TO DIVISION TOPIC")
    print("(These will appear on /basic-facts/Division/)")
    print(f"{'=' * 100}")
    print(f"\n{'Level #':<12} {'Display Level':<15} {'Title':<50} {'Questions':<12} {'Div Qs':<12} {'Other Topics':<30}")
    print("-" * 100)
    
    for level in division_levels:
        # Calculate display level (what shows on website)
        display_level = level.level_number
        if 121 <= level.level_number <= 127:
            display_level = level.level_number - 120
        elif 130 <= level.level_number <= 139:
            display_level = level.level_number - 129  # This might be wrong
        
        # Count questions
        total_questions = level.questions.count()
        division_questions = level.questions.filter(topic=division_topic).count()
        
        # Get other topics linked to this level
        other_topics = [t.name for t in level.topics.all() if t.name != "Division"]
        other_topics_str = ", ".join(other_topics) if other_topics else "None"
        
        print(f"{level.level_number:<12} {display_level:<15} {level.title[:48]:<50} {total_questions:<12} {division_questions:<12} {other_topics_str[:28]:<30}")
    
    # Check for potential issues
    print(f"\n{'=' * 100}")
    print("POTENTIAL ISSUES")
    print(f"{'=' * 100}")
    
    # Levels with no questions
    levels_no_questions = [l for l in division_levels if l.questions.count() == 0]
    if levels_no_questions:
        print(f"\n[ISSUE] {len(levels_no_questions)} levels have NO questions:")
        for level in levels_no_questions:
            print(f"  - Level {level.level_number}: {level.title}")
        print("  These levels will appear on the website but have no questions!")
    
    # Levels with questions but wrong topic
    levels_wrong_topic = []
    for level in division_levels:
        total_q = level.questions.count()
        div_q = level.questions.filter(topic=division_topic).count()
        if total_q > 0 and div_q == 0:
            levels_wrong_topic.append(level)
    
    if levels_wrong_topic:
        print(f"\n[ISSUE] {len(levels_wrong_topic)} levels have questions but NONE have Division topic:")
        for level in levels_wrong_topic:
            wrong_topics = level.questions.values_list('topic__name', flat=True).distinct()
            print(f"  - Level {level.level_number}: {level.title}")
            print(f"    Questions have topics: {list(wrong_topics)}")
    
    # Check for levels 130-139 (should they be Division?)
    levels_130_139 = [l for l in division_levels if 130 <= l.level_number <= 139]
    if levels_130_139:
        print(f"\n[INFO] {len(levels_130_139)} levels in range 130-139 are linked to Division:")
        for level in levels_130_139:
            print(f"  - Level {level.level_number}: {level.title} ({level.questions.count()} questions)")
        print("  According to create_basic_facts.py, these should be Division levels.")
        print("  But generate_basic_facts_questions.py creates questions in 121-127.")
        print("  This mismatch causes empty levels to appear on the website.")
    
    # Summary
    print(f"\n{'=' * 100}")
    print("SUMMARY")
    print(f"{'=' * 100}")
    print(f"Total levels linked to Division: {division_levels.count()}")
    print(f"Levels with questions: {sum(1 for l in division_levels if l.questions.count() > 0)}")
    print(f"Levels with Division questions: {sum(1 for l in division_levels if l.questions.filter(topic=division_topic).count() > 0)}")
    print(f"Levels with no questions: {len(levels_no_questions)}")
    
    if levels_no_questions:
        print(f"\n[RECOMMENDATION] Unlink levels 130-139 from Division topic if they have no questions.")
        print(f"  Or create questions for them if they should be Division levels.")

if __name__ == '__main__':
    check_division_levels_production()

