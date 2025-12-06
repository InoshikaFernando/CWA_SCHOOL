#!/usr/bin/env python
"""
Add/Update "Angles" questions for Year 6
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

def setup_angles_topic():
    """Create Angles topic and associate with Year 6"""
    
    # Get or create the "Angles" topic
    angles_topic = Topic.objects.filter(name="Angles").first()
    if not angles_topic:
        angles_topic = Topic.objects.create(name="Angles")
        print(f"[OK] Created topic: Angles")
    else:
        print(f"[INFO] Topic already exists: Angles")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return None
    
    print(f"[INFO] Found Year 6: {level_6}")
    
    # Check if Angles is already associated
    if level_6.topics.filter(name="Angles").exists():
        print("[INFO] Year 6 already has Angles topic associated.")
        print(f"   Current topics for Year 6: {', '.join([t.name for t in level_6.topics.all()])}")
    else:
        # Associate Angles topic with Year 6
        level_6.topics.add(angles_topic)
        print(f"[OK] Successfully associated Angles topic with Year 6")
        print(f"   Year 6 now has topics: {', '.join([t.name for t in level_6.topics.all()])}")
    
    return angles_topic, level_6

def add_angles_questions(angles_topic, level_6):
    """Add/Update Angles questions for Year 6"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    questions_data = [
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "18°",
            "wrong_answers": ["20°", "16°", "15°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 162°, then 𝑎 = 180° - 162° = 18°.",
            "image_path": "questions/year6/angles/image1.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "82°",
            "wrong_answers": ["80°", "85°", "90°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 98°, then 𝑎 = 180° - 98° = 82°.",
            "image_path": "questions/year6/angles/image2.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "82°",
            "wrong_answers": ["80°", "85°", "98°"],
            "explanation": "The angle a and 82° are vertically opposite angles, so they are equal.",
            "image_path": "questions/year6/angles/image3.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "106°",
            "wrong_answers": ["100°", "110°", "104°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 74°, then 𝑎 = 180° - 74° = 106°.",
            "image_path": "questions/year6/angles/image4.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "34°",
            "wrong_answers": ["30°", "36°", "32°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 146°, then 𝑎 = 180° - 146° = 34°.",
            "image_path": "questions/year6/angles/image5.png"
        },
        {
            "question_text": "Without using a protractor, find the values of the pronumerals 𝑎 and 𝑏",
            "question_type": "multiple_choice",
            "correct_answer": "a = 70°, b = 110°",
            "wrong_answers": ["a = 70°, b = 100°", "a = 80°, b = 110°", "a = 60°, b = 120°"],
            "explanation": "Angle 𝑎 is part of a straight line (180°). If the other angle is 110°, then 𝑎 = 180° - 110° = 70°. Angle 𝑏 is also part of a straight line. If the other angle is 70°, then 𝑏 = 180° - 70° = 110°.",
            "image_path": "questions/year6/angles/image6.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "92°",
            "wrong_answers": ["90°", "88°", "94°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 88°, then 𝑎 = 180° - 88° = 92°.",
            "image_path": "questions/year6/angles/image7.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "83°",
            "wrong_answers": ["80°", "85°", "87°"],
            "explanation": "The angle 𝑎 is part of a straight line (180°). If the other angle is 97°, then 𝑎 = 180° - 97° = 83°.",
            "image_path": "questions/year6/angles/image8.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "57°",
            "wrong_answers": ["60°", "55°", "53°"],
            "explanation": "The angles are consecutive interior angles (same-side interior angles) formed by parallel lines and a transversal. Consecutive interior angles are supplementary, so they add up to 180°. If one angle is 123°, then 𝑎 = 180° - 123° = 57°.",
            "image_path": "questions/year6/angles/image9.png"
        },
        {
            "question_text": "Without using a protractor, find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "148°",
            "wrong_answers": ["150°", "145°", "152°"],
            "explanation": "The angles are corresponding angles (or alternate interior angles) formed by parallel lines and a transversal. Corresponding angles are equal when lines are parallel. Since one angle is 148°, then 𝑎 = 148°.",
            "image_path": "questions/year6/angles/image10.png"
        },
        {
            "question_text": "Two lines cut by the transversal are parallel.",
            "question_type": "true_false",
            "correct_answer": "False",
            "wrong_answers": ["True"],
            "explanation": "The two lines are not parallel. If they were parallel, the corresponding angles, alternate interior angles, or consecutive interior angles would have specific relationships. Since these relationships do not hold, the lines are not parallel.",
            "image_path": "questions/year6/angles/image11.png"
        },
        {
            "question_text": "Two lines cut by the transversal are parallel.",
            "question_type": "true_false",
            "correct_answer": "True",
            "wrong_answers": ["False"],
            "explanation": "The two lines are parallel. The consecutive interior angles (105° and 75°) add up to 180°, which confirms that the lines are parallel. When a transversal cuts two parallel lines, consecutive interior angles are supplementary (add up to 180°).",
            "image_path": "questions/year6/angles/image12.png"
        },
        {
            "question_text": "Find the values of the pronumerals 𝑎 and 𝑏",
            "question_type": "multiple_choice",
            "correct_answer": "a = 42°, b = 48°",
            "wrong_answers": ["a = 42°, b = 50°", "a = 40°, b = 48°", "a = 45°, b = 45°"],
            "explanation": "Angle 𝑎 and the given angle are on a straight line, so they are supplementary: 𝑎 = 180° - 138° = 42°. Angle 𝑏 and the given angle are also on a straight line: 𝑏 = 180° - 132° = 48°.",
            "image_path": "questions/year6/angles/image13.png"
        },
        {
            "question_text": "Find the values of the pronumerals 𝑎 and 𝑏",
            "question_type": "multiple_choice",
            "correct_answer": "a = 284°, b = 104°",
            "wrong_answers": ["a = 284°, b = 100°", "a = 280°, b = 104°", "a = 290°, b = 110°"],
            "explanation": "Angle 𝑎 is found using the relationship between angles around a point or on intersecting lines. Angle 𝑏 is found using supplementary angles or angle relationships in the diagram.",
            "image_path": "questions/year6/angles/image14.png"
        },
        {
            "question_text": "Find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "45°",
            "wrong_answers": ["40°", "50°", "35°"],
            "explanation": "The angle 𝑎 is found using angle relationships in the diagram. This may involve supplementary angles, angles on a straight line, or angles in a triangle.",
            "image_path": "questions/year6/angles/image15.png"
        },
        {
            "question_text": "Find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "50°",
            "wrong_answers": ["45°", "55°", "48°"],
            "explanation": "The angle 𝑎 is found using angle relationships in the diagram. This may involve supplementary angles, angles on a straight line, angles in a triangle, or relationships with parallel lines.",
            "image_path": "questions/year6/angles/image16.png"
        },
        {
            "question_text": "Find the values of the pronumerals 𝑎 and 𝑥",
            "question_type": "multiple_choice",
            "correct_answer": "a = 40°, x = 140°",
            "wrong_answers": ["a = 40°, x = 135°", "a = 45°, x = 140°", "a = 35°, x = 145°"],
            "explanation": "Angle 𝑎 and angle 𝑥 are found using angle relationships in the diagram. This may involve supplementary angles, angles on a straight line, angles in a triangle, or relationships with parallel lines.",
            "image_path": "questions/year6/angles/image17.png"
        },
        {
            "question_text": "Find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "78°",
            "wrong_answers": ["75°", "80°", "72°"],
            "explanation": "The angle 𝑎 is found using angle relationships in the diagram. This may involve supplementary angles, angles on a straight line, angles in a triangle, or relationships with parallel lines.",
            "image_path": "questions/year6/angles/image18.png"
        },
        {
            "question_text": "Find the value of the pronumeral 𝑎",
            "question_type": "multiple_choice",
            "correct_answer": "55°",
            "wrong_answers": ["50°", "60°", "52°"],
            "explanation": "The angle 𝑎 is found using angle relationships in the diagram. This may involve supplementary angles, angles on a straight line, angles in a triangle, or relationships with parallel lines.",
            "image_path": "questions/year6/angles/image19.png"
        },
        {
            "question_text": "Which angle corresponds to ∠BAF?",
            "question_type": "multiple_choice",
            "correct_answer": "∠EDF",
            "wrong_answers": ["∠CDF", "∠CDA", "∠ADC"],
            "explanation": "Corresponding angles are angles that are in the same relative position when two parallel lines are cut by a transversal. ∠BAF and ∠EDF are corresponding angles because they are both on the same side of the transversal and in the same relative position.",
            "image_path": "questions/year6/angles/image20.png"
        },
    ]
    
    # Use shared utility function to process questions
    results = process_questions(
        level=level_6,
        topic=angles_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    return results['created'] + results['updated']

if __name__ == "__main__":
    print("=" * 60)
    print("Year 6 - Angles Questions")
    print("=" * 60)
    
    # Setup topic
    result = setup_angles_topic()
    if result is None:
        print("[ERROR] Failed to setup topic. Exiting.")
        sys.exit(1)
    
    angles_topic, level_6 = result
    
    # Add questions
    print("\n" + "=" * 60)
    print("Adding/Updating Questions")
    print("=" * 60)
    add_angles_questions(angles_topic, level_6)
    
    print("\n[OK] Script completed successfully!")

