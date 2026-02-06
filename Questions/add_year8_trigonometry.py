#!/usr/bin/env python
"""
Add/Update "Trigonometry" questions for Year 8
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

def setup_trigonometry_topic():
    """Create Trigonometry topic and associate with Year 8"""
    
    # Get or create the "Trigonometry" topic
    # Handle case where multiple topics with same name exist
    trigonometry_topic = Topic.objects.filter(name="Trigonometry").first()
    if not trigonometry_topic:
        trigonometry_topic = Topic.objects.create(name="Trigonometry")
        print(f"[OK] Created topic: Trigonometry")
    else:
        print(f"[INFO] Topic already exists: Trigonometry")
    
    # Get Year 8 level
    level_8 = Level.objects.filter(level_number=8).first()
    
    if not level_8:
        print("[ERROR] Year 8 level not found!")
        return None
    
    print(f"[INFO] Found Year 8: {level_8}")
    
    # Check if Trigonometry is already associated
    if level_8.topics.filter(name="Trigonometry").exists():
        print("[INFO] Year 8 already has Trigonometry topic associated.")
        print(f"   Current topics for Year 8: {', '.join([t.name for t in level_8.topics.all()])}")
    else:
        # Associate Trigonometry topic with Year 8
        level_8.topics.add(trigonometry_topic)
        print(f"[OK] Successfully associated Trigonometry topic with Year 8")
        print(f"   Year 8 now has topics: {', '.join([t.name for t in level_8.topics.all()])}")
    
    return trigonometry_topic, level_8

def add_trigonometry_questions(trigonometry_topic, level_8):
    """Add/Update Trigonometry questions for Year 8"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    # 
    # Format for each question:
    # {
    #     "question_text": "Your question here",
    #     "correct_answer": "The correct answer",
    #     "wrong_answers": ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
    #     "explanation": "Explanation of the correct answer"
    # }
    
    questions_data = [
        {
            "question_text": "In a right-angled triangle, the trigonometric ratio for opposite divided by hypotenuse is called:",
            "correct_answer": "sine",
            "wrong_answers": ["cosine", "tangent", "cotangent"],
            "explanation": "The sine ratio is defined as opposite/hypotenuse. This is part of SOHCAHTOA: Sine = Opposite/Hypotenuse."
        },
        {
            "question_text": "What does the acronym SOHCAHTOA stand for in trigonometry?",
            "correct_answer": "Sine = Opposite/Hypotenuse, Cosine = Adjacent/Hypotenuse, Tangent = Opposite/Adjacent",
            "wrong_answers": ["Sine = Other/Hypotenuse, Cosine = Adjacent/Height, Tangent = Opposite/Adjacent", "Sine = Opposite/Height, Cosine = Adjacent/Hypotenuse, Tangent = Other/Adjacent", "Sine = Side/Hypotenuse, Cosine = Angle/Hypotenuse, Tangent = Opposite/Angle"],
            "explanation": "SOHCAHTOA is a mnemonic for remembering the three basic trigonometric ratios in a right-angled triangle."
        },
        {
            "question_text": "In a right-angled triangle, the cosine ratio is:",
            "correct_answer": "adjacent/hypotenuse",
            "wrong_answers": ["opposite/hypotenuse", "opposite/adjacent", "hypotenuse/adjacent"],
            "explanation": "Cosine is defined as the ratio of the adjacent side to the hypotenuse (COH in SOHCAHTOA)."
        },
        {
            "question_text": "The tangent of an angle in a right-angled triangle is:",
            "correct_answer": "opposite/adjacent",
            "wrong_answers": ["opposite/hypotenuse", "adjacent/hypotenuse", "hypotenuse/opposite"],
            "explanation": "Tangent is defined as the ratio of the opposite side to the adjacent side (TOA in SOHCAHTOA)."
        },
        {
            "question_text": "What is the approximate value of sin(30°)?",
            "correct_answer": "0.5",
            "wrong_answers": ["0.866", "0.707", "0.577"],
            "explanation": "The sine of 30 degrees is 0.5 (or 1/2). This is one of the standard trigonometric values."
        },
        {
            "question_text": "What is the approximate value of cos(60°)?",
            "correct_answer": "0.5",
            "wrong_answers": ["0.866", "0.707", "0.577"],
            "explanation": "The cosine of 60 degrees is 0.5 (or 1/2). This is one of the standard trigonometric values."
        },
        {
            "question_text": "What is the approximate value of sin(45°)?",
            "correct_answer": "0.707",
            "wrong_answers": ["0.5", "0.866", "0.866"],
            "explanation": "The sine of 45 degrees is approximately 0.707 (or √2/2). This is one of the standard trigonometric values."
        },
        {
            "question_text": "What is the approximate value of cos(45°)?",
            "correct_answer": "0.707",
            "wrong_answers": ["0.5", "0.866", "0.577"],
            "explanation": "The cosine of 45 degrees is approximately 0.707 (or √2/2). This is one of the standard trigonometric values."
        },
        {
            "question_text": "What is the approximate value of tan(45°)?",
            "correct_answer": "1",
            "wrong_answers": ["0.707", "0.866", "0.577"],
            "explanation": "The tangent of 45 degrees is exactly 1. This is because at 45 degrees, the opposite and adjacent sides are equal."
        },
        {
            "question_text": "Find the value of X in these right-angled triangles, correct to two decimal places (cos(38°) = 0.7880)",
            "correct_answer": "X = 11.03 m",
            "wrong_answers": ["X = 10 m", "X = 12.5 m", "X = 9.5 m"],
            "explanation": "cos(38°) = adjacent/hypotenuse = X/14 ≈ 11.03 m.",
            "image_path": "questions/year8/trigonometry/image1.png",
        },
        {
            "question_text": "Find the value of X in these right-angled triangles, correct to two decimal places (tan(38°) = 2.6051)",
            "correct_answer": "X = 61.88 m",
            "wrong_answers": ["X = 81.66 m", "X = 73.07 m", "X = 55.77 m"],
            "explanation": "Using tan(38°) = opposite/adjacent: opposite = 25 × tan(38°) ≈ 25 × 2.6051 ≈ 61.88 m.",
            "image_path": "questions/year8/trigonometry/image2.png",
        },
        {
            "question_text": "In a right-angled triangle with angle of 60°, hypotenuse of 20 cm, what is the length of the adjacent side?",
            "correct_answer": "10 cm",
            "wrong_answers": ["17.32 cm", "14.14 cm", "11.55 cm"],
            "explanation": "Using cos(60°) = adjacent/hypotenuse: adjacent = 20 × cos(60°) = 20 × 0.5 = 10 cm."
        },
        {
            "question_text": "A ladder leans against a wall at an angle of 60° to the ground. If the ladder is 8 metres long, how high does it reach up the wall?",
            "correct_answer": "6.93 metres",
            "wrong_answers": ["4 metres", "5.66 metres", "4.62 metres"],
            "explanation": "Using sin(60°) = height/hypotenuse: height = 8 × sin(60°) = 8 × 0.866 = 6.93 metres approximately."
        },
        {
            "question_text": "Which trigonometric ratio would you use to find the angle if you know the opposite and adjacent sides?",
            "correct_answer": "tan⁻¹ (inverse tangent)",
            "wrong_answers": ["sin⁻¹ (inverse sine)", "cos⁻¹ (inverse cosine)", "1/tan (reciprocal tangent)"],
            "explanation": "When you know opposite and adjacent sides, you use tan⁻¹ (arctan or inverse tangent) to find the angle."
        },
        {
            "question_text": "In a right-angled triangle, if the opposite side is 5 cm and the adjacent side is 5 cm, what is the angle?",
            "correct_answer": "45°",
            "wrong_answers": ["30°", "60°", "90°"],
            "explanation": "When opposite = adjacent, the ratio is 1, so tan(angle) = 1, which means angle = 45°."
        },
        {
            "question_text": "In a right-angled triangle, if the opposite side is 8 cm and the hypotenuse is 16 cm, what is the angle?",
            "correct_answer": "30°",
            "wrong_answers": ["45°", "60°", "90°"],
            "explanation": "Using sin(angle) = opposite/hypotenuse = 8/16 = 0.5, and sin(30°) = 0.5, the angle is 30°."
        },
        {
            "question_text": "In a right-angled triangle, if the adjacent side is 5 cm and the hypotenuse is 10 cm, what is the angle?",
            "correct_answer": "60°",
            "wrong_answers": ["30°", "45°", "90°"],
            "explanation": "Using cos(angle) = adjacent/hypotenuse = 5/10 = 0.5, and cos(60°) = 0.5, the angle is 60°."
        },
        {
            "question_text": "In a right-angled triangle, if the opposite side is 10 cm and the adjacent side is 10√3 cm, what is the angle? (tan(30°) = 0.577), tan(60°) = 1.732, tan(45°) = 1, tan(90°) = infinity",
            "correct_answer": "30°",
            "wrong_answers": ["45°", "60°", "90°"],
            "explanation": "Using tan(angle) = opposite/adjacent = 10/(10√3) = 1/√3 ≈ 0.577, and tan(30°) ≈ 0.577, the angle is 30°."
        },
        {
            "question_text": "A ramp makes an angle of 25° with the ground. If the ramp is 10 metres long, what is the vertical height? (sin(25°) = 0.423)",
            "correct_answer": "4.23 metres",
            "wrong_answers": ["9.06 metres", "8.82 metres", "5.87 metres"],
            "explanation": "Using sin(25°) = height/hypotenuse: height = 10 × sin(25°) = 10 × 0.423 = 4.23 metres."
        },
        {
            "question_text": "From a point on the ground 50 metres away from a tower, the angle of elevation to the top is 35°. What is the height of the tower? (tan(35°) = 0.700)",
            "correct_answer": "35 metres",
            "wrong_answers": ["40.96 metres", "61.04 metres", "28.57 metres"],
            "explanation": "Using tan(35°) = height/distance: height = 50 × tan(35°) = 50 × 0.700 = 35 metres."
        },
        {
            "question_text": "An airplane is flying at a height of 3000 metres. The angle of depression to a point on the ground is 28°. What is the horizontal distance? (tan(28°) = 0.532)",
            "correct_answer": "5639 metres",
            "wrong_answers": ["1596 metres", "3407 metres", "6383 metres"],
            "explanation": "Using tan(28°) = height/distance: distance = 3000 / tan(28°) = 3000 / 0.532 ≈ 5639 metres."
        },
        {
            "question_text": "In a right-angled triangle, if sin(θ) = 0.8, what is tan(θ)?",
            "correct_answer": "4/3 or approximately 1.33",
            "wrong_answers": ["3/4 or approximately 0.75", "0.8", "5/4 or approximately 1.25"],
            "explanation": "If sin(θ) = 0.8, then cos(θ) = 0.6 (from sin²θ + cos²θ = 1). Then tan(θ) = sin(θ)/cos(θ) = 0.8/0.6 = 4/3 ≈ 1.33."
        },
        {
            "question_text": "A ladder of 15 metres is placed against a wall such that the angle between the ladder and the ground is 65°. How high does the ladder reach on the wall? (sin(65°) = 0.906)",
            "correct_answer": "13.59 metres",
            "wrong_answers": ["6.34 metres", "14.07 metres", "8.59 metres"],
            "explanation": "Using sin(65°) = height/hypotenuse: height = 15 × sin(65°) = 15 × 0.906 = 13.59 metres."
        },
        {
            "question_text": "If a trigonometric angle has cos(θ) = 0.6, what is sin(θ)?",
            "correct_answer": "0.8",
            "wrong_answers": ["0.6", "0.4", "1.2"],
            "explanation": "Using sin²(θ) + cos²(θ) = 1: sin²(θ) = 1 - 0.36 = 0.64, so sin(θ) = 0.8."
        },
        
        {
            "question_text": "What is sin(90°)?",
            "correct_answer": "1",
            "wrong_answers": ["0", "0.5", "-1"],
            "explanation": "The sine of 90 degrees is 1. At 90 degrees, the opposite side equals the hypotenuse."
        },
        {
            "question_text": "What is cos(0°)?",
            "correct_answer": "1",
            "wrong_answers": ["0", "0.5", "-1"],
            "explanation": "The cosine of 0 degrees is 1. At 0 degrees, the adjacent side equals the hypotenuse."
        },
        {
            "question_text": "What is tan(0°)?",
            "correct_answer": "0",
            "wrong_answers": ["1", "0.5", "undefined"],
            "explanation": "The tangent of 0 degrees is 0. At 0 degrees, the opposite side has length 0."
        },
        {
            "question_text": "In a right-angled triangle, if sin(θ) = 0.6, which trigonometric value is cos(θ)?",
            "correct_answer": "0.8",
            "wrong_answers": ["0.4", "0.6", "1.2"],
            "explanation": "Using sin²(θ) + cos²(θ) = 1: cos²(θ) = 1 - 0.36 = 0.64, so cos(θ) = 0.8."
        },
        {
            "question_text": "A surveyor measures an angle of elevation of 30° to the top of a building from a distance of 100 metres. What is the approximate height of the building? (tan(30°) = 0.577)",
            "correct_answer": "57.7 metres",
            "wrong_answers": ["50 metres", "86.6 metres", "100 metres"],
            "explanation": "Using tan(30°) = height/distance: height = 100 × tan(30°) = 100 × 0.577 = 57.7 metres approximately."
        },
        {
            "question_text": "Which angle has a sine value of approximately 0.866?",
            "correct_answer": "60°",
            "wrong_answers": ["30°", "45°", "90°"],
            "explanation": "sin(60°) ≈ 0.866 (or √3/2). This is one of the standard trigonometric values."
        },
    ]
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for q_data in questions_data:
        question_text = q_data["question_text"]
        
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_8,
            topic=trigonometry_topic,
            question_text=question_text
        ).first()
        
        if existing:
            # Question already exists, update if needed
            existing.explanation = q_data["explanation"]
            existing.save()
            
            # Delete old answers and recreate
            Answer.objects.filter(question=existing).delete()
            
            # Create correct answer
            Answer.objects.create(
                question=existing,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=existing,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )
            
            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [UPDATE] Updated: {safe_text}...")
            updated_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_8,
                topic=trigonometry_topic,
                question_text=question_text,
                question_type="Multiple Choice",
                difficulty=2,
                points=1,
                explanation=q_data["explanation"]
            )
            
            # Create correct answer
            Answer.objects.create(
                question=question,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=question,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )
            
            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [OK] Created: {safe_text}...")
            created_count += 1
    
    print(f"\n[SUMMARY]")
    print(f"   [OK] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"   [SKIP] Skipped: {skipped_count} questions")
    print(f"\n[OK] All Trigonometry questions are associated with Year 8")

if __name__ == "__main__":
    print("[INFO] Setting up Trigonometry topic for Year 8...\n")
    result = setup_trigonometry_topic()
    
    if result:
        trigonometry_topic, level_8 = result
        print("\n" + "="*60)
        add_trigonometry_questions(trigonometry_topic, level_8)
        print("\n[OK] Done!")
