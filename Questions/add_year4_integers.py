#!/usr/bin/env python
"""
Add/Update "Integers" questions for Year 4
This script can be run multiple times - it will:
- Add new questions if they don't exist
- Update answers if they've changed
- Skip questions that are already up-to-date
"""
import os
import sys
import django
import random

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer
from django.core.files import File
from django.conf import settings
from question_utils import process_questions


def setup_integers_topic():
    """Create Integers topic and associate with Year 4"""
    integers_topic = Topic.objects.filter(name="Integers").first()
    if not integers_topic:
        integers_topic = Topic.objects.create(name="Integers")
        print(f"[OK] Created topic: Integers")
    else:
        print(f"[INFO] Topic already exists: Integers")

    level_4 = Level.objects.filter(level_number=4).first()
    if not level_4:
        print("[ERROR] Year 4 level not found!")
        return None

    print(f"[INFO] Found Year 4: {level_4}")

    # Check if Integers already associated
    if level_4.topics.filter(name="Integers").exists():
        print("[INFO] Year 4 already has Integers topic associated.")
        print(f"   Current topics for Year 4: {', '.join([t.name for t in level_4.topics.all()])}")
    else:
        level_4.topics.add(integers_topic)
        print(f"[OK] Successfully associated Integers topic with Year 4")
        print(f"   Year 4 now has topics: {', '.join([t.name for t in level_4.topics.all()])}")

    return integers_topic, level_4


def add_integers_questions(integers_topic, level_4):
    """Add/Update Integers questions for Year 4"""
    questions_data = [
        {
            "question_text": "3 × 28 = ?",
            "correct_answer": "84",
            "wrong_answers": ["85", "83", "74"],
            "explanation": "3 × 28 = 84. Multiply 3 by 20 (60) and 3 by 8 (24), then add: 60 + 24 = 84."
        },
        {
            "question_text": "6 × 7 = ?",
            "correct_answer": "42",
            "wrong_answers": ["36", "48", "52"],
            "explanation": "6 times 7 equals 42."
        },
        {
            "question_text": "28 ÷ 4 = ?",
            "correct_answer": "7",
            "wrong_answers": ["6", "14", "4"],
            "explanation": "28 divided by 4 equals 7."
        },
        {
            "question_text": "What is the product of 12 and 3?",
            "correct_answer": "36",
            "wrong_answers": ["32", "39", "42"],
            "explanation": "12 × 3 = 36."
        },
        {
            "question_text": "45 − 19 = ?",
            "correct_answer": "26",
            "wrong_answers": ["24", "25", "27"],
            "explanation": "45 minus 19 equals 26."
        },
    ]

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for q_data in questions_data:
        question_text = q_data["question_text"]
        existing = Question.objects.filter(
            level=level_4,
            topic=integers_topic,
            question_text=question_text
        ).first()

        if existing:
            existing.explanation = q_data["explanation"]
            existing.save()
            Answer.objects.filter(question=existing).delete()

            Answer.objects.create(
                question=existing,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )

            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=existing,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )

            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [UPDATE] Updated: {safe_text}...")
            updated_count += 1
        else:
            question = Question.objects.create(
                level=level_4,
                topic=integers_topic,
                question_text=question_text,
                question_type="Multiple Choice",
                difficulty=1,
                points=1,
                explanation=q_data["explanation"]
            )

            Answer.objects.create(
                question=question,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )

            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=question,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )

            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [OK] Created: {safe_text}...")
            created_count += 1

            print(f"\n[SUMMARY]")
            print(f"   [OK] Created: {created_count} questions")
            print(f"   [UPDATE] Updated: {updated_count} questions")
            print(f"   [SKIP] Skipped: {skipped_count} questions")
            print(f"\n[OK] All Integers questions are associated with Year 4")


if __name__ == "__main__":
    print("[INFO] Setting up Integers topic for Year 4...\n")
    result = setup_integers_topic()
    if result:
        integers_topic, level_4 = result
        print("\n" + "="*60)
        add_integers_questions(integers_topic, level_4)
        print("\n[OK] Done!")
