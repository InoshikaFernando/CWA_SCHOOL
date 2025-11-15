#!/usr/bin/env python
"""
Check for Year 6 measurement questions without answers
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, Level, Topic

def check_year6_measurements_answers():
    """Check for Year 6 measurement questions without answers"""
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    if not level_6:
        print("[ERROR] Year 6 level not found")
        return
    
    # Get Measurements topic
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        print("[ERROR] Measurements topic not found")
        return
    
    # Get all Year 6 measurement questions
    questions = Question.objects.filter(
        level=level_6,
        topic=measurements_topic
    ).order_by('id')
    
    print(f"\n[INFO] Checking {questions.count()} Year 6 measurement questions for answers...\n")
    
    questions_without_answers = []
    
    for question in questions:
        answer_count = question.answers.count()
        
        if answer_count == 0:
            questions_without_answers.append(question)
            print(f"[MISSING] Question ID {question.id}:")
            print(f"  Type: {question.question_type}")
            print(f"  Text: {question.question_text[:100]}...")
            if question.image:
                print(f"  Image: {question.image.name}")
            print(f"  Answers: {answer_count}")
            print()
    
    if questions_without_answers:
        print(f"\n[RESULT] Found {len(questions_without_answers)} Year 6 measurement questions without answers:")
        for q in questions_without_answers:
            print(f"  - ID {q.id}: {q.question_text[:80]}...")
    else:
        print(f"\n[OK] All Year 6 measurement questions have answers!")
    
    return questions_without_answers

if __name__ == "__main__":
    check_year6_measurements_answers()

