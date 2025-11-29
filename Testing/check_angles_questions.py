#!/usr/bin/env python
"""
Diagnostic script to check Year 6 Angles questions in the database
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

# Get all Angles questions for Year 6
questions = Question.objects.filter(
    level=level_6,
    topic=angles_topic
).order_by('id')

print("=" * 80)
print(f"YEAR 6 ANGLES QUESTIONS IN DATABASE")
print("=" * 80)
print(f"Total questions found: {questions.count()}")
print()

if questions.exists():
    for i, q in enumerate(questions, 1):
        print(f"Question {i} (ID: {q.id}):")
        print(f"  Text: {q.question_text[:80]}...")
        print(f"  Image: {q.image.name if q.image else 'None'}")
        
        # Get answers
        correct_answer = q.answers.filter(is_correct=True).first()
        wrong_answers = list(q.answers.filter(is_correct=False).values_list('answer_text', flat=True))
        
        print(f"  Correct: {correct_answer.answer_text if correct_answer else 'None'}")
        print(f"  Wrong: {wrong_answers}")
        print()
else:
    print("[INFO] No questions found in database.")
    print()

# Expected questions from the script
expected_questions = [
    ("Without using a protractor, find the value of the pronumeral 𝑎", "18°", "image1.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "82°", "image2.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "82°", "image3.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "106°", "image4.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "34°", "image5.png"),
    ("Without using a protractor, find the values of the pronumerals 𝑎 and 𝑏", "a = 70°, b = 110°", "image6.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "92°", "image7.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "83°", "image8.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "57°", "image9.png"),
    ("Without using a protractor, find the value of the pronumeral 𝑎", "148°", "image10.png"),
    ("Two lines cut by the transversal are parallel.", "False", "image11.png"),
    ("Two lines cut by the transversal are parallel.", "True", "image12.png"),
    ("Find the values of the pronumerals 𝑎 and 𝑏", "a = 42°, b = 48°", "image13.png"),
    ("Find the values of the pronumerals 𝑎 and 𝑏", "a = 284°, b = 104°", "image14.png"),
    ("Find the value of the pronumeral 𝑎", "45°", "image15.png"),
    ("Find the value of the pronumeral 𝑎", "50°", "image16.png"),
    ("Find the values of the pronumerals 𝑎 and 𝑥", "a = 40°, x = 140°", "image17.png"),
    ("Find the value of the pronumeral 𝑎", "78°", "image18.png"),
    ("Find the value of the pronumeral 𝑎", "55°", "image19.png"),
    ("Which angle corresponds to ∠BAF?", "∠EDF", "image20.png"),
]

print("=" * 80)
print("EXPECTED QUESTIONS (from script)")
print("=" * 80)
print(f"Total expected: {len(expected_questions)}")
print()

# Check which expected questions exist
missing_questions = []
for q_text, correct_ans, image_name in expected_questions:
    # Find matching question
    matching = questions.filter(question_text=q_text)
    
    # Check by correct answer and image
    found = False
    for q in matching:
        correct = q.answers.filter(is_correct=True).first()
        if correct and correct.answer_text == correct_ans:
            if image_name:
                if q.image and (image_name in q.image.name or os.path.basename(q.image.name) == image_name):
                    found = True
                    break
                elif not q.image:
                    # Question exists but no image - might be a match
                    pass
            else:
                found = True
                break
    
    if not found:
        missing_questions.append((q_text[:50], correct_ans, image_name))

if missing_questions:
    print(f"[MISSING] {len(missing_questions)} questions not found:")
    for q_text, correct_ans, image_name in missing_questions:
        print(f"  - {q_text}... | Answer: {correct_ans} | Image: {image_name}")
else:
    print("[OK] All expected questions found in database!")

