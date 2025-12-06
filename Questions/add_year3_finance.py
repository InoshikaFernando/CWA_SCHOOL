#!/usr/bin/env python
"""
Add/Update "Finance" questions for Year 3
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

def setup_finance_topic():
    """Create Finance topic and associate with Year 3"""
    
    # Get or create the "Finance" topic
    # Handle case where multiple topics with same name exist
    finance_topic = Topic.objects.filter(name="Finance").first()
    if not finance_topic:
        finance_topic = Topic.objects.create(name="Finance")
        print(f"[OK] Created topic: Finance")
    else:
        print(f"[INFO] Topic already exists: Finance")
    
    # Get Year 3 level
    level_3 = Level.objects.filter(level_number=3).first()
    
    if not level_3:
        print("[ERROR] Year 3 level not found!")
        return None
    
    print(f"[INFO] Found Year 3: {level_3}")
    
    # Check if Finance is already associated
    if level_3.topics.filter(name="Finance").exists():
        print("[INFO] Year 3 already has Finance topic associated.")
        print(f"   Current topics for Year 3: {', '.join([t.name for t in level_3.topics.all()])}")
    else:
        # Associate Finance topic with Year 3
        level_3.topics.add(finance_topic)
        print(f"[OK] Successfully associated Finance topic with Year 3")
        print(f"   Year 3 now has topics: {', '.join([t.name for t in level_3.topics.all()])}")
    
    return finance_topic, level_3

def add_finance_questions(finance_topic, level_3):
    """Add/Update Finance questions for Year 3"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Which coins make $1?",
            "question_type": "multiple_choice",
            "correct_answer": "50c + 20c + 10c + 10c + 10c",
            "wrong_answers": ["50c + 20c + 30c + 10c", "20c + 20c + 20c + 20c", "10c + 10c + 10c + 10c"],
            "explanation": "50c + 20c + 10c + 10c + 10c = 100c = $1. This combination adds up to exactly one dollar.",
        },
        {
            "question_text": "How much money is this?\n\n$2 coin + $1 coin + 50c",
            "question_type": "multiple_choice",
            "correct_answer": "$3.50",
            "wrong_answers": ["$2.50", "$4", "$3"],
            "explanation": "$2.00 + $1.00 + $0.50 = $3.50. Add the values of all the coins together.",
        },
        {
            "question_text": "You buy an ice cream for $3.50 and pay with a $5 note.\n\nHow much change do you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$1.50",
            "wrong_answers": ["$1.20", "$2", "$1.80"],
            "explanation": "$5.00 - $3.50 = $1.50. Subtract the cost from the amount paid to find the change.",
        },
        {
            "question_text": "You have two $2 coins and one 50c coin.\n\nHow much money do you have in total?",
            "question_type": "multiple_choice",
            "correct_answer": "$4.50",
            "wrong_answers": ["$5", "$3.50", "$2.50"],
            "explanation": "$2 + $2 + $0.50 = $4.50. Add the coins together."
        },
        {
            "question_text": "A sandwich costs $4. You pay with a $10 note.\n\nHow much change will you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$6",
            "wrong_answers": ["$5", "$4", "$7"],
            "explanation": "$10 - $4 = $6. Subtract the price from the amount paid."
        },
        {
            "question_text": "Which of these is worth the most?",
            "question_type": "multiple_choice",
            "correct_answer": "$5 note",
            "wrong_answers": ["$2 coin", "50c coin", "$1 coin"],
            "explanation": "$5 is more than $2, $1, or 50c."
        },
        {
            "question_text": "You buy a toy for $6.50 and give the shopkeeper $10.\n\nWhat is your change?",
            "question_type": "multiple_choice",
            "correct_answer": "$3.50",
            "wrong_answers": ["$4", "$2.50", "$3"],
            "explanation": "$10.00 - $6.50 = $3.50."
        },
        {
            "question_text": "Which coins could you use to make $2?",
            "question_type": "multiple_choice",
            "correct_answer": "$1 + $1",
            "wrong_answers": ["50c + 20c + 20c", "50c + 50c + 20c + 10c", "$1 + 50c"],
            "explanation": "$1 + $1 = $2 exactly."
        },
        {
            "question_text": "A pencil costs $1.50. You have $5.\n\nHow many pencils can you buy?",
            "question_type": "multiple_choice",
            "correct_answer": "3",
            "wrong_answers": ["2", "4", "5"],
            "explanation": "$1.50 × 3 = $4.50, which is less than $5. Four pencils would cost $6, too much."
        },
        {
            "question_text": "You have 4 coins: 20c, 50c, $1, and $2.\n\nHow much money do you have?",
            "question_type": "multiple_choice",
            "correct_answer": "$3.70",
            "wrong_answers": ["$3.50", "$2.70", "$4"],
            "explanation": "$2 + $1 + $0.50 + $0.20 = $3.70."
        },
        {
            "question_text": "A comic costs $4. You give $5.\n\nWhat coin could you get as change?",
            "question_type": "multiple_choice",
            "correct_answer": "$1 coin",
            "wrong_answers": ["50c coin", "$2 coin", "20c coin"],
            "explanation": "$5 - $4 = $1, so you get a $1 coin back."
        },
        {
            "question_text": "Which group of coins makes $1.50?",
            "question_type": "multiple_choice",
            "correct_answer": "$1 + 50c",
            "wrong_answers": ["50c + 50c + 20c + 20c", "$1 + 20c + 20c", "50c + 20c + 10c"],
            "explanation": "$1 + 50c = $1.50."
        },
        {
            "question_text": "You have $10. You spend $3 on lunch and $4 on a drink.\n\nHow much money do you have left?",
            "question_type": "multiple_choice",
            "correct_answer": "$3",
            "wrong_answers": ["$2", "$4", "$3.50"],
            "explanation": "$10 - $3 - $4 = $3."
        },
        {
            "question_text": "Liam buys a chocolate bar for $2.80 and a drink for $1.20.\n\nHow much does he spend in total?",
            "question_type": "multiple_choice",
            "correct_answer": "$4.00",
            "wrong_answers": ["$3.50", "$4.50", "$5.00"],
            "explanation": "$2.80 + $1.20 = $4.00."
        },
        {
            "question_text": "A sandwich costs $3.50 and a juice box costs $2.\n\nHow much do both items cost together?",
            "question_type": "multiple_choice",
            "correct_answer": "$5.50",
            "wrong_answers": ["$6", "$4.50", "$5"],
            "explanation": "$3.50 + $2.00 = $5.50."
        },
        {
            "question_text": "Emma has $10. She buys a toy for $6.75.\n\nHow much money does she have left?",
            "question_type": "multiple_choice",
            "correct_answer": "$3.25",
            "wrong_answers": ["$4", "$2.50", "$3"],
            "explanation": "$10.00 - $6.75 = $3.25."
        },
        {
            "question_text": "A packet of stickers costs $4.20. You pay with a $5 note.\n\nHow much change should you get?",
            "question_type": "multiple_choice",
            "correct_answer": "80c",
            "wrong_answers": ["70c", "90c", "$1"],
            "explanation": "$5.00 - $4.20 = $0.80 (80 cents)."
        },
        {
            "question_text": "A muffin costs $2.40 and a smoothie costs $4.60.\n\nYou pay with a $10 note. How much change do you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$3.00",
            "wrong_answers": ["$2.50", "$3.50", "$4"],
            "explanation": "$2.40 + $4.60 = $7.00. Then $10 - $7 = $3.00."
        },
        {
            "question_text": "You buy 3 apples that cost 60c each.\n\nHow much do you pay altogether?",
            "question_type": "multiple_choice",
            "correct_answer": "$1.80",
            "wrong_answers": ["$1.60", "$2", "$1.50"],
            "explanation": "60c × 3 = 180c = $1.80."
        },
        {
            "question_text": "A toy car costs $8.50. You have $10.\n\nDo you have enough money, and if yes, how much change will you get?",
            "question_type": "multiple_choice",
            "correct_answer": "Yes, $1.50 change",
            "wrong_answers": ["No, not enough money", "Yes, 50c change", "Yes, $2 change"],
            "explanation": "$10.00 - $8.50 = $1.50, so you have enough and get $1.50 change."
        },
        {
            "question_text": "Noah buys a comic for $3.80 and a pen for $1.20.\n\nHe pays with a $5 note. What is his change?",
            "question_type": "multiple_choice",
            "correct_answer": "$0.00 (no change)",
            "wrong_answers": ["$1", "50c", "$0.20"],
            "explanation": "$3.80 + $1.20 = $5.00 exactly, so no change."
        },
        {
            "question_text": "A cupcake costs $2.25. You buy two.\n\nHow much do you spend?",
            "question_type": "multiple_choice",
            "correct_answer": "$4.50",
            "wrong_answers": ["$5", "$4", "$3.50"],
            "explanation": "$2.25 × 2 = $4.50."
        },
        {
            "question_text": "You buy a ball for $6. You have $10. Then you buy an ice block for $2.\n\nHow much money do you have left?",
            "question_type": "multiple_choice",
            "correct_answer": "$2",
            "wrong_answers": ["$4", "$3", "$1"],
            "explanation": "$6 + $2 = $8 spent. $10 - $8 = $2 left."
        },
        {
            "question_text": "You have two $1 coins and three 50c coins.\n\nHow much money do you have altogether?",
            "question_type": "multiple_choice",
            "correct_answer": "$3.50",
            "wrong_answers": ["$3", "$2.50", "$4"],
            "explanation": "$1 + $1 + 50c + 50c + 50c = $3.50."
        },
        {
            "question_text": "Which group of coins makes $2?",
            "question_type": "multiple_choice",
            "correct_answer": "$1 + $1",
            "wrong_answers": ["50c + 50c + 50c + 20c", "$1 + 50c + 20c + 20c", "50c + 20c + 20c + 10c"],
            "explanation": "$1 + $1 = $2 exactly."
        },
        {
            "question_text": "You have a $5 note, a $2 coin, and a $1 coin.\n\nHow much do you have in total?",
            "question_type": "multiple_choice",
            "correct_answer": "$8",
            "wrong_answers": ["$7", "$6", "$9"],
            "explanation": "$5 + $2 + $1 = $8."
        },
        {
            "question_text": "Which coins could you use to make $1.20?",
            "question_type": "multiple_choice",
            "correct_answer": "$1 coin + 20c coin",
            "wrong_answers": ["50c + 50c + 50c + 20c", "$1 + 50c", "50c + 20c + 10c + 10c"],
            "explanation": "$1 + 20c = $1.20."
        },
        {
            "question_text": "You have 4 coins: 20c, 20c, 50c, and $1.\n\nHow much money is that?",
            "question_type": "multiple_choice",
            "correct_answer": "$1.90",
            "wrong_answers": ["$1.70", "$1.80", "$2"],
            "explanation": "$1 + 50c + 20c + 20c = $1.90."
        },
        {
            "question_text": "You buy a drink for $3.40 and pay with a $5 note.\n\nHow much change will you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$1.60",
            "wrong_answers": ["$2", "$1.50", "$1.40"],
            "explanation": "$5.00 - $3.40 = $1.60."
        },
        {
            "question_text": "A book costs $8. You give the shopkeeper $10.\n\nWhat is your change?",
            "question_type": "multiple_choice",
            "correct_answer": "$2",
            "wrong_answers": ["$1", "$3", "$2.50"],
            "explanation": "$10 - $8 = $2."
        },
        {
            "question_text": "You have $10. You buy a toy for $6.75 and a drink for $2.25.\n\nHow much do you have left?",
            "question_type": "multiple_choice",
            "correct_answer": "$1",
            "wrong_answers": ["$0.75", "$1.25", "$1.50"],
            "explanation": "$6.75 + $2.25 = $9.00. $10 - $9 = $1 left."
        },
        {
            "question_text": "A sandwich costs $4.80. You pay with a $10 note.\n\nHow much change do you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$5.20",
            "wrong_answers": ["$6", "$4.80", "$5"],
            "explanation": "$10.00 - $4.80 = $5.20."
        },
        {
            "question_text": "You buy a muffin for $2.50 and a cookie for $1.80.\n\nIf you pay with a $5 note, how much change will you get?",
            "question_type": "multiple_choice",
            "correct_answer": "$0.70",
            "wrong_answers": ["$0.60", "$1", "$0.80"],
            "explanation": "$2.50 + $1.80 = $4.30. $5 - $4.30 = $0.70."
        }
    ]
    
    # Use shared utility function to process questions
    if len(questions_data) == 0:
        print("[INFO] No questions defined yet. Add questions to the questions_data list.")
        return
    
    results = process_questions(
        level=level_3,
        topic=finance_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n[OK] All questions are associated with Finance topic for Year 3")
    
    # Legacy code below - kept for reference but not used
    """
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by exact text match and image if provided)
        query = Question.objects.filter(
            level=level_3,
            question_text=q_data["question_text"]
        )
        
        # If image_path is specified, also match by image
        if "image_path" in q_data and q_data["image_path"]:
            image_name = os.path.basename(q_data["image_path"])
            # Try to find by exact image path first
            existing = query.filter(image=q_data["image_path"]).first()
            if not existing:
                # Fallback: match by image filename (handles different path formats)
                for q in query:
                    if q.image and (image_name in q.image.name or q.image.name.endswith(image_name)):
                        existing = q
                        break
            if not existing:
                # Last resort: just get first match
                existing = query.first()
        else:
            existing = query.first()
        
        if existing:
            question = existing
            question_updated = False
            
            # Update explanation if changed
            if question.explanation != q_data.get("explanation", ""):
                question.explanation = q_data.get("explanation", "")
                question_updated = True
            
            # Ensure topic is set
            if not question.topic:
                question.topic = finance_topic
                question_updated = True
            
            if question_updated:
                question.save()
            
            # Check if answers need updating
            existing_answers = Answer.objects.filter(question=question)
            existing_correct = existing_answers.filter(is_correct=True).first()
            
            # For multiple choice: check if correct answer matches
            if q_data["question_type"] == "multiple_choice":
                correct_answer_text = q_data.get("correct_answer", "")
                wrong_answers = q_data.get("wrong_answers", [])
                
                # Check if correct answer exists and matches
                if correct_answer_text:
                    if not existing_correct or existing_correct.answer_text != correct_answer_text:
                        # Answers need updating
                        Answer.objects.filter(question=question).delete()
                        question_updated = True
                    else:
                        # Check wrong answers count
                        existing_wrong = existing_answers.filter(is_correct=False)
                        existing_wrong_texts = set(a.answer_text for a in existing_wrong)
                        expected_wrong_texts = set(wrong_answers)
                        
                        if existing_wrong_texts != expected_wrong_texts:
                            # Wrong answers changed, update all
                            Answer.objects.filter(question=question).delete()
                            question_updated = True
            
            if question_updated:
                print(f"  [UPDATE] Question {i}: Updating...")
                updated_count += 1
            else:
                # Check if answers exist - if not, we need to create them
                if not Answer.objects.filter(question=question).exists():
                    correct_answer = q_data.get("correct_answer", "").strip()
                    if correct_answer or (q_data["question_type"] == "multiple_choice" and q_data.get("correct_answer")):
                        question_updated = True
                        print(f"  [UPDATE] Question {i}: Missing answers, will add them...")
                        updated_count += 1
                    else:
                        print(f"  [SKIP] Question {i}: No changes needed and no answer provided")
                        skipped_count += 1
                        continue
                else:
                    print(f"  [SKIP] Question {i}: No changes needed")
                    skipped_count += 1
                    continue
        else:
            # Create new question
            question = Question.objects.create(
                level=level_3,
                topic=finance_topic,  # Set topic directly on question
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty=1,
                points=1,
                explanation=q_data.get("explanation", "")
            )
            print(f"  [CREATE] Question {i}: Created new question")
            created_count += 1
            question_updated = True
        
        # Add/update image if specified - use existing file, don't copy
        if "image_path" in q_data and q_data["image_path"]:
            image_path = q_data["image_path"]
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(full_image_path):
                # Set image path directly without copying the file
                question.image.name = image_path
                question.save()
                print(f"      [IMAGE] Set image path: {image_path}")
            else:
                print(f"      [WARNING] Image not found: {full_image_path}")
        
        # Ensure question has topic set and level has topic associated
        if not question.topic:
            question.topic = finance_topic
            question.save()
        question.level.topics.add(finance_topic)
        
        # Create/update answers if question was created or updated
        if question_updated:
            # Delete existing answers if updating (only if we're actually updating)
            if existing and Answer.objects.filter(question=question).exists():
                Answer.objects.filter(question=question).delete()
            
            # Create answers
            if q_data["question_type"] == "multiple_choice":
                correct_answer_text = q_data.get("correct_answer", "")
                wrong_answers = q_data.get("wrong_answers", [])
                
                if correct_answer_text:
                    # Mix correct and wrong answers
                    all_answers = [correct_answer_text] + wrong_answers
                    random.shuffle(all_answers)
                    
                    order = 0
                    for answer_text in all_answers:
                        is_correct = (answer_text == correct_answer_text)
                        Answer.objects.create(
                            question=question,
                            answer_text=answer_text,
                            is_correct=is_correct,
                            order=order
                        )
                        order += 1
                    print(f"      [ANSWERS] Created {len(all_answers)} answer(s)")
    """

if __name__ == "__main__":
    print("[INFO] Setting up Finance topic for Year 3...\n")
    result = setup_finance_topic()
    
    if result:
        finance_topic, level_3 = result
        print("\n" + "="*60)
        add_finance_questions(finance_topic, level_3)
        print("\n[OK] Done!")

