#!/usr/bin/env python
"""
Fix duplicate Year 6 Angles questions by removing duplicates
Keeps the question with the most complete data (answers, image, etc.)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer
from collections import defaultdict

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
print("FIXING DUPLICATE YEAR 6 ANGLES QUESTIONS")
print("=" * 80)
print(f"Total questions found: {questions.count()}")
print()

# Group questions by question_text, correct_answer, and image base name
question_groups = defaultdict(list)

for q in questions:
    # Get correct answer
    correct_answer = q.answers.filter(is_correct=True).first()
    correct_ans_text = correct_answer.answer_text if correct_answer else ""
    
    # Get image base name (without Django suffix)
    image_base = ""
    if q.image and q.image.name:
        image_filename = os.path.basename(q.image.name)
        image_base = os.path.splitext(image_filename)[0]
        # Remove Django suffix (anything after underscore before extension)
        if '_' in image_base:
            image_base = image_base.split('_')[0]
    
    # Create a key for grouping
    key = (q.question_text, correct_ans_text, image_base)
    question_groups[key].append(q)

# Find duplicates
duplicates_to_delete = []
questions_to_keep = []

for key, group in question_groups.items():
    if len(group) > 1:
        print(f"[DUPLICATE] Found {len(group)} questions with:")
        print(f"  Text: {key[0][:60]}...")
        print(f"  Answer: {key[1]}")
        print(f"  Image: {key[2]}")
        
        # Keep the one with the most answers, or the first one if equal
        best_question = max(group, key=lambda q: (
            q.answers.count(),
            q.image is not None,
            q.id  # Prefer lower ID (older)
        ))
        
        questions_to_keep.append(best_question)
        for q in group:
            if q.id != best_question.id:
                duplicates_to_delete.append(q)
                print(f"    Will delete: ID {q.id}")
        print()

print(f"\n[SUMMARY]")
print(f"  Questions to keep: {len(questions_to_keep)}")
print(f"  Duplicates to delete: {len(duplicates_to_delete)}")
print()

if duplicates_to_delete:
    response = input("Delete duplicate questions? (yes/no): ")
    if response.lower() == 'yes':
        deleted_count = 0
        for q in duplicates_to_delete:
            print(f"Deleting question ID {q.id}...")
            q.delete()
            deleted_count += 1
        print(f"\n[OK] Deleted {deleted_count} duplicate questions")
    else:
        print("[SKIP] No questions deleted")
else:
    print("[OK] No duplicates found!")

