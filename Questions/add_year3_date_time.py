#!/usr/bin/env python
"""
Add/Update "Date and Time" questions for Year 3
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

def setup_date_time_topic():
    """Create Date and Time topic and associate with Year 3"""
    
    # Get or create the "Date and Time" topic
    # Handle case where multiple topics with same name exist
    date_time_topic = Topic.objects.filter(name="Date and Time").first()
    if not date_time_topic:
        date_time_topic = Topic.objects.create(name="Date and Time")
        print(f"[OK] Created topic: Date and Time")
    else:
        print(f"[INFO] Topic already exists: Date and Time")
    
    # Get Year 3 level
    level_3 = Level.objects.filter(level_number=3).first()
    
    if not level_3:
        print("[ERROR] Year 3 level not found!")
        return None
    
    print(f"[INFO] Found Year 3: {level_3}")
    
    # Check if Date and Time is already associated
    if level_3.topics.filter(name="Date and Time").exists():
        print("[INFO] Year 3 already has Date and Time topic associated.")
        print(f"   Current topics for Year 3: {', '.join([t.name for t in level_3.topics.all()])}")
    else:
        # Associate Date and Time topic with Year 3
        level_3.topics.add(date_time_topic)
        print(f"[OK] Successfully associated Date and Time topic with Year 3")
        print(f"   Year 3 now has topics: {', '.join([t.name for t in level_3.topics.all()])}")
    
    return date_time_topic, level_3

def add_date_time_questions(date_time_topic, level_3):
    """Add/Update Date and Time questions for Year 3"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Winter break will start 4 days before Christmas Eve (December 24). What is the date of the first day of the winter break?",
            "question_type": "multiple_choice",
            "correct_answer": "December 20",
            "wrong_answers": ["December 18", "December 21", "December 22"],
            "explanation": "Christmas Eve is December 24. Four days before that is December 20.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "What day of the week is Christmas (December 25)?",
            "question_type": "multiple_choice",
            "correct_answer": "Thursday",
            "wrong_answers": ["Wednesday", "Friday", "Saturday"],
            "explanation": "According to the calendar, December 25 falls on a Thursday.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "Liz is hosting a party on the Saturday between Christmas Day and New Year’s Eve. What is the date for the party?",
            "question_type": "multiple_choice",
            "correct_answer": "December 27",
            "wrong_answers": ["December 26", "December 28", "December 29"],
            "explanation": "The Saturday between December 25 and December 31 is December 27.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "Liz sent the invitation for the party 5 days before Christmas. What day is it?",
            "question_type": "multiple_choice",
            "correct_answer": "December 20",
            "wrong_answers": ["December 18", "December 19", "December 21"],
            "explanation": "5 days before December 25 is December 20.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "What day of the week is December 21st?",
            "question_type": "multiple_choice",
            "correct_answer": "Sunday",
            "wrong_answers": ["Saturday", "Monday", "Tuesday"],
            "explanation": "December 21 is shown as a Sunday on the calendar.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "What is the date of the third Saturday of December?",
            "question_type": "multiple_choice",
            "correct_answer": "December 20",
            "wrong_answers": ["December 13", "December 27", "December 19"],
            "explanation": "Saturdays are 6, 13, 20, 27. The third Saturday is December 20.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "What is the date of the second Thursday of December?",
            "question_type": "multiple_choice",
            "correct_answer": "December 11",
            "wrong_answers": ["December 4", "December 18", "December 12"],
            "explanation": "Thursdays are 4, 11, 18, 25. The second Thursday is December 11.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "How many Sundays are there in December?",
            "question_type": "multiple_choice",
            "correct_answer": "5",
            "wrong_answers": ["4", "3", "6"],
            "explanation": "Sundays fall on 30, 7, 14, 21, 28 — a total of 5 Sundays.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "How many Wednesdays are there in December?",
            "question_type": "multiple_choice",
            "correct_answer": "5",
            "wrong_answers": ["4", "3", "6"],
            "explanation": "Wednesdays fall on 3, 10, 17, 24, 31 — 5 Wednesdays.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "How many days are there in December?",
            "question_type": "multiple_choice",
            "correct_answer": "31",
            "wrong_answers": ["30", "29", "28"],
            "explanation": "December always has 31 days.",
            "image_path": "questions/year3/dateTime/december.png"
        },
        {
            "question_text": "The bill is due on the first Friday of March. What is the due date of the bill?",
            "question_type": "multiple_choice",
            "correct_answer": "March 6",
            "wrong_answers": ["March 7", "March 5", "March 3"],
            "explanation": "In the calendar, the Fridays are 6, 13, 20, 27. The first Friday is March 6.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "Emma forgot to pay the bill on time. She paid the bill when it was three days overdue. When did she pay the bill?",
            "question_type": "multiple_choice",
            "correct_answer": "March 9",
            "wrong_answers": ["March 8", "March 10", "March 7"],
            "explanation": "Three days after March 6 is March 9.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "If Emma received a reminder notice for her bill two days before March 5th, on what day of the week did she receive the reminder notice?",
            "question_type": "multiple_choice",
            "correct_answer": "Monday",
            "wrong_answers": ["Sunday", "Tuesday", "Wednesday"],
            "explanation": "Two days before March 5 (Wednesday) is March 3, which is a Monday.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "What is the date of the first Tuesday of March?",
            "question_type": "multiple_choice",
            "correct_answer": "March 3",
            "wrong_answers": ["March 4", "March 2", "March 5"],
            "explanation": "The first Tuesday is March 3.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "What is the date of the last Monday of March?",
            "question_type": "multiple_choice",
            "correct_answer": "March 30",
            "wrong_answers": ["March 31", "March 23", "March 24"],
            "explanation": "Mondays are 2, 9, 16, 23, 30. The last Monday is March 30.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "Which day of the week is March 29th?",
            "question_type": "multiple_choice",
            "correct_answer": "Sunday",
            "wrong_answers": ["Saturday", "Monday", "Friday"],
            "explanation": "March 29 is shown in red under Sunday.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "Which day of the week is March 14th?",
            "question_type": "multiple_choice",
            "correct_answer": "Saturday",
            "wrong_answers": ["Friday", "Sunday", "Thursday"],
            "explanation": "March 14 falls under Saturday.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "How many Sundays are there in March?",
            "question_type": "multiple_choice",
            "correct_answer": "5",
            "wrong_answers": ["4", "3", "6"],
            "explanation": "Sundays are 1, 8, 15, 22, 29 — five Sundays.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "How many Wednesdays are there in March?",
            "question_type": "multiple_choice",
            "correct_answer": "4",
            "wrong_answers": ["5", "3", "6"],
            "explanation": "Wednesdays are 4, 11, 18, 25 — four Wednesdays.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "How many days are there in March?",
            "question_type": "multiple_choice",
            "correct_answer": "31",
            "wrong_answers": ["30", "29", "28"],
            "explanation": "The calendar ends on March 31.",
            "image_path": "questions/year3/dateTime/march.png"
        },
        {
            "question_text": "How many days are in the month of April?",
            "question_type": "multiple_choice",
            "correct_answer": "30",
            "wrong_answers": ["31", "28", "29"],
            "explanation": "April always has 30 days.",
        },
        {
            "question_text": "How many days are in the month of December?",
            "question_type": "multiple_choice",
            "correct_answer": "31",
            "wrong_answers": ["30", "29", "28"],
            "explanation": "December always has 31 days.",
        },
        {
            "question_text": "How many days are in the month of January?",
            "question_type": "multiple_choice",
            "correct_answer": "31",
            "wrong_answers": ["30", "29", "28"],
            "explanation": "January always has 31 days.",
        },
        {
            "question_text": "Which month comes after January?",
            "question_type": "multiple_choice",
            "correct_answer": "February",
            "wrong_answers": ["March", "December", "April"],
            "explanation": "The month after January is February.",
        },
        {
            "question_text": "Which month comes before December?",
            "question_type": "multiple_choice",
            "correct_answer": "November",
            "wrong_answers": ["October", "January", "February"],
            "explanation": "The month before December is November.",
        },
        {
            "question_text": "Which month comes before January?",
            "question_type": "multiple_choice",
            "correct_answer": "December",
            "wrong_answers": ["November", "February", "October"],
            "explanation": "The month before January is December.",
        },
        {
            "question_text": "Which month comes after April?",
            "question_type": "multiple_choice",
            "correct_answer": "May",
            "wrong_answers": ["March", "June", "July"],
            "explanation": "The month after April is May.",
        },
        {
            "question_text": "How many months are there in a year?",
            "question_type": "multiple_choice",
            "correct_answer": "12",
            "wrong_answers": ["10", "11", "13"],
            "explanation": "A year always has 12 months.",
        },
        {
            "question_text": "How many days are there in a week?",
            "question_type": "multiple_choice",
            "correct_answer": "7",
            "wrong_answers": ["6", "5", "8"],
            "explanation": "Sunday to Saturday makes 7 days.",
        },
        {
            "question_text": "Which day comes after Wednesday?",
            "question_type": "multiple_choice",
            "correct_answer": "Thursday",
            "wrong_answers": ["Tuesday", "Friday", "Monday"],
            "explanation": "The order is Wednesday → Thursday.",
        },
        {
            "question_text": "Which day comes before Sunday?",
            "question_type": "multiple_choice",
            "correct_answer": "Saturday",
            "wrong_answers": ["Friday", "Monday", "Thursday"],
            "explanation": "Saturday comes right before Sunday.",
        },
        {
            "question_text": "How many days are in February during a leap year?",
            "question_type": "multiple_choice",
            "correct_answer": "29",
            "wrong_answers": ["28", "30", "31"],
            "explanation": "February has 29 days in a leap year.",
        },
        {
            "question_text": "Which month comes after August?",
            "question_type": "multiple_choice",
            "correct_answer": "September",
            "wrong_answers": ["October", "July", "June"],
            "explanation": "The order is August → September.",
        },
        {
            "question_text": "Which month comes before April?",
            "question_type": "multiple_choice",
            "correct_answer": "March",
            "wrong_answers": ["February", "May", "January"],
            "explanation": "March comes just before April.",
        },
        {
            "question_text": "How many hours are there in one day?",
            "correct_answer": "24",
            "wrong_answers": ["12", "20", "30"],
            "question_type": "multiple_choice",
            "explanation": "A full day has 24 hours.",
        },
        {
            "question_text": "How many minutes are in one hour?",
            "correct_answer": "60",
            "wrong_answers": ["100", "30", "45"],
            "question_type": "multiple_choice",
            "explanation": "Each hour has 60 minutes.",
        },
        {
            "question_text": "If today is Monday, what day will it be in 3 days?",
            "question_type": "multiple_choice",
            "correct_answer": "Thursday",
            "wrong_answers": ["Wednesday", "Friday", "Saturday"],
            "explanation": "Monday + 3 days = Thursday.",
        },
        {
            "question_text": "If today is Friday, what day was it 2 days ago?",
            "question_type": "multiple_choice",
            "correct_answer": "Wednesday",
            "wrong_answers": ["Tuesday", "Thursday", "Monday"],
            "explanation": "Two days before Friday is Wednesday.",
        },
        {
            "question_text": "How many seconds are in one minute?",
            "question_type": "multiple_choice",
            "correct_answer": "60",
            "wrong_answers": ["100", "30", "90"],
            "explanation": "1 minute = 60 seconds.",
        },
        {
            "question_text": "Which month has 28 days?",
            "question_type": "multiple_choice",
            "correct_answer": "February",
            "wrong_answers": ["March", "January", "April"],
            "explanation": "February normally has 28 days.",
        },
        {
            "question_text": "Which season comes after winter?",
            "question_type": "multiple_choice",
            "correct_answer": "Spring",
            "wrong_answers": ["Summer", "Autumn", "Winter"],
            "explanation": "Winter → Spring → Summer → Autumn.",
        }
    ]

    
    if not questions_data:
        print("[WARNING] No questions defined in questions_data list!")
        print("Please add questions to the questions_data list in the script.")
        return
    
    # Use shared utility function to process questions
    results = process_questions(
        level=level_3,
        topic=date_time_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n[OK] All questions are associated with Date and Time topic for Year 3")

if __name__ == "__main__":
    print("=" * 80)
    print("Adding/Updating Date and Time questions for Year 3")
    print("=" * 80)
    
    result = setup_date_time_topic()
    if result:
        date_time_topic, level_3 = result
        add_date_time_questions(date_time_topic, level_3)
        print("[SUCCESS] Script completed!")
    else:
        print("[ERROR] Failed to set up topic. Please check the errors above.")

