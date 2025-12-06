#!/usr/bin/env python
"""
Add/Update "Measurements" questions for Year 2
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
    """Create Measurements topic and associate with Year 2"""
    
    # Get or create the "Measurements" topic
    # Handle case where multiple topics with same name exist
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
        print(f"[OK] Created topic: Measurements")
    else:
        print(f"[INFO] Topic already exists: Measurements")
    
    # Get Year 2 level
    level_2 = Level.objects.filter(level_number=2).first()
    
    if not level_2:
        print("[ERROR] Year 2 level not found!")
        return None
    
    print(f"[INFO] Found Year 2: {level_2}")
    
    # Check if Measurements is already associated
    if level_2.topics.filter(name="Measurements").exists():
        print("[INFO] Year 2 already has Measurements topic associated.")
        print(f"   Current topics for Year 2: {', '.join([t.name for t in level_2.topics.all()])}")
    else:
        # Associate Measurements topic with Year 2
        level_2.topics.add(measurements_topic)
        print(f"[OK] Successfully associated Measurements topic with Year 2")
        print(f"   Year 2 now has topics: {', '.join([t.name for t in level_2.topics.all()])}")
    
    return measurements_topic, level_2

def add_measurements_questions(measurements_topic, level_2):
    """Add/Update Measurements questions for Year 2"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "What is the length of the pencil?\n\n[Choose the best estimate]",
            "question_type": "multiple_choice",
            "correct_answer": "About 15 cm",
            "wrong_answers": ["About 5 cm", "About 30 cm", "About 50 cm"],
            "explanation": "A typical pencil is about 15-18 cm long.",
        },
        {
            "question_text": "What would you use to measure the length of your desk?\n\nA) A ruler\nB) A thermometer\nC) A clock\nD) A scale",
            "question_type": "multiple_choice",
            "correct_answer": "A ruler",
            "wrong_answers": ["A thermometer", "A clock", "A scale"],
            "explanation": "A ruler is used to measure length.",
        },
        {
            "question_text": "Which measurement would you use to measure how tall your friend is?\n\nA) cm\nB) m\nC) g\nD) kg",
            "question_type": "multiple_choice",
            "correct_answer": "m",
            "wrong_answers": ["l", "g", "kg"],
            "explanation": "We measure height in meters (m) or centimeters (cm). For a person's height, meters is more appropriate.",
        },
        {
            "question_text": "A rope is 10 metres long. Another rope is 15 metres long. What is the total length?",
            "question_type": "multiple_choice",
            "correct_answer": "25 metres",
            "wrong_answers": ["20 metres", "30 metres", "35 metres"],
            "explanation": "To find the total, add: 10 + 15 = 25 metres.",
        },
        {
            "question_text": "Which unit would you use to measure the length of a pencil?",
            "question_type": "multiple_choice",
            "correct_answer": "centimeters",
            "wrong_answers": ["meters", "kilometers", "liters"],
            "explanation": "A pencil is small, so we use centimeters to measure it.",
        },
        {
            "question_text": "Which unit would you use to measure the weight of an apple?",
            "question_type": "multiple_choice",
            "correct_answer": "grams",
            "wrong_answers": ["kilograms", "meters", "liters"],
            "explanation": "An apple is light, so we use grams to measure its weight.",
        },
        {
            "question_text": "Which unit would you use to measure the capacity of a water bottle?",
            "question_type": "multiple_choice",
            "correct_answer": "liters",
            "wrong_answers": ["kilograms", "meters", "grams"],
            "explanation": "We use liters to measure how much liquid a container can hold.",
        },
        {
            "question_text": "Which unit would you use to measure how tall you are?",
            "question_type": "multiple_choice",
            "correct_answer": "centimeters",
            "wrong_answers": ["kilograms", "liters", "kilometers"],
            "explanation": "We measure height in centimeters or meters.",
        },
        {
            "question_text": "Which unit would you use to measure the weight of a toy car?",
            "question_type": "multiple_choice",
            "correct_answer": "grams",
            "wrong_answers": ["liters", "meters", "kilometers"],
            "explanation": "A toy car is light, so we use grams to measure its weight.",
        },
        {
            "question_text": "Which unit would you use to measure the length of your bed?",
            "question_type": "multiple_choice",
            "correct_answer": "meters",
            "wrong_answers": ["grams", "liters", "centimeters"],
            "explanation": "A bed is big, so we use meters to measure its length.",
        },
        {
            "question_text": "Which is the shortest?\n\nA) Your finger\nB) A spoon\nC) A book\nD) A door",
            "question_type": "multiple_choice",
            "correct_answer": "Your finger",
            "wrong_answers": ["A spoon", "A book", "A door"],
            "explanation": "Your finger is the shortest object among the options.",
        },
        {
            "question_text": "How many centimetres are in 1 metre?",
            "question_type": "multiple_choice",
            "correct_answer": "100 cm",
            "wrong_answers": ["10 cm", "50 cm", "1000 cm"],
            "explanation": "1 metre equals 100 centimetres.",
        },
        {
            "question_text": "If a pencil is 12 cm long and you cut off 4 cm, how much is left?",
            "question_type": "multiple_choice",
            "correct_answer": "8 cm",
            "wrong_answers": ["4 cm", "6 cm", "16 cm"],
            "explanation": "Subtract 4 cm from 12 cm: 12 - 4 = 8 cm.",
        },
        {
            "question_text": "Which would be about 1 metre long?\n\nA) Your thumb\nB) A book\nC) Your arm span\nD) A car",
            "question_type": "multiple_choice",
            "correct_answer": "Your arm span",
            "wrong_answers": ["Your thumb", "A book", "A car"],
            "explanation": "Your arm span (the distance from fingertip to fingertip with arms outstretched) is approximately 1 metre for most people.",
        },
        {
            "question_text": "What is the longest?\n\nA) A paperclip (3 cm)\nB) A pencil (15 cm)\nC) A pen (12 cm)\nD) A straw (20 cm)",
            "question_type": "multiple_choice",
            "correct_answer": "A straw (20 cm)",
            "wrong_answers": ["A paperclip (3 cm)", "A pencil (15 cm)", "A pen (12 cm)"],
            "explanation": "A straw at 20 cm is the longest among the options.",
        },
        {
            "question_text": "Estimate: How long is a typical toothbrush?\n\nA) 10 cm\nB) 20 cm\nC) 30 cm\nD) 40 cm",
            "question_type": "multiple_choice",
            "correct_answer": "20 cm",
            "wrong_answers": ["10 cm", "30 cm", "40 cm"],
            "explanation": "A typical toothbrush is approximately 20 cm long.",
        },
    ]
    
    # Use shared utility function to process questions
    results = process_questions(
        level=level_2,
        topic=measurements_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n[OK] All questions are associated with Measurements topic for Year 2")
    
    # Legacy code below - kept for reference but not used
    """
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by exact text match)
        existing = Question.objects.filter(
            level=level_2,
            question_text=q_data["question_text"]
        ).first()
        
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
                level=level_2,
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
    """

if __name__ == "__main__":
    print("[INFO] Setting up Measurements topic for Year 2...\n")
    result = setup_measurements_topic()
    
    if result:
        measurements_topic, level_2 = result
        print("\n" + "="*60)
        add_measurements_questions(measurements_topic, level_2)
        print("\n[OK] Done!")

