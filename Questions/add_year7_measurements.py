#!/usr/bin/env python
"""
Add/Update "Measurements" questions for Year 7
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

def setup_measurements_topic():
    """Create Measurements topic and associate with Year 7"""
    
    # Get or create the "Measurements" topic
    # Handle case where multiple topics with same name exist
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
        print(f"[OK] Created topic: Measurements")
    else:
        print(f"[INFO] Topic already exists: Measurements")
    
    # Get Year 7 level
    level_7 = Level.objects.filter(level_number=7).first()
    
    if not level_7:
        print("[ERROR] Year 7 level not found!")
        return None
    
    print(f"[INFO] Found Year 7: {level_7}")
    
    # Check if Measurements is already associated
    if level_7.topics.filter(name="Measurements").exists():
        print("[INFO] Year 7 already has Measurements topic associated.")
        print(f"   Current topics for Year 7: {', '.join([t.name for t in level_7.topics.all()])}")
    else:
        # Associate Measurements topic with Year 7
        level_7.topics.add(measurements_topic)
        print(f"[OK] Successfully associated Measurements topic with Year 7")
        print(f"   Year 7 now has topics: {', '.join([t.name for t in level_7.topics.all()])}")
    
    return measurements_topic, level_7

def add_measurements_questions(measurements_topic, level_7):
    """Add/Update Measurements questions for Year 7"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match and image if provided
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Which is longer and by how many millimetres: 1.24 m or 1458 mm?",
            "question_type": "multiple_choice",
            "correct_answer": "1458 mm by 218 mm",
            "wrong_answers": ["1.24 m by 218 mm", "1458 mm by 120 mm", "1.24 m by 200 mm"],
            "explanation": "Convert 1.24 m to mm: 1.24 × 1000 = 1240 mm. Compare: 1458 mm - 1240 mm = 218 mm. So 1458 mm is longer by 218 mm.",
        },
        {
            "question_text": "Find the circumference of this circle.",
            "question_type": "multiple_choice",
            "correct_answer": "About 44 cm",
            "wrong_answers": ["About 28 cm", "About 88 cm", "About 14 cm"],
            "explanation": "Circumference = π × diameter = π × 14 ≈ 43.98 cm ≈ 44 cm.",
            "image_path": "questions/year6/measurements/image7.png",
        },
        {
            "question_text": "Find the circumference of this circle.",
            "question_type": "multiple_choice",
            "correct_answer": "About 44 cm",
            "wrong_answers": ["About 28 cm", "About 88 cm", "About 14 cm"],
            "explanation": "Circumference = π × diameter = π × 14 ≈ 43.98 cm ≈ 44 cm.",
            "image_path": "questions/year6/measurements/image7.png",
        },
        {
            "question_text": "Find the circumference of this circle.",
            "question_type": "multiple_choice",
            "correct_answer": "About 69 mm",
            "wrong_answers": ["About 44 mm", "About 22 mm", "About 90 mm"],
            "explanation": "Circumference = π × diameter = π × 22 mm ≈ 69.12 mm.",
            "image_path": "questions/year6/measurements/image8.png",
        },
        {
            "question_text": "Find the circumference of this circle.",
            "question_type": "multiple_choice",
            "correct_answer": "About 38 cm",
            "wrong_answers": ["About 24 cm", "About 12 cm", "About 44 cm"],
            "explanation": "Radius = 6 cm, diameter = 12 cm. Circumference = π × d ≈ 3.14 × 12 = 37.68 cm ≈ 38 cm.",
            "image_path": "questions/year6/measurements/image9.png",
        },
        {
            "question_text": "Find the circumference of this circle.",
            "question_type": "multiple_choice",
            "correct_answer": "About 94 cm",
            "wrong_answers": ["About 45 cm", "About 30 cm", "About 75 cm"],
            "explanation": "Radius = 15 cm, circumference = 2πr ≈ 2 × 3.14 × 15 = 94.2 cm ≈ 94 cm.",
            "image_path": "questions/year6/measurements/image10.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image5.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image6.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image7.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image8.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image9.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image10.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image11.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image12.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image13.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image14.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image15.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image16.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image17.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image18.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image19.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image20.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image21.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "short_answer",
            "correct_answer": "",  # No answer provided in database
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Calculate the area using the appropriate formula for the shape.",
            "image_path": "questions/year6/measurements/image22.png",
        },
        {
            "question_text": "What is the volume of the spacecraft? (use π = 22/7)",
            "question_type": "short_answer",
            "correct_answer": "4 x 22 x 7 x 7 m3",
            "wrong_answers": [],  # Not used for short_answer
            "explanation": "Volume for the corn is 1/3πR²h and volume of cylinder is πR²h",
            "image_path": "questions/image23.png",
        },
        {
            "question_text": "Which metric unit would be most appropriate for measuring the distance around the school?",
            "question_type": "multiple_choice",
            "correct_answer": "kilometers",
            "wrong_answers": ["meters", "centimeters", "millimeters", "hectometers"],
            "explanation": "The distance around a school perimeter is typically measured in kilometers.",
        },
        {
            "question_text": "Which metric unit would be most appropriate for measuring the distance between two cities?",
            "question_type": "multiple_choice",
            "correct_answer": "kilometers",
            "wrong_answers": ["meters", "centimeters", "millimeters", "decimeters"],
            "explanation": "Distances between cities are measured in kilometers.",
        },
    ]
    
    # Use shared utility function to process questions
    from question_utils import process_questions
    
    results = process_questions(
        level=level_7,
        topic=measurements_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n[OK] All questions are associated with Measurements topic for Year 7")
    
    # Legacy code below - kept for reference but not used
    """
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by exact text match AND image if provided)
        # For questions with images, we need BOTH text and image to match
        existing = None
        
        if "image_path" in q_data and q_data["image_path"]:
            image_name = os.path.basename(q_data["image_path"])
            # Must match both question_text AND image
            query = Question.objects.filter(
                level=level_7,
                question_text=q_data["question_text"]
            )
            
            # Try to find by exact image path first
            existing = query.filter(image=q_data["image_path"]).first()
            if not existing:
                # Fallback: match by image filename (handles different path formats)
                for q in query:
                    if q.image:
                        q_image_name = os.path.basename(q.image.name)
                        # Remove Django suffix if present (e.g., image5_abc123.png -> image5.png)
                        if '_' in q_image_name:
                            q_image_base = q_image_name.split('_')[0] + os.path.splitext(q_image_name)[1]
                        else:
                            q_image_base = q_image_name
                        
                        if image_name == q_image_base or image_name in q.image.name or q.image.name.endswith(image_name):
                            existing = q
                            break
        else:
            # No image: match by question_text only (but only if no image questions exist with same text)
            query = Question.objects.filter(
                level=level_7,
                question_text=q_data["question_text"]
            )
            # Only match if the existing question also has no image
            existing = query.filter(image__isnull=True).first() or (query.first() if query.count() == 1 else None)
        
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
                level=level_7,
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
        
        # Set image path to reference Year 6 images (don't copy, just use the path)
        if "image_path" in q_data and q_data["image_path"]:
            image_path = q_data["image_path"]
            # Just set the image path directly without copying the file
            # This references the Year 6 image path
            question.image.name = image_path
            question.save()
            print(f"      [IMAGE] Set image path to Year 6: {image_path}")
        
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
    """

if __name__ == "__main__":
    print("[INFO] Setting up Measurements topic for Year 7...\n")
    result = setup_measurements_topic()

    if result:
        measurements_topic, level_7 = result
        print("\n" + "="*60)
        add_measurements_questions(measurements_topic, level_7)
        print("\n[OK] Done!")
