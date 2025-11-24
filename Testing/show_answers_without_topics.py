"""
Script to show StudentAnswer records that don't have topics assigned.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, CustomUser
from django.db.models import Count
import argparse

def show_answers_without_topics(username=None, limit=None):
    """
    Show StudentAnswer records where the question doesn't have a topic.
    """
    print("=" * 100)
    print("STUDENT ANSWERS WITHOUT TOPICS")
    print("=" * 100)
    
    # Get all student answers where question has no topic
    answers_query = StudentAnswer.objects.filter(
        question__topic__isnull=True
    ).select_related('student', 'question', 'question__level')
    
    if username:
        answers_query = answers_query.filter(student__username=username)
    
    total_count = answers_query.count()
    
    print(f"\nTotal StudentAnswer records without topics: {total_count}")
    
    if total_count == 0:
        print("\n[OK] No student answers found without topics!")
        return
    
    # Group by student
    student_counts = answers_query.values('student__username').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print(f"\nGrouped by student:")
    print(f"{'Student':<30} {'Count':<10}")
    print("-" * 100)
    for item in student_counts:
        print(f"{item['student__username']:<30} {item['count']:<10}")
    
    # Group by level
    level_counts = answers_query.values('question__level__level_number').annotate(
        count=Count('id')
    ).order_by('question__level__level_number')
    
    print(f"\nGrouped by level:")
    print(f"{'Level':<10} {'Count':<10}")
    print("-" * 100)
    for item in level_counts:
        level_num = item['question__level__level_number']
        level_name = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
        print(f"{level_name:<10} {item['count']:<10}")
    
    # Show detailed records
    print(f"\n{'=' * 100}")
    print("DETAILED RECORDS")
    print(f"{'=' * 100}")
    
    answers = answers_query.order_by('student__username', 'question__level__level_number', 'answered_at')
    
    if limit:
        answers = answers[:limit]
        print(f"\nShowing first {limit} records:")
    else:
        print(f"\nShowing all {total_count} records:")
    
    print(f"\n{'Student':<25} {'Level':<10} {'Question ID':<15} {'Question Text':<50} {'Answered At':<25}")
    print("-" * 100)
    
    for answer in answers:
        student_name = answer.student.username[:24]
        level_num = answer.question.level.level_number if answer.question.level else "N/A"
        level_name = f"Year {level_num}" if level_num != "N/A" and level_num < 100 else f"Level {level_num}" if level_num != "N/A" else "N/A"
        question_id = answer.question.id
        question_text = answer.question.question_text[:48] if answer.question.question_text else "N/A"
        answered_at = answer.answered_at.strftime("%Y-%m-%d %H:%M:%S") if answer.answered_at else "N/A"
        
        print(f"{student_name:<25} {level_name:<10} {question_id:<15} {question_text:<50} {answered_at:<25}")
    
    if limit and total_count > limit:
        print(f"\n... and {total_count - limit} more records (use --limit to see more)")
    
    # Show questions that need topics
    print(f"\n{'=' * 100}")
    print("QUESTIONS THAT NEED TOPICS ASSIGNED")
    print(f"{'=' * 100}")
    
    question_ids = answers_query.values_list('question_id', flat=True).distinct()
    questions = Question.objects.filter(id__in=question_ids).select_related('level')
    
    print(f"\nTotal unique questions without topics: {questions.count()}")
    print(f"\n{'Question ID':<15} {'Level':<10} {'Question Text':<60}")
    print("-" * 100)
    
    for question in questions[:50]:  # Show first 50
        level_num = question.level.level_number if question.level else "N/A"
        level_name = f"Year {level_num}" if level_num != "N/A" and level_num < 100 else f"Level {level_num}" if level_num != "N/A" else "N/A"
        question_text = question.question_text[:58] if question.question_text else "N/A"
        print(f"{question.id:<15} {level_name:<10} {question_text:<60}")
    
    if questions.count() > 50:
        print(f"\n... and {questions.count() - 50} more questions (showing first 50)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show StudentAnswer records without topics')
    parser.add_argument('--username', type=str, help='Filter by specific username')
    parser.add_argument('--limit', type=int, help='Limit number of records to show')
    args = parser.parse_args()
    
    show_answers_without_topics(username=args.username, limit=args.limit)

