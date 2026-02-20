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
            "question_text": "What is the HCF of 48 and 72?",
            "question_type": "multiple_choice",
            "correct_answer": "24",
            "wrong_answers": ["12", "6", "36"],
            "explanation": "Common factors of 48 and 72 include 1, 2, 3, 4, 6, 8, 12, 24. The highest is 24."
        },
        {
            "question_text": "Factorise: 4x + 8",
            "question_type": "multiple_choice",
            "correct_answer": "4(x + 2)",
            "wrong_answers": ["8(x + 4)", "4x(8)", "2(x + 4)"],
            "explanation": "The common factor of 4x and 8 is 4."
        },
        {
            "question_text": "Factorise: 5x + 10",
            "question_type": "multiple_choice",
            "correct_answer": "5(x + 2)",
            "wrong_answers": ["10(x + 5)", "5x(10)", "5x + 2"],
            "explanation": "Both terms share a common factor of 5."
        },
        {
            "question_text": "Factorise: 3x + 6",
            "question_type": "multiple_choice",
            "correct_answer": "3(x + 2)",
            "wrong_answers": ["6(x + 3)", "3x(6)", "x(3 + 6)"],
            "explanation": "The highest common factor of 3x and 6 is 3."
        },
        {
            "question_text": "Factorise: 2x + 8",
            "question_type": "multiple_choice",
            "correct_answer": "2(x + 4)",
            "wrong_answers": ["8(x + 2)", "2x(8)", "x(2 + 8)"],
            "explanation": "The highest common factor of 2x and 8 is 2."
        },
        {
            "question_text": "Factorise: 4x + 12",
            "question_type": "multiple_choice",
            "correct_answer": "4(x + 3)",
            "wrong_answers": ["12(x + 4)", "2(x + 6)", "4x(12)"],
            "explanation": "The highest common factor of 4x and 12 is 4."
        },
        {
            "question_text": "Factorise: 5x + 20",
            "question_type": "multiple_choice",
            "correct_answer": "5(x + 4)",
            "wrong_answers": ["20(x + 5)", "4(x + 5)", "5x(20)"],
            "explanation": "The highest common factor of 5x and 20 is 5."
        },
        {
            "question_text": "Factorise: 6x + 18",
            "question_type": "multiple_choice",
            "correct_answer": "6(x + 3)",
            "wrong_answers": ["3(2x + 6)", "18(x + 6)", "6x(18)"],
            "explanation": "The highest common factor of 6x and 18 is 6."
        },
        {
            "question_text": "Factorise: 7x + 14",
            "question_type": "multiple_choice",
            "correct_answer": "7(x + 2)",
            "wrong_answers": ["14(x + 7)", "2(x + 7)", "7x(14)"],
            "explanation": "The highest common factor of 7x and 14 is 7."
        },
        {
            "question_text": "Factorise: 8x + 24",
            "question_type": "multiple_choice",
            "correct_answer": "8(x + 3)",
            "wrong_answers": ["4(2x + 6)", "24(x + 8)", "8x(24)"],
            "explanation": "The highest common factor of 8x and 24 is 8."
        },
        {
            "question_text": "Factorise: 9x + 27",
            "question_type": "multiple_choice",
            "correct_answer": "9(x + 3)",
            "wrong_answers": ["3(3x + 9)", "27(x + 9)", "9x(27)"],
            "explanation": "The highest common factor of 9x and 27 is 9."
        },
        {
            "question_text": "Factorise: 10x + 30",
            "question_type": "multiple_choice",
            "correct_answer": "10(x + 3)",
            "wrong_answers": ["5(2x + 6)", "30(x + 10)", "10x(30)"],
            "explanation": "The highest common factor of 10x and 30 is 10."
        },
        {
            "question_text": "Factorise: 12x + 16",
            "question_type": "multiple_choice",
            "correct_answer": "4(3x + 4)",
            "wrong_answers": ["12(x + 16)", "2(6x + 8)", "8(x + 2)"],
            "explanation": "The highest common factor of 12x and 16 is 4."
        },
        {
            "question_text": "Factorise: 15x + 25",
            "question_type": "multiple_choice",
            "correct_answer": "5(3x + 5)",
            "wrong_answers": ["15(x + 25)", "25(x + 15)", "5(x + 5)"],
            "explanation": "The highest common factor of 15x and 25 is 5."
        },
        {
            "question_text": "Factorise: 12x + 18",
            "question_type": "multiple_choice",
            "correct_answer": "6(2x + 3)",
            "wrong_answers": ["3(4x + 6)", "12(x + 18)", "2(6x + 9)"],
            "explanation": "The highest common factor of 12x and 18 is 6."
        },
        {
            "question_text": "Factorise: 16x + 24",
            "question_type": "multiple_choice",
            "correct_answer": "8(2x + 3)",
            "wrong_answers": ["4(4x + 6)", "16(x + 24)", "2(8x + 12)"],
            "explanation": "The highest common factor of 16x and 24 is 8."
        },
        {
            "question_text": "Factorise: 6x - 9",
            "question_type": "multiple_choice",
            "correct_answer": "3(2x - 3)",
            "wrong_answers": ["3(2x + 3)", "6(x - 9)", "9(6x - 1)"],
            "explanation": "Both terms share a common factor of 3."
        },
        {
            "question_text": "Factorise: 15x - 20",
            "question_type": "multiple_choice",
            "correct_answer": "5(3x - 4)",
            "wrong_answers": ["5(3x + 4)", "15(x - 20)", "10(3x - 2)"],
            "explanation": "The highest common factor of 15x and 20 is 5."
        },
        {
            "question_text": "Factorise: 9x + 12",
            "question_type": "multiple_choice",
            "correct_answer": "3(3x + 4)",
            "wrong_answers": ["9(x + 12)", "6(3x + 2)", "3(3x + 2)"],
            "explanation": "The highest common factor of 9x and 12 is 3."
        },
        {
            "question_text": "Factorise: 8xy + 12x",
            "question_type": "multiple_choice",
            "correct_answer": "4x(2y + 3)",
            "wrong_answers": ["4(2xy + 3x)", "2x(4y + 6)", "8x(y + 12)"],
            "explanation": "Common factors are 4 and x."
        },
        {
            "question_text": "Factorise: 10ab + 15a",
            "question_type": "multiple_choice",
            "correct_answer": "5a(2b + 3)",
            "wrong_answers": ["5(2ab + 3a)", "10a(b + 15)", "15a(10b + 1)"],
            "explanation": "Common factors are 5 and a."
        },
        {
            "question_text": "Factorise: 14x + 21y",
            "question_type": "multiple_choice",
            "correct_answer": "7(2x + 3y)",
            "wrong_answers": ["7(2x + 3)", "14(x + 21y)", "3(7x + 7y)"],
            "explanation": "The highest common factor of 14 and 21 is 7."
        },
        {
            "question_text": "Factorise: 18x - 24y",
            "question_type": "multiple_choice",
            "correct_answer": "6(3x - 4y)",
            "wrong_answers": ["3(6x - 8y)", "6(3x + 4y)", "12(3x - 2y)"],
            "explanation": "The highest common factor of 18 and 24 is 6."
        },
        {
            "question_text": "Factorise: 21xy + 28x",
            "question_type": "multiple_choice",
            "correct_answer": "7x(3y + 4)",
            "wrong_answers": ["7(3xy + 4x)", "21x(y + 28)", "4x(7y + 3)"],
            "explanation": "Common factors are 7 and x."
        },
    ]

    process_questions(
        level=level_7,
        topic=factors_topic,
        questions_data=questions_data,
        verbose=True
    )


if __name__ == "__main__":
    print("[INFO] Setting up Factors topic for Year 7...\n")
    result = setup_factors_topic()
    
    if result:
        factors_topic, level_7 = result
        print("\n" + "="*60)
        add_factors_questions(factors_topic, level_7)
        print("\n[OK] Done!")
    # import argparse

    # parser = argparse.ArgumentParser(description='Add/Update Year 7 Factors questions')
    # parser.add_argument('--execute', action='store_true', help='Actually perform the operations')
    # args = parser.parse_args()

    # if not args.execute:
    #     print("[DRY RUN] Use --execute to actually add/update questions")
    #     print()

    # result = setup_factors_topic()
    # if result:
    #     topic, level = result
    #     if args.execute:
    #         add_factors_questions(topic, level)
    #     else:
    #         print("[DRY RUN] Would add/update questions here")
    # else:
    #     print("[ERROR] Failed to setup topic")
