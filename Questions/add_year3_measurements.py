#!/usr/bin/env python
"""
Add/Update "Measurements" questions for Year 3
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
    """Create Measurements topic and associate with Year 3"""
    
    # Get or create the "Measurements" topic
    # Handle case where multiple topics with same name exist
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
        print(f"[OK] Created topic: Measurements")
    else:
        print(f"[INFO] Topic already exists: Measurements")
    
    # Get Year 3 level
    level_3 = Level.objects.filter(level_number=3).first()
    
    if not level_3:
        print("[ERROR] Year 3 level not found!")
        return None
    
    print(f"[INFO] Found Year 3: {level_3}")
    
    # Check if Measurements is already associated
    if level_3.topics.filter(name="Measurements").exists():
        print("[INFO] Year 3 already has Measurements topic associated.")
        print(f"   Current topics for Year 3: {', '.join([t.name for t in level_3.topics.all()])}")
    else:
        # Associate Measurements topic with Year 3
        level_3.topics.add(measurements_topic)
        print(f"[OK] Successfully associated Measurements topic with Year 3")
        print(f"   Year 3 now has topics: {', '.join([t.name for t in level_3.topics.all()])}")
    
    return measurements_topic, level_3

def add_measurements_questions(measurements_topic, level_3):
    """Add/Update Measurements questions for Year 3"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Which unit would you use to measure the weight of an apple?",
            "question_type": "multiple_choice",
            "correct_answer": "grams",
            "wrong_answers": ["kilometres", "litres", "centimetres"],
            "explanation": "An apple is light, so we use grams to measure its weight.",
        },
        {
            "question_text": "A box is 40 cm long, 20 cm wide, and 30 cm tall. What is the approximate height?",
            "question_type": "multiple_choice",
            "correct_answer": "30 cm",
            "wrong_answers": ["20 cm", "40 cm", "50 cm"],
            "explanation": "The height is given as 30 cm in the question.",
        },
        {
            "question_text": "Read the ruler. What is the length at point A?",
            "question_type": "multiple_choice",
            "correct_answer": "0 cm",
            "wrong_answers": ["5 cm", "0.5 cm", "10 cm"],
            "explanation": "Point A is at the 0.5 cm mark on the ruler.",
            "image_path": "questions/year3/measurements/image_ruler.png",
        },
        {
            "question_text": "Read the ruler. What is the length at point B?",
            "question_type": "multiple_choice",
            "correct_answer": "2 cm",
            "wrong_answers": ["2.5 cm", "1.8 cm", "3 cm"],
            "explanation": "Point B is at the 1.8 cm mark on the ruler.",
            "image_path": "questions/year3/measurements/image_ruler.png",
        },
        {
            "question_text": "Read the ruler. What is the length at point C?",
            "question_type": "multiple_choice",
            "correct_answer": "5.5 cm",
            "wrong_answers": ["5 cm", "6 cm", "5.7 cm"],
            "explanation": "Point C is at the 5.7 cm mark on the ruler.",
            "image_path": "questions/year3/measurements/image_ruler.png",
        },
        {
            "question_text": "Read the ruler. What is the length at point D?",
            "question_type": "multiple_choice",
            "correct_answer": "10.2 cm",
            "wrong_answers": ["10 cm", "10.5 cm", "11 cm"],
            "explanation": "Point D is at the 10.5 cm mark on the ruler.",
            "image_path": "questions/year3/measurements/image_ruler.png",
        },
        {
            "question_text": "Read the ruler. What is the length at point E?",
            "question_type": "multiple_choice",
            "correct_answer": "14.7 cm",
            "wrong_answers": ["14 cm", "15 cm", "14.5 cm"],
            "explanation": "Point E is at the 14.7 cm mark on the ruler.",
            "image_path": "questions/year3/measurements/image_ruler.png",
        },
        {
            "question_text": "How many centimetres are in half a metre?",
            "question_type": "multiple_choice",
            "correct_answer": "50 cm",
            "wrong_answers": ["25 cm", "75 cm", "100 cm"],
            "explanation": "Half a metre is 0.5 m, which equals 50 cm.",
        },
        {
            "question_text": "If you have a ribbon that is 1 metre long and you cut 30 cm off, how much is left?",
            "question_type": "multiple_choice",
            "correct_answer": "70 cm",
            "wrong_answers": ["60 cm", "80 cm", "90 cm"],
            "explanation": "1 metre = 100 cm. After cutting 30 cm: 100 - 30 = 70 cm.",
        },
        {
            "question_text": "Which is the heaviest?\n\nA) A feather\nB) A book\nC) A car\nD) A ball",
            "question_type": "multiple_choice",
            "correct_answer": "A car",
            "wrong_answers": ["A feather", "A book", "A ball"],
            "explanation": "A car is the heaviest object among the options.",
        },
        {
            "question_text": "A water bottle holds 500 ml. How many millilitres are in 1 litre?",
            "question_type": "multiple_choice",
            "correct_answer": "1000 ml",
            "wrong_answers": ["500 ml", "1500 ml", "2000 ml"],
            "explanation": "1 litre equals 1000 millilitres.",
        },
        {
            "question_text": "Estimate: How tall is a typical 8-year-old child?",
            "question_type": "multiple_choice",
            "correct_answer": "About 130 cm",
            "wrong_answers": ["About 50 cm", "About 90 cm", "About 200 cm"],
            "explanation": "A typical 8-year-old child is approximately 130 cm tall.",
        },
        {
            "question_text": "Which holds the most water?\n\nA) A teaspoon (5 ml)\nB) A glass (250 ml)\nC) A jug (1000 ml)\nD) A bucket (10 litres)",
            "question_type": "multiple_choice",
            "correct_answer": "A bucket (10 litres)",
            "wrong_answers": ["A teaspoon (5 ml)", "A glass (250 ml)", "A jug (1000 ml)"],
            "explanation": "A bucket holding 10 litres (10,000 ml) holds the most water.",
        },
        {
            "question_text": "Which is the lightest?\n\nA) An elephant\nB) A dog\nC) A pencil\nD) A car",
            "question_type": "multiple_choice",
            "correct_answer": "A pencil",
            "wrong_answers": ["An elephant", "A dog", "A car"],
            "explanation": "A pencil is the lightest object among the options.",
        },
        {
            "question_text": "How many millimetres are in 5 centimetres?",
            "question_type": "multiple_choice",
            "correct_answer": "50 mm",
            "wrong_answers": ["5 mm", "25 mm", "500 mm"],
            "explanation": "1 cm = 10 mm, so 5 cm = 5 × 10 = 50 mm.",
        },
        {
            "question_text": "Estimate: How long would it take to walk 1 kilometre?\n\nA) 10 minutes\nB) 15 minutes\nC) 30 minutes\nD) 1 hour",
            "question_type": "multiple_choice",
            "correct_answer": "15 minutes",
            "wrong_answers": ["10 minutes", "30 minutes", "1 hour"],
            "explanation": "It typically takes about 15 minutes to walk 1 kilometre at a normal walking pace.",
        },
        {
            "question_text": "Convert 1m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "100 cm",
            "wrong_answers": ["10 cm", "1000 cm", "50 cm"],
            "explanation": "1 metre = 100 centimetres.",
        },
        {
            "question_text": "Convert 2.5m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "250 cm",
            "wrong_answers": ["25 cm", "200 cm", "2000 cm"],
            "explanation": "2.5 metres = 2.5 × 100 = 250 centimetres.",
        },
        {
            "question_text": "Convert 0.5m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "50 cm",
            "wrong_answers": ["5 cm", "500 cm", "55 cm"],
            "explanation": "0.5 metres = 0.5 × 100 = 50 centimetres.",
        },
        {
            "question_text": "Convert 3m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "300 cm",
            "wrong_answers": ["30 cm", "3000 cm", "400 cm"],
            "explanation": "3 metres = 3 × 100 = 300 centimetres.",
        },
        {
            "question_text": "Convert 1.5m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "150 cm",
            "wrong_answers": ["15 cm", "100 cm", "50 cm"],
            "explanation": "1.5 metres = 1.5 × 100 = 150 centimetres.",
        },
        {
            "question_text": "Convert 4m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "400 cm",
            "wrong_answers": ["40 cm", "4000 cm", "300 cm"],
            "explanation": "4 metres = 4 × 100 = 400 centimetres.",
        },
        {
            "question_text": "Convert 0.75m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "75 cm",
            "wrong_answers": ["7.5 cm", "700 cm", "80 cm"],
            "explanation": "0.75 metres = 0.75 × 100 = 75 centimetres.",
        },
        {
            "question_text": "Convert 2m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "200 cm",
            "wrong_answers": ["20 cm", "100 cm", "300 cm"],
            "explanation": "2 metres = 2 × 100 = 200 centimetres.",
        },
        {
            "question_text": "Convert 5m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "500 cm",
            "wrong_answers": ["50 cm", "5000 cm", "400 cm"],
            "explanation": "5 metres = 5 × 100 = 500 centimetres.",
        },
        {
            "question_text": "Convert 0.25m to cm",
            "question_type": "multiple_choice",
            "correct_answer": "25 cm",
            "wrong_answers": ["2.5 cm", "20 cm", "30 cm"],
            "explanation": "0.25 metres = 0.25 × 100 = 25 centimetres.",
        },
    ]
    
    print(f"\n[INFO] Processing {len(questions_data)} Measurements questions for Year 3...\n")
    
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
                level=level_3,
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
    print(f"\n[OK] All questions are associated with Measurements topic for Year 3")

if __name__ == "__main__":
    print("[INFO] Setting up Measurements topic for Year 3...\n")
    result = setup_measurements_topic()
    
    if result:
        measurements_topic, level_3 = result
        print("\n" + "="*60)
        add_measurements_questions(measurements_topic, level_3)
        print("\n[OK] Done!")

