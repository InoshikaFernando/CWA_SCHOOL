#!/usr/bin/env python
"""
Check Year 7 Measurements questions in database
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer

# Get Year 7 and Measurements topic
level_7 = Level.objects.filter(level_number=7).first()
measurements_topic = Topic.objects.filter(name="Measurements").first()

if not level_7 or not measurements_topic:
    print("[ERROR] Year 7 or Measurements topic not found!")
    sys.exit(1)

# Get all Measurements questions for Year 7
questions = Question.objects.filter(
    level=level_7,
    topic=measurements_topic
).order_by('id')

print("=" * 80)
print("YEAR 7 MEASUREMENTS QUESTIONS CHECK")
print("=" * 80)
print(f"Total questions found: {questions.count()}")
print()

valid_questions = []
invalid_questions = []

for q in questions:
    answer_count = q.answers.count()
    correct_count = q.answers.filter(is_correct=True).count()
    wrong_count = q.answers.filter(is_correct=False).count()
    
    is_valid = True
    issues = []
    
    if answer_count == 0:
        is_valid = False
        issues.append("NO ANSWERS")
    elif correct_count == 0:
        is_valid = False
        issues.append("NO CORRECT ANSWER")
    elif q.question_type in ['multiple_choice', 'true_false'] and wrong_count == 0:
        is_valid = False
        issues.append("NO WRONG ANSWERS (MCQ needs at least one wrong answer)")
    
    if is_valid:
        valid_questions.append(q)
        print(f"[VALID] ID {q.id}: {q.question_text[:60]}... | {correct_count} correct, {wrong_count} wrong")
    else:
        invalid_questions.append(q)
        print(f"[INVALID] ID {q.id}: {q.question_text[:60]}... | Issues: {', '.join(issues)} | {answer_count} total answers")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total questions in database: {questions.count()}")
print(f"Valid questions (will show in quiz): {len(valid_questions)}")
print(f"Invalid questions (will be filtered out): {len(invalid_questions)}")
print()
print(f"Expected questions for Year 7: 22")
print(f"Actual valid questions: {len(valid_questions)}")
print()

if len(valid_questions) < 22:
    print(f"[WARNING] Only {len(valid_questions)} valid questions found!")
    print("This is why only 6 (or fewer) questions are showing in production.")
    print()
    if invalid_questions:
        print("Invalid questions that need fixing:")
        for q in invalid_questions:
            print(f"  - ID {q.id}: {q.question_text[:60]}...")

