#!/usr/bin/env python
"""
Add/Update "Integers" questions for Year 8
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
    """Create Integers topic and associate with Year 8"""
    
    # Get or create the "Integers" topic
    # Handle case where multiple topics with same name exist
    integers_topic = Topic.objects.filter(name="Integers").first()
    if not integers_topic:
        integers_topic = Topic.objects.create(name="Integers")
        print(f"[OK] Created topic: Integers")
    else:
        print(f"[INFO] Topic already exists: Integers")
    
    # Get Year 8 level
    level_8 = Level.objects.filter(level_number=8).first()
    
    if not level_8:
        print("[ERROR] Year 8 level not found!")
        return None
    
    print(f"[INFO] Found Year 8: {level_8}")
    
    # Check if Integers is already associated
    if level_8.topics.filter(name="Integers").exists():
        print("[INFO] Year 8 already has Integers topic associated.")
        print(f"   Current topics for Year 8: {', '.join([t.name for t in level_8.topics.all()])}")
    else:
        # Associate Integers topic with Year 8
        level_8.topics.add(integers_topic)
        print(f"[OK] Successfully associated Integers topic with Year 8")
        print(f"   Year 8 now has topics: {', '.join([t.name for t in level_8.topics.all()])}")
    
    return integers_topic, level_8

def add_integers_questions(integers_topic, level_8):
    """Add/Update Integers questions for Year 8"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    # 
    # Format for each question:
    # {
    #     "question_text": "Your question here",
    #     "correct_answer": "The correct answer",
    #     "wrong_answers": ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
    #     "explanation": "Explanation of the correct answer"
    # }
    
    questions_data = [
        {
            "question_text": "The temperature was -12°C. It increased by 7°C. What is the new temperature?",
            "correct_answer": "-5",
            "wrong_answers": ["-19", "5", "12"],
            "explanation": "-12 + 7 = -5. The new temperature is -5°C."
        },
        {
            "question_text": "A submarine is 30 meters below sea level. It rises 18 meters. What is its new position?",
            "correct_answer": "-12",
            "wrong_answers": ["12", "-48", "18"],
            "explanation": "-30 + 18 = -12. The submarine is now 12 meters below sea level."
        },
        {
            "question_text": "James had $15. He spent $23. What is his balance?",
            "correct_answer": "-8",
            "wrong_answers": ["8", "-38", "23"],
            "explanation": "15 − 23 = -8. James is $8 in debt."
        },
        {
            "question_text": "A lift goes down 6 floors from level 2. What floor does it reach?",
            "correct_answer": "-4",
            "wrong_answers": ["4", "-8", "6"],
            "explanation": "2 − 6 = -4. The lift reaches floor -4."
        },
        {
            "question_text": "Calculate: -4 × 6",
            "correct_answer": "-24",
            "wrong_answers": ["24", "-10", "10"],
            "explanation": "A negative number multiplied by a positive number gives a negative result. -4 × 6 = -24."
        },
        {
            "question_text": "Calculate: -8 ÷ 4",
            "correct_answer": "-2",
            "wrong_answers": ["2", "-12", "32"],
            "explanation": "-8 ÷ 4 = -2."
        },
        {
            "question_text": "A square has a side length of 7 cm. What is its area?",
            "correct_answer": "49",
            "wrong_answers": ["14", "21", "28"],
            "explanation": "Area of a square = side × side. 7 × 7 = 49 cm²."
        },
        {
            "question_text": "What is the square of 9?",
            "correct_answer": "81",
            "wrong_answers": ["18", "27", "72"],
            "explanation": "9² means 9 × 9, which equals 81."
        },
        {
            "question_text": "What is the value of (-5)²?",
            "correct_answer": "25",
            "wrong_answers": ["-25", "10", "-10"],
            "explanation": "(-5)² means -5 × -5, which equals 25."
        },
        {
            "question_text": "Find the square root of 64.",
            "correct_answer": "8",
            "wrong_answers": ["16", "6", "-8"],
            "explanation": "8 × 8 = 64, so the square root of 64 is 8."
        },
        {
            "question_text": "Calculate: 3² + 4²",
            "correct_answer": "25",
            "wrong_answers": ["49", "14", "7"],
            "explanation": "3² = 9 and 4² = 16. 9 + 16 = 25."
        },
        {
            "question_text": "Calculate: 10 − (−6)",
            "correct_answer": "16",
            "wrong_answers": ["4", "-16", "-4"],
            "explanation": "Subtracting a negative is the same as adding. 10 + 6 = 16."
        },
        {
            "question_text": "The temperature was -8°C overnight. During the day, it dropped by another 6°C. What is the new temperature?",
            "correct_answer": "-14",
            "wrong_answers": ["-2", "14", "-48"],
            "explanation": "-8 − 6 = -14. The new temperature is -14°C."
        },
        {
            "question_text": "A hiker is 5 meters above sea level and then walks down 12 meters. What is the hiker's new position?",
            "correct_answer": "-7",
            "wrong_answers": ["7", "-17", "12"],
            "explanation": "5 − 12 = -7. The hiker is 7 meters below sea level."
        },
        {
            "question_text": "Sarah had $20 in her account. She spent $35. What is her balance now?",
            "correct_answer": "-15",
            "wrong_answers": ["15", "-55", "35"],
            "explanation": "20 − 35 = -15. Sarah is $15 in debt."
        },
        {
            "question_text": "A lift starts at floor -3 and goes up 9 floors. What floor does it stop at?",
            "correct_answer": "6",
            "wrong_answers": ["-12", "12", "3"],
            "explanation": "-3 + 9 = 6. The lift stops at floor 6."
        },
        {
            "question_text": "A square garden has sides that are 10 meters long. What is the area of the garden?",
            "correct_answer": "100",
            "wrong_answers": ["40", "20", "50"],
            "explanation": "Area of a square = side × side. 10 × 10 = 100 m²."
        },
        {
            "question_text": "Each side of a square tile is 6 cm long. What is the area of one tile?",
            "correct_answer": "36",
            "wrong_answers": ["12", "24", "18"],
            "explanation": "6² = 6 × 6 = 36 cm²."
        },
        {
            "question_text": "A number is squared to give 49. What is the original positive number?",
            "correct_answer": "7",
            "wrong_answers": ["-7", "14", "21"],
            "explanation": "7 × 7 = 49, so the number is 7."
        },
        {
            "question_text": "The area of a square playground is 81 square meters. What is the length of one side?",
            "correct_answer": "9",
            "wrong_answers": ["18", "27", "8"],
            "explanation": "The square root of 81 is 9."
        },
        {
            "question_text": "A robot moves backward 4 steps each turn. After 6 turns, how far has it moved?",
            "correct_answer": "-24",
            "wrong_answers": ["24", "-10", "6"],
            "explanation": "-4 × 6 = -24. The robot moved 24 steps backward."
        },
        {
            "question_text": "A debt of $32 is shared equally among 4 people. How much debt does each person have?",
            "correct_answer": "-8",
            "wrong_answers": ["8", "-128", "4"],
            "explanation": "-32 ÷ 4 = -8. Each person owes $8."
        },
        {
            "question_text": "A square picture frame has a side length of 12 cm. What is the perimeter of the frame?",
            "correct_answer": "48",
            "wrong_answers": ["24", "144", "36"],
            "explanation": "Perimeter = 4 × side. 4 × 12 = 48 cm."
        },
        {
            "question_text": "The length of a square room is doubled. If the original side was 5 m, what is the area of the new room?",
            "correct_answer": "100",
            "wrong_answers": ["50", "25", "75"],
            "explanation": "New side = 10 m. Area = 10 × 10 = 100 m²."
        }
    ]
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for q_data in questions_data:
        question_text = q_data["question_text"]
        
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_8,
            topic=integers_topic,
            question_text=question_text
        ).first()
        
        if existing:
            # Question already exists, update if needed
            existing.explanation = q_data["explanation"]
            existing.save()
            
            # Delete old answers and recreate
            Answer.objects.filter(question=existing).delete()
            
            # Create correct answer
            Answer.objects.create(
                question=existing,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
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
            # Create new question
            question = Question.objects.create(
                level=level_8,
                topic=integers_topic,
                question_text=question_text,
                question_type="Multiple Choice",
                difficulty=3,
                points=1,
                explanation=q_data["explanation"]
            )
            
            # Create correct answer
            Answer.objects.create(
                question=question,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
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
    print(f"\n[OK] All Integers questions are associated with Year 8")

if __name__ == "__main__":
    print("[INFO] Setting up Integers topic for Year 8...\n")
    result = setup_integers_topic()
    
    if result:
        integers_topic, level_8 = result
        print("\n" + "="*60)
        add_integers_questions(integers_topic, level_8)
        print("\n[OK] Done!")
