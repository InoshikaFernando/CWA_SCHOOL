#!/usr/bin/env python
"""
Add/Update "Measurements" questions for Year 6
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

def setup_measurements_topic():
    """Create Measurements topic and associate with Year 6"""
    
    # Get or create the "Measurements" topic
    measurements_topic, created = Topic.objects.get_or_create(name="Measurements")
    if created:
        print(f"[OK] Created topic: Measurements")
    else:
        print(f"[INFO] Topic already exists: Measurements")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return None
    
    print(f"[INFO] Found Year 6: {level_6}")
    
    # Check if Measurements is already associated
    if level_6.topics.filter(name="Measurements").exists():
        print("[INFO] Year 6 already has Measurements topic associated.")
        print(f"   Current topics for Year 6: {', '.join([t.name for t in level_6.topics.all()])}")
    else:
        # Associate Measurements topic with Year 6
        level_6.topics.add(measurements_topic)
        print(f"[OK] Successfully associated Measurements topic with Year 6")
        print(f"   Year 6 now has topics: {', '.join([t.name for t in level_6.topics.all()])}")
    
    return measurements_topic, level_6

def add_measurements_questions(measurements_topic, level_6):
    """Add/Update Measurements questions for Year 6"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Which metric unit would be most appropriate for measuring the height of a classroom?",
            "question_type": "multiple_choice",
            "correct_answer": "meters",
            "wrong_answers": ["centimeters", "kilometers", "millimeters", "decimeters"],
            "explanation": "The height of a classroom is typically a few meters tall, so meters is the most appropriate unit.",
        },
        {
            "question_text": "Which metric unit would be most appropriate for measuring the length of a pencil?",
            "question_type": "multiple_choice",
            "correct_answer": "centimeters",
            "wrong_answers": ["meters", "kilometers", "millimeters", "decimeters"],
            "explanation": "A pencil is about 15-18 cm long, so centimeters is the most appropriate unit.",
        },
        {
            "question_text": "Which metric unit would be most appropriate for measuring the width of a fingernail?",
            "question_type": "multiple_choice",
            "correct_answer": "millimeters",
            "wrong_answers": ["centimeters", "meters", "kilometers", "decimeters"],
            "explanation": "A fingernail is about 1 cm wide, so millimeters would give the most precise measurement.",
        },
        {
            "question_text": "Which metric unit would be most appropriate for measuring the length of a ruler?",
            "question_type": "multiple_choice",
            "correct_answer": "centimeters",
            "wrong_answers": ["meters", "kilometers", "millimeters", "decimeters"],
            "explanation": "A ruler is 30 cm long, so centimeters is the appropriate unit.",
        },
        {
            "question_text": "Convert 5 meters to centimeters.",
            "question_type": "multiple_choice",
            "correct_answer": "500 cm",
            "wrong_answers": ["5 cm", "50 cm", "5000 cm", "50000 cm"],
            "explanation": "1 meter = 100 centimeters, so 5 meters = 5 × 100 = 500 cm",
        },
        {
            "question_text": "Convert 86000 centimeters to kilometers.",
            "question_type": "multiple_choice",
            "correct_answer": "0.86 km",
            "wrong_answers": ["86 km", "8.6 km", "860 km", "0.086 km"],
            "explanation": "1 km = 100000 cm, so 86000 cm ÷ 100000 = 0.86 km",
        },
        {
            "question_text": "Convert 6.5 meters to millimeters.",
            "question_type": "multiple_choice",
            "correct_answer": "6500 mm",
            "wrong_answers": ["65 mm", "650 mm", "65000 mm", "650000 mm"],
            "explanation": "1 meter = 1000 millimeters, so 6.5 meters = 6.5 × 1000 = 6500 mm",
        },
        {
            "question_text": "Convert 600000 millimeters to kilometers.",
            "question_type": "multiple_choice",
            "correct_answer": "0.6 km",
            "wrong_answers": ["60 km", "6 km", "600 km", "0.06 km"],
            "explanation": "1 km = 1000000 mm, so 600000 mm ÷ 1000000 = 0.6 km",
        },
        {
            "question_text": "Convert 3 kilometers to meters.",
            "question_type": "multiple_choice",
            "correct_answer": "3000 m",
            "wrong_answers": ["30 m", "300 m", "30000 m", "0.3 m"],
            "explanation": "1 kilometer = 1000 meters, so 3 kilometers = 3 × 1000 = 3000 m",
        },
        {
            "question_text": "Convert 450 centimeters to meters.",
            "question_type": "multiple_choice",
            "correct_answer": "4.5 m",
            "wrong_answers": ["45 m", "0.45 m", "4500 m", "45000 m"],
            "explanation": "1 meter = 100 centimeters, so 450 cm ÷ 100 = 4.5 m",
        },
        {
            "question_text": "Convert 2.8 kilometers to meters.",
            "question_type": "multiple_choice",
            "correct_answer": "2800 m",
            "wrong_answers": ["28 m", "280 m", "28000 m", "0.28 m"],
            "explanation": "1 km = 1000 m, so 2.8 km = 2.8 × 1000 = 2800 m",
        },
        {
            "question_text": "Convert 7500 millimeters to centimeters.",
            "question_type": "multiple_choice",
            "correct_answer": "750 cm",
            "wrong_answers": ["75 cm", "7.5 cm", "7500 cm", "75000 cm"],
            "explanation": "1 cm = 10 mm, so 7500 mm ÷ 10 = 750 cm",
        },
        {
            "question_text": "Convert 9.3 centimeters to millimeters.",
            "question_type": "multiple_choice",
            "correct_answer": "93 mm",
            "wrong_answers": ["9.3 mm", "930 mm", "9300 mm", "0.93 mm"],
            "explanation": "1 cm = 10 mm, so 9.3 cm × 10 = 93 mm",
        },
        {
            "question_text": "Convert 1.5 meters to millimeters.",
            "question_type": "multiple_choice",
            "correct_answer": "1500 mm",
            "wrong_answers": ["15 mm", "150 mm", "15000 mm", "0.15 mm"],
            "explanation": "1 m = 1000 mm, so 1.5 m = 1.5 × 1000 = 1500 mm",
        },
        {
            "question_text": "Read the scale on this ruler to measure the marked length.",
            "question_type": "multiple_choice",
            "correct_answer": "2.7 cm",
            "wrong_answers": ["2.6 cm", "2.8 cm", "2.5 cm", "3.0 cm"],
            "explanation": "The arrow starts at 0 cm and ends at the 7th millimeter mark after 2 cm, which is 2.7 cm.",
            "image_path": "questions/year6/measurements/image1.png",
        },
        {
            "question_text": "Read the scales on this ruler to measure the marked length.",
            "question_type": "multiple_choice",
            "correct_answer": "1.5 m",
            "wrong_answers": ["1.4 m", "1.6 m", "2.0 m", "1.0 m"],
            "explanation": "The arrow starts at 5.5 m and ends at 7 m, so the length is 7 - 5.5 = 1.5 m.",
            "image_path": "questions/year6/measurements/image2.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "25.6 cm",  
            "wrong_answers": ["25.7 cm", "24.6 cm", "26.6 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image3.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "38.1 cm", 
            "wrong_answers": ["38.2 cm", "37.1 cm", "39.1 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image4.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "42 cm",  
            "wrong_answers": ["43 cm", "41 cm", "44 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image5.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "28.2 cm",  
            "wrong_answers": ["28.3 cm", "28.1 cm", "28.4 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image6.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "16.07 cm",  
            "wrong_answers": ["7.07 cm", "28.29 cm", "14.14 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image11.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "356.29 mm",  
            "wrong_answers": ["540.57 mm", "270.29 mm", "313.29 mm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image12.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "short_answer",
            "correct_answer": "45.43 m",  
            "wrong_answers": ["62.86 m", "31.43 m", "37.43 m"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image13.png",
        },
    ]
    
    print(f"\n[INFO] Processing {len(questions_data)} Measurements questions for Year 6...\n")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by exact text match and image if provided)
        query = Question.objects.filter(
            level=level_6,
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
                question.save()
                question_updated = True
            
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
            
            # For short answer: check if correct answer exists and matches
            elif q_data["question_type"] == "short_answer":
                correct_answer_text = q_data.get("correct_answer", "").strip()
                
                if correct_answer_text:
                    # Only update if answer is provided and different
                    if not existing_correct or existing_correct.answer_text != correct_answer_text:
                        # Delete old answers and create new one
                        Answer.objects.filter(question=question).delete()
                        question_updated = True
                else:
                    # No answer provided in data, skip updating answers
                    if existing_answers.exists():
                        print(f"  [SKIP] Question {i}: Already has answers, skipping answer update (no answer in data)")
                        skipped_count += 1
                        continue
            
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
                level=level_6,
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
        
        # Associate with Measurements topic
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
            
            elif q_data["question_type"] == "short_answer":
                correct_answer_text = q_data.get("correct_answer", "").strip()
                
                if correct_answer_text:
                    Answer.objects.create(
                        question=question,
                        answer_text=correct_answer_text,
                        is_correct=True,
                        order=0
                    )
                    print(f"      [ANSWERS] Created answer: {correct_answer_text}")
                else:
                    print(f"      [WARNING] No answer provided for short_answer question")
    
    print(f"\n[SUMMARY]")
    print(f"   [CREATE] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"   [SKIP] Skipped: {skipped_count} questions")
    print(f"\n[OK] All questions are associated with Measurements topic for Year 6")

if __name__ == "__main__":
    print("[INFO] Setting up Measurements topic for Year 6...\n")
    result = setup_measurements_topic()
    
    if result:
        measurements_topic, level_6 = result
        print("\n" + "="*60)
        add_measurements_questions(measurements_topic, level_6)
        print("\n[OK] Done!")

