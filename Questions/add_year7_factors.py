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
    """Create Factors topic and associate with Year 7"""

    # Get or create the "Factors" topic
    factors_topic = Topic.objects.filter(name="Factors").first()
    if not factors_topic:
        factors_topic = Topic.objects.create(name="Factors")
        print(f"[OK] Created topic: Factors")
    else:
        print(f"[INFO] Topic already exists: Factors")

    # Get Year 7 level
    level_7 = Level.objects.filter(level_number=7).first()

    if not level_7:
        print("[ERROR] Year 7 level not found!")
        return None

    print(f"[INFO] Found Year 7: {level_7}")

    # Associate topic if not already linked
    if level_7.topics.filter(name="Factors").exists():
        print("[INFO] Year 7 already has Factors topic associated.")
    else:
        level_7.topics.add(factors_topic)
        print("[OK] Successfully associated Factors topic with Year 7")

    return factors_topic, level_7


def add_factors_questions(factors_topic, level_7):
    """Add/Update Factors questions for Year 7"""

    questions_data = [

        # Prime Factorisation
        {
            "question_text": "What is the prime factorisation of 84?",
            "question_type": "multiple_choice",
            "correct_answer": "2 × 2 × 3 × 7",
            "wrong_answers": ["2 × 3 × 14", "4 × 21", "2 × 6 × 7"],
            "explanation": "84 = 2 × 2 × 3 × 7."
        },

        {
            "question_text": "What is the prime factorisation of 90?",
            "question_type": "multiple_choice",
            "correct_answer": "2 × 3 × 3 × 5",
            "wrong_answers": ["3 × 30", "2 × 9 × 5", "6 × 15"],
            "explanation": "90 = 2 × 3 × 3 × 5."
        },

        # LCM (larger numbers)
        {
            "question_text": "What is the LCM of 12 and 15?",
            "question_type": "multiple_choice",
            "correct_answer": "60",
            "wrong_answers": ["30", "45", "120"],
            "explanation": "Multiples of 12 and 15 meet at 60."
        },

        {
            "question_text": "What is the LCM of 18 and 24?",
            "question_type": "multiple_choice",
            "correct_answer": "72",
            "wrong_answers": ["36", "48", "96"],
            "explanation": "Prime factor method gives LCM = 72."
        },

        {
            "question_text": "What is the LCM of 6, 8 and 12?",
            "question_type": "multiple_choice",
            "correct_answer": "24",
            "wrong_answers": ["12", "48", "36"],
            "explanation": "LCM of 6, 8 and 12 is 24."
        },

        # HCF (larger numbers)
        {
            "question_text": "What is the HCF of 24 and 36?",
            "question_type": "multiple_choice",
            "correct_answer": "12",
            "wrong_answers": ["6", "18", "24"],
            "explanation": "Common factors: 1, 2, 3, 4, 6, 12. Highest is 12."
        },

        {
            "question_text": "What is the HCF of 45 and 75?",
            "question_type": "multiple_choice",
            "correct_answer": "15",
            "wrong_answers": ["5", "25", "30"],
            "explanation": "Prime factors give HCF = 15."
        },

        {
            "question_text": "What is the HCF of 36, 54 and 90?",
            "question_type": "multiple_choice",
            "correct_answer": "18",
            "wrong_answers": ["9", "6", "12"],
            "explanation": "Common prime factors give HCF = 18."
        },

        # Word Problems
        {
            "question_text": "Three bells ring every 8, 12 and 20 minutes. After how many minutes will they ring together?",
            "question_type": "multiple_choice",
            "correct_answer": "120 minutes",
            "wrong_answers": ["60 minutes", "240 minutes", "40 minutes"],
            "explanation": "LCM of 8, 12 and 20 is 120."
        },

        {
            "question_text": "48 apples and 72 oranges are packed into identical boxes. What is the greatest number of boxes that can be made?",
            "question_type": "multiple_choice",
            "correct_answer": "24",
            "wrong_answers": ["12", "6", "48"],
            "explanation": "HCF of 48 and 72 is 24."
        }

    ]

    process_questions(
        level=level_7,
        topic=factors_topic,
        questions_data=questions_data,
        verbose=True
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Add/Update Year 7 Factors questions')
    parser.add_argument('--execute', action='store_true', help='Actually perform the operations')
    args = parser.parse_args()

    if not args.execute:
        print("[DRY RUN] Use --execute to actually add/update questions")
        print()

    result = setup_factors_topic()
    if result:
        topic, level = result
        if args.execute:
            add_factors_questions(topic, level)
        else:
            print("[DRY RUN] Would add/update questions here")
    else:
        print("[ERROR] Failed to setup topic")
