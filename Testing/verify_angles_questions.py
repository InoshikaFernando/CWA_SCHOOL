#!/usr/bin/env python
"""
Verify Year 6 Angles questions in database and check topic association
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

if not level_6:
    print("[ERROR] Year 6 level not found!")
    sys.exit(1)

if not angles_topic:
    print("[ERROR] Angles topic not found!")
    sys.exit(1)

print("=" * 80)
print("VERIFYING YEAR 6 ANGLES QUESTIONS")
print("=" * 80)
print()

# Check topic association
print(f"Year 6 topics: {', '.join([t.name for t in level_6.topics.all()])}")
print(f"Is Angles associated with Year 6? {level_6.topics.filter(name='Angles').exists()}")
print()

# Get all Angles questions for Year 6
questions = Question.objects.filter(
    level=level_6,
    topic=angles_topic
).order_by('id')

print(f"Total Angles questions for Year 6: {questions.count()}")
print()

if questions.exists():
    print("Questions found:")
    for i, q in enumerate(questions, 1):
        correct_answer = q.answers.filter(is_correct=True).first()
        image_name = os.path.basename(q.image.name) if q.image else "None"
        print(f"  {i}. ID: {q.id} | Answer: {correct_answer.answer_text if correct_answer else 'None'} | Image: {image_name}")
else:
    print("[WARNING] No questions found!")
    print()
    
    # Check if questions exist but with wrong topic
    all_year6_questions = Question.objects.filter(level=level_6)
    print(f"Total Year 6 questions (all topics): {all_year6_questions.count()}")
    
    questions_without_topic = all_year6_questions.filter(topic__isnull=True)
    print(f"Year 6 questions without topic: {questions_without_topic.count()}")
    
    # Check if any questions have "angle" in the text
    angle_related = all_year6_questions.filter(question_text__icontains="angle")
    print(f"Year 6 questions with 'angle' in text: {angle_related.count()}")
    if angle_related.exists():
        print("  These questions:")
        for q in angle_related:
            print(f"    - ID: {q.id} | Topic: {q.topic.name if q.topic else 'None'} | Text: {q.question_text[:60]}...")

