#!/usr/bin/env python
"""
Add/Update "Factors" questions for Year 6
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

def setup_factors_topic():
    """Create Factors topic and associate with Year 6"""
    
    # Get or create the "Factors" topic
    factors_topic = Topic.objects.filter(name="Factors").first()
    if not factors_topic:
        factors_topic = Topic.objects.create(name="Factors")
        print(f"[OK] Created topic: Factors")
    else:
        print(f"[INFO] Topic already exists: Factors")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return None
    
    print(f"[INFO] Found Year 6: {level_6}")
    
    # Check if Factors is already associated
    if level_6.topics.filter(name="Factors").exists():
        print("[INFO] Year 6 already has Factors topic associated.")
        print(f"   Current topics for Year 6: {', '.join([t.name for t in level_6.topics.all()])}")
    else:
        # Associate Factors topic with Year 6
        level_6.topics.add(factors_topic)
        print(f"[OK] Successfully associated Factors topic with Year 6")
        print(f"   Year 6 now has topics: {', '.join([t.name for t in level_6.topics.all()])}")
    
    return factors_topic, level_6

def add_factors_questions(factors_topic, level_6):
    """Add/Update Factors questions for Year 6"""
    
    # Define all questions
    questions_data = [
        {
            "question_text": "What is the LCM of 3 and 4?",
            "question_type": "multiple_choice",
            "correct_answer": "12",
            "wrong_answers": ["6", "8", "24"],
            "explanation": "Multiples of 3: 3, 6, 9, 12. Multiples of 4: 4, 8, 12. Lowest common multiple is 12."
        },
        {
            "question_text": "What is the LCM of 5 and 10?",
            "question_type": "multiple_choice",
            "correct_answer": "10",
            "wrong_answers": ["5", "20", "15"],
            "explanation": "Multiples of 5: 5, 10, 15. Multiples of 10: 10, 20, 30. LCM is 10."
        },
        {
            "question_text": "What is the LCM of 6 and 8?",
            "question_type": "multiple_choice",
            "correct_answer": "24",
            "wrong_answers": ["12", "16", "48"],
            "explanation": "Multiples of 6: 6, 12, 18, 24. Multiples of 8: 8, 16, 24. LCM is 24."
        },
        {
            "question_text": "What is the LCM of 9 and 12?",
            "question_type": "multiple_choice",
            "correct_answer": "36",
            "wrong_answers": ["18", "24", "48"],
            "explanation": "Multiples of 9: 9, 18, 27, 36. Multiples of 12: 12, 24, 36. LCM is 36."
        },
        {
            "question_text": "What is the LCM of 7 and 9?",
            "question_type": "multiple_choice",
            "correct_answer": "63",
            "wrong_answers": ["27", "45", "72"],
            "explanation": "Multiples of 7: 7, 14, 21, 28, 35, 42, 49, 56, 63. Multiples of 9: 9, 18, 27, 36, 45, 54, 63. LCM is 63."
        },
        {
            "question_text": "A bus arrives every 12 minutes. Another arrives every 18 minutes. After how many minutes will both buses arrive together?",
            "question_type": "multiple_choice",
            "correct_answer": "36 minutes",
            "wrong_answers": ["24 minutes", "48 minutes", "72 minutes"],
            "explanation": "LCM of 12 and 18 is 36, so they meet every 36 minutes."
        },
        {
            "question_text": "Two lights flash every 5 seconds and 8 seconds. When will they flash together?",
            "question_type": "multiple_choice",
            "correct_answer": "40 seconds",
            "wrong_answers": ["20 seconds", "30 seconds", "50 seconds"],
            "explanation": "LCM of 5 and 8 is 40."
        },
        {
            "question_text": "A gardener waters roses every 6 days and sunflowers every 15 days. When will both be watered on the same day again?",
            "question_type": "multiple_choice",
            "correct_answer": "30 days",
            "wrong_answers": ["21 days", "45 days", "60 days"],
            "explanation": "LCM of 6 and 15 is 30."
        },
        {
            "question_text": "What is the HCF of 8 and 12?",
            "question_type": "multiple_choice",
            "correct_answer": "4",
            "wrong_answers": ["2", "6", "8"],
            "explanation": "Factors of 8: 1, 2, 4, 8. Factors of 12: 1, 2, 3, 4, 6, 12. Highest common factor is 4."
        },
        {
            "question_text": "What is the HCF of 15 and 20?",
            "question_type": "multiple_choice",
            "correct_answer": "5",
            "wrong_answers": ["10", "15", "20"],
            "explanation": "Factors of 15: 1, 3, 5, 15. Factors of 20: 1, 2, 4, 5, 10, 20. HCF is 5."
        },
        {
            "question_text": "What is the HCF of 18 and 24?",
            "question_type": "multiple_choice",
            "correct_answer": "6",
            "wrong_answers": ["3", "12", "9"],
            "explanation": "Common factors of 18 and 24 are 1, 2, 3, 6. Highest is 6."
        },
        {
            "question_text": "What is the HCF of 9 and 27?",
            "question_type": "multiple_choice",
            "correct_answer": "9",
            "wrong_answers": ["3", "6", "27"],
            "explanation": "Factors of 9: 1, 3, 9. Factors of 27: 1, 3, 9, 27. HCF is 9."
        },
        {
            "question_text": "What is the HCF of 16 and 40?",
            "question_type": "multiple_choice",
            "correct_answer": "8",
            "wrong_answers": ["4", "6", "10"],
            "explanation": "Common factors of 16 and 40: 1, 2, 4, 8. Highest is 8."
        },
        {
            "question_text": "What is the HCF of 21 and 28?",
            "question_type": "multiple_choice",
            "correct_answer": "7",
            "wrong_answers": ["3", "14", "21"],
            "explanation": "Common factors of 21 and 28: 1, 7. Highest is 7."
        },
        {
            "question_text": "What is the HCF of 30 and 45?",
            "question_type": "multiple_choice",
            "correct_answer": "15",
            "wrong_answers": ["5", "10", "30"],
            "explanation": "Common factors of 30 and 45: 1, 3, 5, 15. Highest is 15."
        },
        {
            "question_text": "What is the HCF of 12, 18, and 24?",
            "question_type": "multiple_choice",
            "correct_answer": "6",
            "wrong_answers": ["3", "4", "12"],
            "explanation": "Common factors: 1, 2, 3, 6. Highest is 6."
        },
        {
            "question_text": "What is the HCF of 14 and 49?",
            "question_type": "multiple_choice",
            "correct_answer": "7",
            "wrong_answers": ["14", "21", "28"],
            "explanation": "Common factors of 14 and 49: 1, 7. Highest is 7."
        },
        {
            "question_text": "What is the HCF of 32 and 56?",
            "question_type": "multiple_choice",
            "correct_answer": "8",
            "wrong_answers": ["4", "16", "32"],
            "explanation": "Common factors of 32 and 56: 1, 2, 4, 8. Highest is 8."
        }
    ]
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for q_data in questions_data:
        question_text = q_data["question_text"]
        question_type = q_data.get("question_type", "multiple_choice")
        correct_answer = q_data["correct_answer"]
        wrong_answers = q_data.get("wrong_answers", [])
        explanation = q_data.get("explanation", "")
        image_path = q_data.get("image_path", None)
        
        # Check if question already exists (by exact text match)
        existing_question = Question.objects.filter(
            question_text=question_text,
            level=level_6,
            topic=factors_topic
        ).first()
        
        if existing_question:
            # Question exists - check if we need to update answers
            existing_correct_answer = existing_question.answers.filter(is_correct=True).first()
            needs_update = False
            
            # Check if correct answer changed
            if not existing_correct_answer or existing_correct_answer.answer_text != correct_answer:
                needs_update = True
            
            # Check if explanation changed
            if existing_question.explanation != explanation:
                needs_update = True
            
            if needs_update:
                # Delete old answers
                existing_question.answers.all().delete()
                
                # Update question explanation
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
                
                updated_count += 1
                print(f"  [UPDATED] {question_text[:60]}...")
            else:
                skipped_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_6,
                topic=factors_topic,
                question_text=question_text,
                question_type=question_type,
                difficulty=1,
                points=1,
                explanation=explanation
            )
            
            # Set image if provided
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
            
            added_count += 1
            print(f"  [ADDED] {question_text[:60]}...")
    
    print(f"\n[SUMMARY]")
    print(f"  Added: {added_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(questions_data)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add/Update Year 6 Factors questions')
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

