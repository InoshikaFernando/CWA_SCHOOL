#!/usr/bin/env python
"""
Add/Update "Factors" questions for Year 7
This script can be run multiple times - it will:
- Add new questions if they don't exist
- Update answers if they've changed
- Skip questions that are already up-to-date
"""

import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()


from maths.models import Level, Topic
from question_utils import process_questions

def setup_factors_topic():
    """Create Factors topic and associate with Year 8"""

    # Get or create the "Factors" topic
    factors_topic = Topic.objects.filter(name="Factors").first()
    if not factors_topic:
        factors_topic = Topic.objects.create(name="Factors")
        print("[OK] Created topic: Factors")
    else:
        print("[INFO] Topic already exists: Factors")

    # Get Year 8 level
    level_8 = Level.objects.filter(level_number=8).first()

    if not level_8:
        print("[ERROR] Year 8 level not found!")
        return None

    print(f"[INFO] Found Year 8: {level_8}")

    # Associate topic if not already linked
    if level_8.topics.filter(name="Factors").exists():
        print("[INFO] Year 8 already has Factors topic associated.")
    else:
        level_8.topics.add(factors_topic)
        print("[OK] Successfully associated Factors topic with Year 8")

    return factors_topic, level_8

def add_factors_questions(factors_topic, level_8):
    """Add/Update Factors questions for Year 8"""
    questions_data = [

        {
            "question_text": "Factorise: x² + 5x + 6",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 2)(x + 3)",
            "wrong_answers": ["(x + 1)(x + 6)", "(x + 2)(x + 4)", "(x + 3)(x + 3)"],
            "explanation": "Two numbers that multiply to 6 and add to 5 are 2 and 3."
        },

        {
            "question_text": "Factorise: x² + 7x + 10",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 5)(x + 2)",
            "wrong_answers": ["(x + 1)(x + 10)", "(x + 3)(x + 4)", "(x + 7)(x + 3)"],
            "explanation": "Two numbers that multiply to 10 and add to 7 are 5 and 2."
        },

        {
            "question_text": "Factorise: x² + 9x + 20",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 4)(x + 5)",
            "wrong_answers": ["(x + 2)(x + 10)", "(x + 1)(x + 20)", "(x + 3)(x + 7)"],
            "explanation": "4 and 5 multiply to 20 and add to 9."
        },

        {
            "question_text": "Factorise: x² + 11x + 24",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 3)(x + 8)",
            "wrong_answers": ["(x + 4)(x + 6)", "(x + 2)(x + 12)", "(x + 1)(x + 24)"],
            "explanation": "3 and 8 multiply to 24 and add to 11."
        },

        {
            "question_text": "Factorise: x² - 5x + 6",
            "question_type": "multiple_choice",
            "correct_answer": "(x - 2)(x - 3)",
            "wrong_answers": ["(x - 1)(x - 6)", "(x - 2)(x - 4)", "(x - 3)(x - 3)"],
            "explanation": "Two numbers that multiply to 6 and add to -5 are -2 and -3."
        },

        {
            "question_text": "Factorise: x² - 7x + 12",
            "question_type": "multiple_choice",
            "correct_answer": "(x - 3)(x - 4)",
            "wrong_answers": ["(x - 2)(x - 6)", "(x - 1)(x - 12)", "(x - 5)(x - 2)"],
            "explanation": "Two numbers that multiply to 12 and add to -7 are -3 and -4."
        },

        {
            "question_text": "Factorise: x² + x - 6",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 3)(x - 2)",
            "wrong_answers": ["(x + 2)(x - 3)", "(x + 1)(x - 6)", "(x + 6)(x - 1)"],
            "explanation": "3 and -2 multiply to -6 and add to 1."
        },

        {
            "question_text": "Factorise: x² - 2x - 15",
            "question_type": "multiple_choice",
            "correct_answer": "(x - 5)(x + 3)",
            "wrong_answers": ["(x - 3)(x + 5)", "(x - 1)(x - 15)", "(x - 15)(x + 1)"],
            "explanation": "-5 and 3 multiply to -15 and add to -2."
        },

        {
            "question_text": "Factorise: x² + 6x - 16",
            "question_type": "multiple_choice",
            "correct_answer": "(x + 8)(x - 2)",
            "wrong_answers": ["(x + 4)(x - 4)", "(x + 2)(x - 8)", "(x + 16)(x - 1)"],
            "explanation": "8 and -2 multiply to -16 and add to 6."
        },

        {
            "question_text": "Factorise: x² - x - 12",
            "question_type": "multiple_choice",
            "correct_answer": "(x - 4)(x + 3)",
            "wrong_answers": ["(x - 3)(x + 4)", "(x - 6)(x + 2)", "(x - 12)(x + 1)"],
            "explanation": "-4 and 3 multiply to -12 and add to -1."
        }
    ]

    process_questions(
        level=level_8,
        topic=factors_topic,
        questions_data=questions_data,
        verbose=True
    )


if __name__ == "__main__":
    print("[INFO] Setting up Factors topic for Year 8...\n")
    result = setup_factors_topic()
    
    if result:
        factors_topic, level_8 = result
        print("\n" + "="*60)
        add_factors_questions(factors_topic, level_8)
        print("\n[OK] Done!")
