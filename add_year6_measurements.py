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
    # Handle case where multiple topics with same name exist
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
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
            "question_type": "multiple_choice",
            "correct_answer": "25.6 cm",  
            "wrong_answers": ["25.7 cm", "24.6 cm", "26.6 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image3.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "38.1 cm", 
            "wrong_answers": ["38.2 cm", "37.1 cm", "39.1 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image4.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "42 cm",  
            "wrong_answers": ["43 cm", "41 cm", "44 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image5.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "28.2 cm",  
            "wrong_answers": ["28.3 cm", "28.1 cm", "28.4 cm"],  # Not used for short_answer
            "explanation": "Add all side lengths shown to get the perimeter.",
            "image_path": "questions/year6/measurements/image6.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "16.07 cm",  
            "wrong_answers": ["7.07 cm", "28.29 cm", "14.14 cm"],  # Not used for short_answer
            "explanation": "Calculate the perimeter by finding the quarter circle's arc length (one-quarter of the full circle's circumference) and adding it to the two straight side lengths.",
            "image_path": "questions/year6/measurements/image11.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "356.29 mm",  
            "wrong_answers": ["540.57 mm", "270.29 mm", "313.29 mm"],  # Not used for short_answer
            "explanation": "Calculate the perimeter by finding the half circle's arc length (one-half of the full circle's circumference) and adding it to the two straight side lengths.",
            "image_path": "questions/year6/measurements/image12.png",
        },
        {
            "question_text": "Find the perimeter of each of these shapes.",
            "question_type": "multiple_choice",
            "correct_answer": "45.43 m",  
            "wrong_answers": ["62.86 m", "31.43 m", "37.43 m"],  # Not used for short_answer
            "explanation": "Calculate the perimeter by finding the half circle's arc length (one-half of the full circle's circumference) and adding it to the two straight side lengths.",
            "image_path": "questions/year6/measurements/image13.png",
        },
        {
            "question_text": "What is the volume of the spacecraft? (use π = 22/7)",
            "question_type": "multiple_choice",
            "correct_answer": "4 x 22 x 7 x 7 m3",
            "wrong_answers": ["22 X 7 X 7 X 7 m3", "5 x 22 x 7 x 7 m3", "1/3 x 7 x 49 + 22 x 21 x 14 m3", "3/4 x 22 x 49 + 22 x 14 x 20 cm3"],  # Not used for short_answer
            "explanation": "Volume for the corn is 1/3πR²h and volume of cylinder is πR²h",
            "image_path": "questions/year6/measurements/image23.png",
        },
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
            "question_type": "multiple_choice",
            "correct_answer": "154 cm²",  # No answer provided in database
            "wrong_answers": ["44 cm²", "49 cm²", "144 cm²"],  # Not used for short_answer
            "explanation": "Calculate the area using πr².",
            "image_path": "questions/year6/measurements/image7.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "380.29 cm²",  # No answer provided in database
            "wrong_answers": ["69.14 cm²", "69.14 cm", "375.14 cm³"],  # Not used for short_answer
            "explanation": "Calculate the area using πr².",
            "image_path": "questions/year6/measurements/image8.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "113.14 cm²",  # No answer provided in database
            "wrong_answers": ["37.71 cm", "39.14 cm³", "113.14 cm²"],  # Not used for short_answer
            "explanation": "Calculate the area using πr².",
            "image_path": "questions/year6/measurements/image9.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "707.14 cm²",  # No answer provided in database
            "wrong_answers": ["94.29 cm²", "94.29 cm", "984.29 cm³"],  # Not used for short_answer
            "explanation": "Calculate the area using πr²",
            "image_path": "questions/year6/measurements/image10.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "15.91 cm²",  # No answer provided in database
            "wrong_answers": ["63.64 cm", "24.91 cm³", "53.64 cm²"],  # Not used for short_answer
            "explanation": "Calculate the area using πr² and divide by 4.",
            "image_path": "questions/year6/measurements/image11.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "2905.57 mm²",  # No answer provided in database
            "wrong_answers": ["5811.14 mm²", "6905.57 mm", "2905.57 cm³"],  # Not used for short_answer
            "explanation": "Calculate the area using πr² and divide by 2.",
            "image_path": "questions/year6/measurements/image12.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "102 m²",  # No answer provided in database
            "wrong_answers": ["78.57 m", "24 m²", "102 cm³"],  # Not used for short_answer
            "explanation": "Calculate the area using πr² and divide by 2, and add the triagle area by 1/2 x base x height.",
            "image_path": "questions/year6/measurements/image13.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "14.4 cm²",  # No answer provided in database
            "wrong_answers": ["14.4 m", "7.2 cm³", "7.2 m²"],  # Not used for short_answer
            "explanation": "Calculate the area of the Parallelogram using base x height.",
            "image_path": "questions/year6/measurements/image14.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "27 m²",  # No answer provided in database
            "wrong_answers": ["27 cm²", "24 cm³", "24 m³"],  # Not used for short_answer
            "explanation": "Calculate the area of the Parallelogram using base x height.",
            "image_path": "questions/year6/measurements/image15.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "48 cm²",  # No answer provided in database
            "wrong_answers": ["14 m", "14 cm³", "48 m²"],  # Not used for short_answer
            "explanation": "Calculate the area of the Parallelogram using base x height.",
            "image_path": "questions/year6/measurements/image16.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "58.5 cm²",  # No answer provided in database
            "wrong_answers": ["15.5 m³", "58.5 cm³", "48 m²"],  # Not used for short_answer
            "explanation": "Calculate the area of the Parallelogram using base x height.",
            "image_path": "questions/year6/measurements/image17.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "33 m²",  # No answer provided in database
            "wrong_answers": ["66 m²", "66 cm³", "33 m³"],  # Not used for short_answer
            "explanation": "Calculate the area of the triangle using 1/2 x base x height.",
            "image_path": "questions/year6/measurements/image18.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "54 m²",  # No answer provided in database
            "wrong_answers": ["108 m²", "108 cm³", "54 m³"],  # Not used for short_answer
            "explanation": "Calculate the area of the triangle using 1/2 x base x height.",
            "image_path": "questions/year6/measurements/image19.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "10.5 m²",  # No answer provided in database
            "wrong_answers": ["10.5 cm²", "21 m³", "21 m²"],  # Not used for short_answer
            "explanation": "Calculate the area of the triangle using 1/2 x base x height.",
            "image_path": "questions/year6/measurements/image20.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "152 m²",  # No answer provided in database
            "wrong_answers": ["160 m²", "152 cm³", "160 cm³"],  # Not used for short_answer
            "explanation": "Calculate the rectangle area and remove the triangle area. (area of triangle is 1/2 x base x height).",
            "image_path": "questions/year6/measurements/image21.png",
        },
        {
            "question_text": "Calculate the area of this shape.",
            "question_type": "multiple_choice",
            "correct_answer": "120 m²",  # No answer provided in database
            "wrong_answers": ["120 cm²", "180 m²", "180 cm³"],  # Not used for short_answer
            "explanation": "Calculate the rectangle area and remove the triangle area. (area of triangle is 1/2 x base x height).",
            "image_path": "questions/year6/measurements/image22.png",
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
        {
            "question_text": "The width of a cube increases by 50%, but it remains a cube. What is the percentage increase in the surface area of the cube?",
            "question_type": "multiple_choice",
            "correct_answer": "125%",
            "wrong_answers": ["200%", "225%", "125%", "75%"],
            "explanation": "Let the original side length of the cube = x, Original surface area = 6𝑥². New side length = 1.5𝑥, New surface area = 6(1.5𝑥)² = 13.5𝑥². Percentage increase = (New surface area - Original surface area) / Original surface area * 100% = (13.5𝑥² - 6𝑥²) / 6𝑥² * 100% = 125%.",
        },
        {
            "question_text": "The sides of a square are doubled. What is the percentage increase in its area?",
            "question_type": "multiple_choice",
            "correct_answer": "300%",
            "wrong_answers": ["100%", "200%", "400%", "300%"],
            "explanation": "Let the side = x, original area = x². New side = 2x, new area = (2x)² = 4x². Percentage increase = (4x² - x²) / x² × 100 = 300%."
        },
        {
            "question_text": "The radius of a circle increases by 20%. What is the percentage increase in its area?",
            "question_type": "multiple_choice",
            "correct_answer": "44%",
            "wrong_answers": ["20%", "40%", "60%", "44%"],
            "explanation": "Area ∝ r². If radius increases by 20%, new radius = 1.2r. New area = (1.2r)² = 1.44r², meaning a 44% increase."
        },
        {
            "question_text": "The height of a cylinder is doubled and the radius is halved. What happens to its volume?",
            "question_type": "multiple_choice",
            "correct_answer": "It stays the same",
            "wrong_answers": ["It doubles", "It halves", "It becomes one-quarter", "It stays the same"],
            "explanation": "Volume = πr²h. New volume = π(½r)²(2h) = πr²h. The volume remains unchanged."
        },
        {
            "question_text": "The length of a rectangle is increased by 50%, and the width stays the same. What is the percentage increase in area?",
            "question_type": "multiple_choice",
            "correct_answer": "50%",
            "wrong_answers": ["25%", "75%", "100%", "50%"],
            "explanation": "Area = L × W. Increasing length by 50% makes it 1.5L, so new area = 1.5LW. Increase = 50%."
        },
        {
            "question_text": "A cube’s edge length is tripled. By what factor does its volume increase?",
            "question_type": "multiple_choice",
            "correct_answer": "27 times",
            "wrong_answers": ["3 times", "6 times", "9 times", "27 times"],
            "explanation": "Volume ∝ side³. If side is tripled, volume increases by 3³ = 27 times."
        },
        {
            "question_text": "All dimensions of a rectangular prism are reduced by 50%. What is the percentage decrease in its volume?",
            "question_type": "multiple_choice",
            "correct_answer": "87.5%",
            "wrong_answers": ["50%", "75%", "90%", "87.5%"],
            "explanation": "Volume ∝ length × width × height. If each is halved, new volume = (0.5)³ = 0.125, meaning 12.5% remains, so an 87.5% decrease."
        },
        {
            "question_text": "The diameter of a circle is reduced by 40%. What is the percentage decrease in its area?",
            "question_type": "multiple_choice",
            "correct_answer": "64%",
            "wrong_answers": ["40%", "36%", "60%", "64%"],
            "explanation": "Area ∝ r². New radius = 0.6r, new area = 0.36r² → area decreases by 64%."
        },
        {
            "question_text": "The volume of a cube doubles. What is the percentage increase in the cube’s side length?",
            "question_type": "multiple_choice",
            "correct_answer": "26%",
            "wrong_answers": ["10%", "20%", "30%", "26%"],
            "explanation": "Volume ∝ side³. New side = ³√2 × old side ≈ 1.26×, which is a 26% increase."
        },
        {
            "question_text": "A rectangle’s perimeter is 60 cm. If both its length and width increase by 25%, what is the new perimeter?",
            "question_type": "multiple_choice",
            "correct_answer": "75 cm",
            "wrong_answers": ["70 cm", "80 cm", "90 cm", "75 cm"],
            "explanation": "Perimeter ∝ (L + W). If both increase by 25%, total perimeter increases by 25% → 60 × 1.25 = 75 cm."
        },
        {
            "question_text": "The surface area of a cube is 150 cm². If the edge length doubles, what is the new surface area?",
            "question_type": "multiple_choice",
            "correct_answer": "600 cm²",
            "wrong_answers": ["300 cm²", "450 cm²", "750 cm²", "600 cm²"],
            "explanation": "Surface area ∝ side². Doubling the side makes the area 4 times larger → 150 × 4 = 600 cm²."
        },
        {
            "question_text": "A cube-shaped gift box has a side length of 10 cm. If the side is increased by 20%, what is the new volume of the box compared to the old one?",
            "question_type": "multiple_choice",
            "correct_answer": "1.728 times larger",
            "wrong_answers": ["1.2 times larger", "1.44 times larger", "2 times larger", "1.728 times larger"],
            "explanation": "Volume ∝ side³. New side = 1.2× old side, so new volume = (1.2)³ = 1.728× the original."
        },
        {
            "question_text": "A rectangular water tank is 2 m long, 1.5 m wide, and 1 m high. If the height is doubled, how much more water can it hold?",
            "question_type": "multiple_choice",
            "correct_answer": "Double the amount",
            "wrong_answers": ["Half the amount", "Three times the amount", "Four times the amount", "Double the amount"],
            "explanation": "Volume ∝ height. Doubling height doubles the capacity → 2× the amount of water."
        },
        {
            "question_text": "A cylindrical candle has a radius of 5 cm and height of 10 cm. If the radius is doubled and height stays the same, how many times greater is its volume?",
            "question_type": "multiple_choice",
            "correct_answer": "4 times greater",
            "wrong_answers": ["2 times", "6 times", "8 times", "4 times greater"],
            "explanation": "Volume of a cylinder = πr²h. Doubling radius makes r² → (2r)² = 4r² → volume increases 4 times."
        },
        {
            "question_text": "A cone has a radius of 3 cm and height of 8 cm. If both radius and height are doubled, how many times greater is the volume?",
            "question_type": "multiple_choice",
            "correct_answer": "8 times greater",
            "wrong_answers": ["2 times", "4 times", "6 times", "8 times greater"],
            "explanation": "Volume of a cone = ⅓πr²h. If both r and h double → (2r)²(2h) = 8× bigger."
        },
        {
            "question_text": "A cylindrical water bottle has a volume of 500 mL. If its height is doubled but the radius stays the same, what will the new volume be?",
            "question_type": "multiple_choice",
            "correct_answer": "1 L",
            "wrong_answers": ["750 mL", "1.5 L", "250 mL", "1 L"],
            "explanation": "Volume ∝ height. Doubling height doubles volume → 500 mL × 2 = 1 L."
        },
        {
            "question_text": "A metal cube is melted and reshaped into a cylinder with the same volume. If the cube’s side is 6 cm, what is its volume?",
            "question_type": "multiple_choice",
            "correct_answer": "216 cm³",
            "wrong_answers": ["36 cm³", "64 cm³", "125 cm³", "216 cm³"],
            "explanation": "Volume of a cube = side³ = 6³ = 216 cm³."
        },
        {
            "question_text": "A cone and a cylinder have the same base radius and height. How does the volume of the cone compare to the cylinder?",
            "question_type": "multiple_choice",
            "correct_answer": "The cone’s volume is one-third of the cylinder’s volume",
            "wrong_answers": ["The same", "Half", "Twice", "The cone’s volume is one-third of the cylinder’s volume"],
            "explanation": "Volume of a cone = ⅓πr²h, while cylinder = πr²h. Therefore, cone = one-third of the cylinder."
        },
        {
            "question_text": "A cylindrical jar has a radius of 4 cm and height of 12 cm. If both radius and height increase by 25%, how many times larger is the new volume?",
            "question_type": "multiple_choice",
            "correct_answer": "1.953 times larger",
            "wrong_answers": ["1.5 times", "2 times", "1.75 times", "1.953 times larger"],
            "explanation": "Volume ∝ r²h. New radius = 1.25r, new height = 1.25h → new volume = (1.25)³ = 1.953× larger."
        },
        {
            "question_text": "A swimming pool is shaped like a rectangular prism 8 m long, 4 m wide, and 2 m deep. If it is filled halfway, how much water is inside?",
            "question_type": "multiple_choice",
            "correct_answer": "32 m³",
            "wrong_answers": ["16 m³", "24 m³", "64 m³", "32 m³"],
            "explanation": "Full volume = 8×4×2 = 64 m³. Half full = 64 ÷ 2 = 32 m³."
        },
        {
            "question_text": "A cone-shaped paper cup has a height of 9 cm and radius of 3 cm. If both dimensions are halved, what happens to its volume?",
            "question_type": "multiple_choice",
            "correct_answer": "It becomes one-eighth as large",
            "wrong_answers": ["One-quarter", "One-third", "Half", "It becomes one-eighth as large"],
            "explanation": "Volume ∝ r²h. If r and h are halved → (½)³ = ⅛ → volume becomes one-eighth."
        }
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
                level=level_6,
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
        # Always set the image path if specified (file may exist in production even if not locally)
        if "image_path" in q_data and q_data["image_path"]:
            image_path = q_data["image_path"]
            # Check if image path needs updating
            current_image = question.image.name if question.image else None
            if current_image != image_path:
                question.image.name = image_path
                question.save()
                print(f"      [IMAGE] Updated image path: {current_image or 'None'} -> {image_path}")
            else:
                print(f"      [IMAGE] Image path already set: {image_path}")
            
            # Optional: Warn if file doesn't exist locally (but still set the path)
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if not os.path.exists(full_image_path):
                print(f"      [INFO] Image file not found locally (may exist in production): {full_image_path}")
        
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

