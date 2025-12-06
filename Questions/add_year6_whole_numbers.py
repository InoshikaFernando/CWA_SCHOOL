#!/usr/bin/env python
"""
Add/Update "Whole Numbers" questions for Year 6
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

def setup_whole_numbers_topic():
    """Create Whole Numbers topic and associate with Year 6"""
    
    # Get or create the "Whole Numbers" topic
    # Handle case where multiple topics with same name exist
    whole_numbers_topic = Topic.objects.filter(name="Whole Numbers").first()
    if not whole_numbers_topic:
        whole_numbers_topic = Topic.objects.create(name="Whole Numbers")
        print(f"[OK] Created topic: Whole Numbers")
    else:
        print(f"[INFO] Topic already exists: Whole Numbers")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return None
    
    print(f"[INFO] Found Year 6: {level_6}")
    
    # Check if Whole Numbers is already associated
    if level_6.topics.filter(name="Whole Numbers").exists():
        print("[INFO] Year 6 already has Whole Numbers topic associated.")
        print(f"   Current topics for Year 6: {', '.join([t.name for t in level_6.topics.all()])}")
    else:
        # Associate Whole Numbers topic with Year 6
        level_6.topics.add(whole_numbers_topic)
        print(f"[OK] Successfully associated Whole Numbers topic with Year 6")
        print(f"   Year 6 now has topics: {', '.join([t.name for t in level_6.topics.all()])}")
    
    return whole_numbers_topic, level_6

def add_whole_numbers_questions(whole_numbers_topic, level_6):
    """Add/Update Whole Numbers questions for Year 6"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "How many months are in 37 years?",
            "correct_answer": "444",
            "wrong_answers": ["370", "340", "412"],
            "explanation": "1 year = 12 months. So 37 × 12 = 444 months."
        },
        {
            "question_text": "The product of a number multiplied by itself is 400. What is the number?",
            "correct_answer": "20",
            "wrong_answers": ["40", "25", "15"],
            "explanation": "If a × a = 400, then a = √400 = 20."
        },
        {
            "question_text": "From the product of 30 and 60, subtract 280.",
            "correct_answer": "1520",
            "wrong_answers": ["1480", "1600", "1200"],
            "explanation": "30 × 60 = 1800. Then 1800 − 280 = 1520."
        },
        {
            "question_text": "Hari’s marks are 70, 85, 63, 92 and 89. What is his total mark?",
            "correct_answer": "399",
            "wrong_answers": ["379", "409", "420"],
            "explanation": "Add the marks: 70 + 85 + 63 + 92 + 89 = 399."
        },
        {
            "question_text": "Find the total number of days in the months of May, June and July.",
            "correct_answer": "92",
            "wrong_answers": ["91", "90", "93"],
            "explanation": "May: 31 days, June: 30 days, July: 31 days. Total = 31 + 30 + 31 = 92."
        },
        {
            "question_text": "Subtract the sum of 235 and 180 from 768.",
            "correct_answer": "353",
            "wrong_answers": ["403", "333", "368"],
            "explanation": "235 + 180 = 415. Then 768 − 415 = 353."
        },
        {
            "question_text": "How many minutes are in 15 hours?",
            "correct_answer": "900",
            "wrong_answers": ["600", "850", "1500"],
            "explanation": "1 hour = 60 minutes. So 15 × 60 = 900."
        },
        {
            "question_text": "Find the sum of 36 metres, 53 metres and 21 metres.",
            "correct_answer": "110",
            "wrong_answers": ["120", "100", "90"],
            "explanation": "36 + 53 + 21 = 110 metres."
        },
        {
            "question_text": "Add 68 kg, 125 kg and 32 kg.",
            "correct_answer": "225",
            "wrong_answers": ["215", "235", "205"],
            "explanation": "68 + 125 + 32 = 225 kg."
        },
        {
            "question_text": "How many apples are there altogether in three boxes of 45, 56 and 52?",
            "correct_answer": "153",
            "wrong_answers": ["145", "165", "148"],
            "explanation": "45 + 56 + 52 = 153 apples."
        },
        {
            "question_text": "Find the product of 32 and 16.",
            "correct_answer": "512",
            "wrong_answers": ["428", "480", "540"],
            "explanation": "32 × 16 = 512."
        },
        {
            "question_text": "Find the price of 75 oranges at 15 cents each.",
            "correct_answer": "1125 cents",
            "wrong_answers": ["1075 cents", "1150 cents", "1200 cents"],
            "explanation": "75 × 15 = 1125 cents."
        },
        {
            "question_text": "How many books are in 120 cases if each contains 36 books?",
            "correct_answer": "4320",
            "wrong_answers": ["3620", "4000", "4520"],
            "explanation": "120 × 36 = 4320 books."
        }
    ]
    
    if not questions_data:
        print("[WARNING] No questions defined in questions_data list!")
        print("Please add questions to the questions_data list in the script.")
        return
    
    # Use shared utility function to process questions
    results = process_questions(
        level=level_6,
        topic=whole_numbers_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n[OK] All questions are associated with Whole Numbers topic for Year 6")

if __name__ == "__main__":
    print("=" * 80)
    print("Adding/Updating Whole Numbers questions for Year 6")
    print("=" * 80)
    
    result = setup_whole_numbers_topic()
    if result:
        whole_numbers_topic, level_6 = result
        add_whole_numbers_questions(whole_numbers_topic, level_6)
        print("[SUCCESS] Script completed!")
    else:
        print("[ERROR] Failed to set up topic. Please check the errors above.")

