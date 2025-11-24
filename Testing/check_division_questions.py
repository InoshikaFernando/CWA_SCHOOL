"""
Script to check Division topic questions and identify if they contain Addition questions.
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
import argparse

def check_division_questions():
    """
    Check Division topic questions and identify misclassified questions.
    """
    print("=" * 100)
    print("CHECKING DIVISION TOPIC QUESTIONS")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name__icontains='Division').first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Get all Division questions
    division_questions = Question.objects.filter(topic=division_topic).select_related('level')
    
    print(f"\nTotal Division questions: {division_questions.count()}")
    
    if division_questions.count() == 0:
        print("\n[INFO] No questions found in Division topic")
        return
    
    # Check for questions that might be Addition questions
    addition_keywords = ['add', 'plus', '+', 'sum', 'total', 'together', 'combine', 'more than']
    division_keywords = ['divide', 'division', '/', '÷', 'split', 'share', 'group', 'quotient', 'remainder']
    
    print(f"\n{'=' * 100}")
    print("ANALYZING QUESTIONS FOR MISCLASSIFICATION")
    print(f"{'=' * 100}")
    
    suspicious_questions = []
    correct_questions = []
    
    for question in division_questions:
        question_text_lower = question.question_text.lower() if question.question_text else ""
        
        # Count addition keywords
        addition_count = sum(1 for keyword in addition_keywords if keyword in question_text_lower)
        division_count = sum(1 for keyword in division_keywords if keyword in question_text_lower)
        
        # Check if question text contains addition keywords but not division keywords
        if addition_count > 0 and division_count == 0:
            suspicious_questions.append({
                'question': question,
                'addition_keywords': addition_count,
                'division_keywords': division_count,
                'reason': 'Contains addition keywords but no division keywords'
            })
        elif division_count > 0:
            correct_questions.append(question)
        else:
            # Neither addition nor division keywords - might need manual review
            suspicious_questions.append({
                'question': question,
                'addition_keywords': addition_count,
                'division_keywords': division_count,
                'reason': 'No clear division or addition keywords'
            })
    
    print(f"\nCorrect Division questions: {len(correct_questions)}")
    print(f"Suspicious/Misclassified questions: {len(suspicious_questions)}")
    
    if suspicious_questions:
        print(f"\n{'=' * 100}")
        print("SUSPICIOUS QUESTIONS (Might be Addition, not Division)")
        print(f"{'=' * 100}")
        print(f"\n{'Question ID':<15} {'Level':<10} {'Question Text':<60} {'Reason':<40}")
        print("-" * 100)
        
        for item in suspicious_questions:
            question = item['question']
            level_num = question.level.level_number if question.level else "N/A"
            level_name = f"Year {level_num}" if level_num != "N/A" and level_num < 100 else f"Level {level_num}" if level_num != "N/A" else "N/A"
            question_text = question.question_text[:58] if question.question_text else "N/A"
            reason = item['reason'][:38]
            
            print(f"{question.id:<15} {level_name:<10} {question_text:<60} {reason:<40}")
    
    # Also check Addition topic to see if Division questions are there
    print(f"\n{'=' * 100}")
    print("CHECKING ADDITION TOPIC FOR COMPARISON")
    print(f"{'=' * 100}")
    
    addition_topic = Topic.objects.filter(name__icontains='Addition').first()
    if addition_topic:
        addition_questions = Question.objects.filter(topic=addition_topic).select_related('level')
        print(f"\nAddition Topic: {addition_topic.name} (ID: {addition_topic.id})")
        print(f"Total Addition questions: {addition_questions.count()}")
        
        # Check if any Division questions appear in Addition topic
        division_question_ids = set(division_questions.values_list('id', flat=True))
        addition_question_ids = set(addition_questions.values_list('id', flat=True))
        
        overlap = division_question_ids & addition_question_ids
        
        if overlap:
            print(f"\n[WARNING] Found {len(overlap)} questions that are in BOTH Division and Addition topics!")
            print(f"Question IDs: {list(overlap)}")
        else:
            print(f"\n[OK] No overlap between Division and Addition topics")
    else:
        print(f"\n[INFO] Addition topic not found")
    
    # Show sample of correct Division questions
    if correct_questions:
        print(f"\n{'=' * 100}")
        print("SAMPLE OF CORRECT DIVISION QUESTIONS")
        print(f"{'=' * 100}")
        print(f"\n{'Question ID':<15} {'Level':<10} {'Question Text':<60}")
        print("-" * 100)
        
        for question in correct_questions[:10]:  # Show first 10
            level_num = question.level.level_number if question.level else "N/A"
            level_name = f"Year {level_num}" if level_num != "N/A" and level_num < 100 else f"Level {level_num}" if level_num != "N/A" else "N/A"
            question_text = question.question_text[:58] if question.question_text else "N/A"
            print(f"{question.id:<15} {level_name:<10} {question_text:<60}")

if __name__ == '__main__':
    check_division_questions()

