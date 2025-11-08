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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer
from django.core.files import File
from django.conf import settings

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
            "wrong_answers": ["50c + 20c + 20c + 10c", "20c + 20c + 20c + 20c", "10c + 10c + 10c + 10c"],
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
    ]
    
    print(f"\n[INFO] Processing {len(questions_data)} Finance questions for Year 3...\n")
    
    if len(questions_data) == 0:
        print("[INFO] No questions defined yet. Add questions to the questions_data list.")
        return
    
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
        
        # Add/update image if specified
        if "image_path" in q_data and q_data["image_path"]:
            image_path = q_data["image_path"]
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(full_image_path):
                with open(full_image_path, 'rb') as f:
                    question.image.save(os.path.basename(image_path), File(f), save=True)
                print(f"      [IMAGE] Added/updated image: {image_path}")
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
    
    print(f"\n[SUMMARY]")
    print(f"   [CREATE] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"   [SKIP] Skipped: {skipped_count} questions")
    print(f"\n[OK] All questions are associated with Finance topic for Year 3")

if __name__ == "__main__":
    print("[INFO] Setting up Finance topic for Year 3...\n")
    result = setup_finance_topic()
    
    if result:
        finance_topic, level_3 = result
        print("\n" + "="*60)
        add_finance_questions(finance_topic, level_3)
        print("\n[OK] Done!")

