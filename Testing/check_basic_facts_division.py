"""
Script to check Basic Facts Division questions and see if they're misclassified as Addition.
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

def check_basic_facts_division():
    """
    Check Basic Facts Division questions for misclassification.
    """
    print("=" * 100)
    print("CHECKING BASIC FACTS DIVISION QUESTIONS")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    addition_topic = Topic.objects.filter(name="Addition").first()
    
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    if not addition_topic:
        print("\n[ERROR] Addition topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    print(f"Addition Topic: {addition_topic.name} (ID: {addition_topic.id})")
    
    # Get Basic Facts Division levels (121-127)
    division_levels = Level.objects.filter(level_number__gte=121, level_number__lte=127)
    
    print(f"\nBasic Facts Division levels: {[l.level_number for l in division_levels]}")
    
    # Get all questions in Division levels
    division_level_questions = Question.objects.filter(
        level__level_number__gte=121,
        level__level_number__lte=127
    ).select_related('level', 'topic')
    
    print(f"\nTotal questions in Division levels (121-127): {division_level_questions.count()}")
    
    # Check topic assignment
    print(f"\n{'=' * 100}")
    print("TOPIC ASSIGNMENT ANALYSIS")
    print(f"{'=' * 100}")
    
    # Group by topic
    from django.db.models import Count
    topic_counts = division_level_questions.values('topic__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print(f"\nQuestions in Division levels grouped by topic:")
    print(f"{'Topic':<30} {'Count':<10}")
    print("-" * 100)
    for item in topic_counts:
        topic_name = item['topic__name'] or "No Topic"
        count = item['count']
        print(f"{topic_name:<30} {count:<10}")
    
    # Check for questions in Division levels that have Addition topic
    addition_in_division_levels = division_level_questions.filter(topic=addition_topic)
    
    print(f"\n{'=' * 100}")
    print("MISCLASSIFIED QUESTIONS (Division levels with Addition topic)")
    print(f"{'=' * 100}")
    
    if addition_in_division_levels.exists():
        print(f"\n[WARNING] Found {addition_in_division_levels.count()} questions in Division levels (121-127) that have Addition topic!")
        
        print(f"\n{'Question ID':<15} {'Level':<10} {'Question Text':<60} {'Current Topic':<20}")
        print("-" * 100)
        
        for question in addition_in_division_levels[:50]:  # Show first 50
            level_num = question.level.level_number if question.level else "N/A"
            level_name = f"Level {level_num}"
            question_text = question.question_text[:58] if question.question_text else "N/A"
            topic_name = question.topic.name if question.topic else "No Topic"
            
            print(f"{question.id:<15} {level_name:<10} {question_text:<60} {topic_name:<20}")
        
        if addition_in_division_levels.count() > 50:
            print(f"\n... and {addition_in_division_levels.count() - 50} more questions")
        
        print(f"\n{'=' * 100}")
        print("RECOMMENDATION")
        print(f"{'=' * 100}")
        print(f"\nThese questions should have Division topic, not Addition topic.")
        print(f"Would you like to fix them? (This would require a script to update them)")
    else:
        print(f"\n[OK] No questions in Division levels have Addition topic")
    
    # Check for questions that should be in Division topic but aren't
    division_topic_questions = Question.objects.filter(topic=division_topic)
    print(f"\n{'=' * 100}")
    print("QUESTIONS WITH DIVISION TOPIC")
    print(f"{'=' * 100}")
    print(f"\nTotal questions with Division topic: {division_topic_questions.count()}")
    
    if division_topic_questions.exists():
        # Check their levels
        level_counts = division_topic_questions.values('level__level_number').annotate(
            count=Count('id')
        ).order_by('level__level_number')
        
        print(f"\nDivision topic questions by level:")
        print(f"{'Level':<10} {'Count':<10}")
        print("-" * 100)
        for item in level_counts:
            level_num = item['level__level_number']
            level_name = f"Level {level_num}" if level_num >= 100 else f"Year {level_num}"
            print(f"{level_name:<10} {item['count']:<10}")
    
    # Show sample of correct Division questions
    correct_division = division_level_questions.filter(topic=division_topic)
    if correct_division.exists():
        print(f"\n{'=' * 100}")
        print("SAMPLE OF CORRECT DIVISION QUESTIONS")
        print(f"{'=' * 100}")
        print(f"\n{'Question ID':<15} {'Level':<10} {'Question Text':<60}")
        print("-" * 100)
        
        for question in correct_division[:10]:
            level_num = question.level.level_number if question.level else "N/A"
            level_name = f"Level {level_num}"
            question_text = question.question_text[:58] if question.question_text else "N/A"
            print(f"{question.id:<15} {level_name:<10} {question_text:<60}")

if __name__ == '__main__':
    check_basic_facts_division()

