#!/usr/bin/env python
"""
Add/Update "Measurements" questions for Year 5
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

def setup_measurements_topic():
    """Create Measurements topic and associate with Year 5"""
    
    # Get or create the "Measurements" topic
    # Handle case where multiple topics with same name exist
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
        print(f"[OK] Created topic: Measurements")
    else:
        print(f"[INFO] Topic already exists: Measurements")
    
    # Get Year 5 level
    level_5 = Level.objects.filter(level_number=5).first()
    
    if not level_5:
        print("[ERROR] Year 5 level not found!")
        return None
    
    print(f"[INFO] Found Year 5: {level_5}")
    
    # Check if Measurements is already associated
    if level_5.topics.filter(name="Measurements").exists():
        print("[INFO] Year 5 already has Measurements topic associated.")
        print(f"   Current topics for Year 5: {', '.join([t.name for t in level_5.topics.all()])}")
    else:
        # Associate Measurements topic with Year 5
        level_5.topics.add(measurements_topic)
        print(f"[OK] Successfully associated Measurements topic with Year 5")
        print(f"   Year 5 now has topics: {', '.join([t.name for t in level_5.topics.all()])}")
    
    return measurements_topic, level_5

def add_measurements_questions(measurements_topic, level_5):
    """Add/Update Measurements questions for Year 5"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match and image if provided
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Find the unknown length.",
            "question_type": "multiple_choice",
            "correct_answer": "2cm",
            "wrong_answers": ["3cm", "4cm", "5cm"],
            "explanation": "Use the given measurements to find the unknown length.",
            "image_path": "questions/year5/measurements/image1.png",
        },
        {
            "question_text": "Find the unknown length.",
            "question_type": "multiple_choice",
            "correct_answer": "5cm",
            "wrong_answers": ["2cm", "3cm", "4cm"],
            "explanation": "Use the given measurements to find the unknown length.",
            "image_path": "questions/year5/measurements/image2.png",
        },
        {
            "question_text": "Find the unknown length.",
            "question_type": "multiple_choice",
            "correct_answer": "32cm",
            "wrong_answers": ["27cm", "30cm", "35cm"],
            "explanation": "Use the given measurements to find the unknown length.",
            "image_path": "questions/year5/measurements/image3.png",
        },
        {
            "question_text": "Find the unknown length.",
            "question_type": "multiple_choice",
            "correct_answer": "6cm",
            "wrong_answers": ["5cm", "4cm", "3cm"],
            "explanation": "Use the given measurements to find the unknown length.",
            "image_path": "questions/year5/measurements/image4.png",
        },
        {
            "question_text": "Find the unknown length.",
            "question_type": "multiple_choice",
            "correct_answer": "2cm",
            "wrong_answers": ["1cm", "3cm", "4cm"],
            "explanation": "Use the given measurements to find the unknown length.",
            "image_path": "questions/year5/measurements/image5.png",
        },
        {
            "question_text": "What is the height of the tide at 3:00 p.m. in the afternoon?",
            "question_type": "multiple_choice",
            "correct_answer": "1.8 meters",
            "wrong_answers": ["1.2 meters", "2.1 meters", "1.5 meters", "0.9 meters"],
            "explanation": "Read the tide height from the graph at 3:00 p.m.",
            "image_path": "questions/year5/measurements/image.png",
        },
        {
            "question_text": "What is the height of the tide at 7:00 p.m.?",
            "question_type": "multiple_choice",
            "correct_answer": "3.4",
            "wrong_answers": ["3.5", "3.3", "3.6"],
            "explanation": "Read the tide height from the graph at 7:00 p.m.",
            "image_path": "questions/year5/measurements/image.png",
        },
    ]
    
    print(f"\n[INFO] Processing {len(questions_data)} Measurements questions for Year 5...\n")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by exact text match and image if provided)
        query = Question.objects.filter(
            level=level_5,
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
                question.topic = measurements_topic
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
                level=level_5,
                topic=measurements_topic,  # Set topic directly on question
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
            question.topic = measurements_topic
            question.save()
        question.level.topics.add(measurements_topic)
        
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
    print(f"\n[OK] All questions are associated with Measurements topic for Year 5")

if __name__ == "__main__":
    print("[INFO] Setting up Measurements topic for Year 5...\n")
    result = setup_measurements_topic()
    
    if result:
        measurements_topic, level_5 = result
        print("\n" + "="*60)
        add_measurements_questions(measurements_topic, level_5)
        print("\n[OK] Done!")

