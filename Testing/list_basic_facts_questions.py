"""
Script to list all Basic Facts questions with level numbers and topics.
Useful for reviewing and revising Basic Facts questions.
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

def list_basic_facts_questions(topic_filter=None, level_filter=None, output_format='table'):
    """
    List all Basic Facts questions with level numbers and topics.
    
    Args:
        topic_filter: Filter by specific topic name (e.g., "Addition", "Division")
        level_filter: Filter by specific level number (e.g., 100, 121)
        output_format: 'table' (default) or 'csv'
    """
    print("=" * 100)
    print("BASIC FACTS QUESTIONS LIST")
    print("=" * 100)
    
    # Get all Basic Facts levels (100-149)
    basic_facts_levels = Level.objects.filter(
        level_number__gte=100,
        level_number__lte=149
    ).order_by('level_number')
    
    # Get all questions in Basic Facts levels
    questions_query = Question.objects.filter(
        level__level_number__gte=100,
        level__level_number__lte=149
    ).select_related('level', 'topic').order_by('level__level_number', 'id')
    
    # Apply filters
    if topic_filter:
        questions_query = questions_query.filter(topic__name__icontains=topic_filter)
        print(f"\nFiltering by topic: {topic_filter}")
    
    if level_filter:
        questions_query = questions_query.filter(level__level_number=level_filter)
        print(f"Filtering by level: {level_filter}")
    
    total_questions = questions_query.count()
    print(f"\nTotal Basic Facts questions: {total_questions}")
    
    if total_questions == 0:
        print("\n[INFO] No Basic Facts questions found")
        return
    
    # Group by topic and level
    print(f"\n{'=' * 100}")
    print("QUESTIONS BY TOPIC AND LEVEL")
    print(f"{'=' * 100}")
    
    # Get all topics used in Basic Facts
    topics_used = questions_query.values('topic__name').annotate(
        count=Count('id')
    ).order_by('topic__name')
    
    print(f"\nTopics found:")
    for item in topics_used:
        topic_name = item['topic__name'] or "No Topic"
        print(f"  - {topic_name}: {item['count']} questions")
    
    # Group by level and topic
    level_topic_data = {}
    for question in questions_query:
        level_num = question.level.level_number if question.level else None
        topic_name = question.topic.name if question.topic else "No Topic"
        
        if level_num not in level_topic_data:
            level_topic_data[level_num] = {}
        if topic_name not in level_topic_data[level_num]:
            level_topic_data[level_num][topic_name] = []
        
        level_topic_data[level_num][topic_name].append(question)
    
    # Display organized by level and topic
    for level_num in sorted(level_topic_data.keys()):
        level_obj = Level.objects.filter(level_number=level_num).first()
        level_title = level_obj.title if level_obj else f"Level {level_num}"
        
        print(f"\n{'=' * 100}")
        print(f"LEVEL {level_num}: {level_title}")
        print(f"{'=' * 100}")
        
        for topic_name in sorted(level_topic_data[level_num].keys()):
            questions = level_topic_data[level_num][topic_name]
            
            print(f"\n  Topic: {topic_name} ({len(questions)} questions)")
            print(f"  {'-' * 98}")
            
            if output_format == 'table':
                print(f"  {'ID':<8} {'Question Text':<70} {'Answers':<10}")
                print(f"  {'-' * 98}")
                
                for question in questions:
                    question_text = question.question_text[:68] if question.question_text else "N/A"
                    answer_count = question.answers.count()
                    print(f"  {question.id:<8} {question_text:<70} {answer_count:<10}")
            else:  # csv format
                print(f"  Question ID,Question Text,Answer Count")
                for question in questions:
                    question_text = question.question_text.replace('"', '""') if question.question_text else "N/A"
                    answer_count = question.answers.count()
                    print(f"  {question.id},\"{question_text}\",{answer_count}")
    
    # Summary statistics
    print(f"\n{'=' * 100}")
    print("SUMMARY STATISTICS")
    print(f"{'=' * 100}")
    
    # Questions without topics
    no_topic = questions_query.filter(topic__isnull=True).count()
    if no_topic > 0:
        print(f"\n[WARNING] {no_topic} questions without topics assigned")
    
    # Questions without answers
    from maths.models import Answer
    questions_with_answers = questions_query.annotate(
        answer_count=Count('answers')
    ).filter(answer_count=0).count()
    
    if questions_with_answers > 0:
        print(f"[WARNING] {questions_with_answers} questions without answers")
    
    # Questions with single answer
    questions_with_one_answer = questions_query.annotate(
        answer_count=Count('answers')
    ).filter(answer_count=1).count()
    
    if questions_with_one_answer > 0:
        print(f"[INFO] {questions_with_one_answer} questions with only one answer")
    
    # Export option
    if output_format == 'csv':
        print(f"\n{'=' * 100}")
        print("CSV EXPORT")
        print(f"{'=' * 100}")
        print("\nTo export to CSV file, redirect output:")
        print("  python Testing/list_basic_facts_questions.py --format csv > basic_facts_questions.csv")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List all Basic Facts questions with level numbers and topics')
    parser.add_argument('--topic', type=str, help='Filter by topic name (e.g., "Addition", "Division")')
    parser.add_argument('--level', type=int, help='Filter by level number (e.g., 100, 121)')
    parser.add_argument('--format', type=str, choices=['table', 'csv'], default='table', help='Output format (default: table)')
    args = parser.parse_args()
    
    list_basic_facts_questions(
        topic_filter=args.topic,
        level_filter=args.level,
        output_format=args.format
    )

