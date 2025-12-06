#!/usr/bin/env python
"""
Diagnose why only 7 Angles questions are showing in production
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer

# Get Year 6 and Angles topic
level_6 = Level.objects.filter(level_number=6).first()
angles_topic = Topic.objects.filter(name="Angles").first()

if not level_6 or not angles_topic:
    print("[ERROR] Year 6 or Angles topic not found!")
    sys.exit(1)

# Get all Angles questions for Year 6
questions = Question.objects.filter(
    level=level_6,
    topic=angles_topic
).order_by('id')

print("=" * 80)
print("DIAGNOSING WHY ONLY 7 ANGLES QUESTIONS ARE SHOWING")
print("=" * 80)
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
print(f"Total questions: {questions.count()}")
print(f"Valid questions (will show in quiz): {len(valid_questions)}")
print(f"Invalid questions (will be filtered out): {len(invalid_questions)}")
print()

if len(valid_questions) < 20:
    print(f"[WARNING] Only {len(valid_questions)} valid questions found!")
    print("This is why only 7 (or fewer) questions are showing in production.")
    print()
    print("To fix:")
    print("1. Run: python Testing/check_angles_answers.py")
    print("2. Add missing answers to invalid questions")
    print("3. Or run: python Testing/fix_angles_duplicates.py to remove duplicates")

