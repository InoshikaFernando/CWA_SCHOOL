#!/usr/bin/env python
"""
Check which Year 6 Angles questions have answers
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
print("CHECKING YEAR 6 ANGLES QUESTIONS FOR ANSWERS")
print("=" * 80)
print()

questions_with_answers = []
questions_without_answers = []

for q in questions:
    answer_count = q.answers.count()
    correct_count = q.answers.filter(is_correct=True).count()
    wrong_count = q.answers.filter(is_correct=False).count()
    
    if answer_count == 0:
        questions_without_answers.append(q)
        print(f"[NO ANSWERS] ID {q.id}: {q.question_text[:60]}...")
    elif correct_count == 0:
        questions_without_answers.append(q)
        print(f"[NO CORRECT ANSWER] ID {q.id}: {q.question_text[:60]}... | Has {wrong_count} wrong answers")
    elif wrong_count == 0 and q.question_type in ['multiple_choice', 'true_false']:
        questions_without_answers.append(q)
        print(f"[NO WRONG ANSWERS] ID {q.id}: {q.question_text[:60]}... | Has {correct_count} correct answer(s)")
    else:
        questions_with_answers.append(q)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total questions: {questions.count()}")
print(f"Questions with valid answers: {len(questions_with_answers)}")
print(f"Questions without valid answers: {len(questions_without_answers)}")
print()

if questions_without_answers:
    print("[ISSUE] These questions may not appear in quizzes:")
    for q in questions_without_answers:
        print(f"  - ID {q.id}: {q.question_text[:60]}...")

