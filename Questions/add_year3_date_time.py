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
        }
    ]

    
    if not questions_data:
        print("[WARNING] No questions defined in questions_data list!")
        print("Please add questions to the questions_data list in the script.")
        return
    
    print(f"\n{'=' * 80}")
    print(f"Processing {len(questions_data)} Date and Time questions for Year 3")
    print(f"{'=' * 80}\n")
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for idx, q_data in enumerate(questions_data, 1):
        question_text = q_data.get("question_text", "").strip()
        if not question_text:
            print(f"[SKIP] Question {idx}: Empty question text")
            skipped_count += 1
            continue
        
        question_type = q_data.get("question_type", "multiple_choice")
        correct_answer = q_data.get("correct_answer", "").strip()
        wrong_answers = q_data.get("wrong_answers", [])
        explanation = q_data.get("explanation", "")
        image_path = q_data.get("image_path", None)
        
        if not correct_answer:
            print(f"[SKIP] Question {idx}: No correct answer provided")
            skipped_count += 1
            continue
        
        # Check if question already exists (by exact text match)
        existing_question = Question.objects.filter(
            question_text=question_text,
            level=level_3,
            topic=date_time_topic
        ).first()
        
        if existing_question:
            # Question exists - check if we need to update answers
            existing_correct = existing_question.answers.filter(is_correct=True).first()
            needs_update = False
            
            if not existing_correct or existing_correct.answer_text != correct_answer:
                needs_update = True
            
            if needs_update:
                # Delete old answers and create new ones
                existing_question.answers.all().delete()
                
                # Update question explanation if provided
                if explanation:
                    existing_question.explanation = explanation
                    existing_question.save()
                
                # Create correct answer
                Answer.objects.create(
                    question=existing_question,
                    answer_text=correct_answer,
                    is_correct=True
                )
                
                # Create wrong answers
                for wrong_answer in wrong_answers:
                    if wrong_answer and wrong_answer.strip():
                        Answer.objects.create(
                            question=existing_question,
                            answer_text=wrong_answer.strip(),
                            is_correct=False
                        )
                
                # Update image if provided
                if image_path:
                    image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    if os.path.exists(image_full_path):
                        with open(image_full_path, 'rb') as f:
                            existing_question.image.save(
                                os.path.basename(image_path),
                                File(f),
                                save=True
                            )
                    else:
                        # Set image path even if file doesn't exist locally (for production)
                        existing_question.image.name = image_path
                        existing_question.save()
                
                print(f"[UPDATE] Question {idx}: Updated '{question_text[:50]}...'")
                updated_count += 1
            else:
                print(f"[SKIP] Question {idx}: Already exists and up-to-date")
                skipped_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_3,
                topic=date_time_topic,
                question_text=question_text,
                question_type=question_type,
                difficulty=1,
                points=1
            )
            
            # Add image if provided
            if image_path:
                image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                if os.path.exists(image_full_path):
                    with open(image_full_path, 'rb') as f:
                        question.image.save(
                            os.path.basename(image_path),
                            File(f),
                            save=True
                        )
                else:
                    # Set image path even if file doesn't exist locally (for production)
                    question.image.name = image_path
                    question.save()
            
            # Set question explanation if provided
            if explanation:
                question.explanation = explanation
                question.save()
            
            # Create correct answer
            Answer.objects.create(
                question=question,
                answer_text=correct_answer,
                is_correct=True
            )
            
            # Create wrong answers
            for wrong_answer in wrong_answers:
                if wrong_answer and wrong_answer.strip():
                    Answer.objects.create(
                        question=question,
                        answer_text=wrong_answer.strip(),
                        is_correct=False
                    )
            
            print(f"[ADDED] Question {idx}: '{question_text[:50]}...'")
            added_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"SUMMARY:")
    print(f"  Added: {added_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(questions_data)}")
    print(f"{'=' * 80}\n")

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

