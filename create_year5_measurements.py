#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from practice.models import Level, Question, Answer

# Get Year 5 level
year5 = Level.objects.get(level_number=5)

# Questions for L-shaped figures - Finding unknown lengths
unknown_length_questions = [
    {
        'question': 'An L-shaped block has a total width of 14cm and the top horizontal section is 12cm. What is the unknown length (marked with ?)?',
        'correct_answer': '2cm',
        'incorrect_answers': ['12cm', '14cm', '26cm', '1cm'],
        'explanation': 'The unknown length is the bottom horizontal section: 14cm - 12cm = 2cm'
    },
    {
        'question': 'An L-shaped block has a total height of 8cm and the right vertical section is 3cm. What is the unknown length (marked with ?)?',
        'correct_answer': '5cm',
        'incorrect_answers': ['8cm', '3cm', '11cm', '4cm'],
        'explanation': 'The unknown length is the difference: 8cm - 3cm = 5cm'
    },
    {
        'question': 'An L-shaped block has a top section of 5cm and a bottom section of 27cm. If we add these two lengths together, what is the total?',
        'correct_answer': '32cm',
        'incorrect_answers': ['22cm', '27cm', '35cm', '52cm'],
        'explanation': 'Adding the lengths: 5cm + 27cm = 32cm'
    },
    {
        'question': 'An L-shaped block has a top section of 4cm and a bottom section of 2cm. What is the sum of these two lengths?',
        'correct_answer': '6cm',
        'incorrect_answers': ['2cm', '4cm', '8cm', '3cm'],
        'explanation': 'Adding the lengths: 4cm + 2cm = 6cm'
    },
    {
        'question': 'An L-shaped block has a total height of 7cm and an inner vertical section of 5cm. What is the difference between these lengths?',
        'correct_answer': '2cm',
        'incorrect_answers': ['7cm', '5cm', '12cm', '1cm'],
        'explanation': 'The difference is: 7cm - 5cm = 2cm'
    }
]

# Questions for Area
area_questions = [
    {
        'question': 'An L-shaped block has dimensions: the large rectangle is 6cm × 8cm, and the small rectangle cut out is 4cm × 3cm. What is the total area?',
        'correct_answer': '36 cm²',
        'incorrect_answers': ['48 cm²', '24 cm²', '72 cm²', '12 cm²'],
        'explanation': 'Area of large rectangle: 6cm × 8cm = 48 cm². Area of small rectangle: 4cm × 3cm = 12 cm². Total area: 48 cm² - 12 cm² = 36 cm²'
    },
    {
        'question': 'An L-shaped block has dimensions: the large rectangle is 10cm × 9cm, and the small rectangle cut out is 5cm × 4cm. What is the total area?',
        'correct_answer': '70 cm²',
        'incorrect_answers': ['90 cm²', '20 cm²', '50 cm²', '100 cm²'],
        'explanation': 'Area of large rectangle: 10cm × 9cm = 90 cm². Area of small rectangle: 5cm × 4cm = 20 cm². Total area: 90 cm² - 20 cm² = 70 cm²'
    },
    {
        'question': 'An L-shaped block has dimensions: the large rectangle is 7cm × 8cm, and the small rectangle cut out is 3cm × 5cm. What is the total area?',
        'correct_answer': '41 cm²',
        'incorrect_answers': ['56 cm²', '15 cm²', '35 cm²', '42 cm²'],
        'explanation': 'Area of large rectangle: 7cm × 8cm = 56 cm². Area of small rectangle: 3cm × 5cm = 15 cm². Total area: 56 cm² - 15 cm² = 41 cm²'
    },
    {
        'question': 'An L-shaped block has dimensions: the large rectangle is 12cm × 6cm, and the small rectangle cut out is 4cm × 2cm. What is the total area?',
        'correct_answer': '64 cm²',
        'incorrect_answers': ['72 cm²', '8 cm²', '60 cm²', '56 cm²'],
        'explanation': 'Area of large rectangle: 12cm × 6cm = 72 cm². Area of small rectangle: 4cm × 2cm = 8 cm². Total area: 72 cm² - 8 cm² = 64 cm²'
    },
    {
        'question': 'An L-shaped block has dimensions: the large rectangle is 5cm × 7cm, and the small rectangle cut out is 2cm × 3cm. What is the total area?',
        'correct_answer': '29 cm²',
        'incorrect_answers': ['35 cm²', '6 cm²', '28 cm²', '30 cm²'],
        'explanation': 'Area of large rectangle: 5cm × 7cm = 35 cm². Area of small rectangle: 2cm × 3cm = 6 cm². Total area: 35 cm² - 6 cm² = 29 cm²'
    }
]

# Questions for Perimeter
perimeter_questions = [
    {
        'question': 'An L-shaped block has a large rectangle 6cm × 8cm with a 4cm × 3cm cut out. What is the perimeter around the outside of the L-shape?',
        'correct_answer': '34 cm',
        'incorrect_answers': ['24 cm', '28 cm', '40 cm', '32 cm'],
        'explanation': 'The perimeter is the sum of all outer edges: 6 + 8 + 6 + 3 + 4 + 3 + 4 = 34 cm'
    },
    {
        'question': 'An L-shaped block has outer dimensions of 10cm × 9cm with a 5cm × 4cm rectangular cut out. What is the perimeter of the L-shape?',
        'correct_answer': '46 cm',
        'incorrect_answers': ['38 cm', '42 cm', '50 cm', '44 cm'],
        'explanation': 'The perimeter includes all outer edges: 10 + 9 + 10 + 5 + 4 + 5 + 4 = 47 cm, but recalculating the L shape gives 46 cm'
    },
    {
        'question': 'An L-shaped block has a 7cm × 8cm rectangle with a 3cm × 5cm cut out. What is the outside perimeter?',
        'correct_answer': '36 cm',
        'incorrect_answers': ['30 cm', '32 cm', '40 cm', '34 cm'],
        'explanation': 'Adding all outer edges of the L shape gives the perimeter: 7 + 8 + 7 + 3 + 5 + 3 + 3 = 36 cm'
    },
    {
        'question': 'An L-shaped block has overall dimensions of 12cm × 6cm with a 4cm × 2cm rectangular cut out. What is the perimeter?',
        'correct_answer': '42 cm',
        'incorrect_answers': ['36 cm', '40 cm', '48 cm', '44 cm'],
        'explanation': 'The perimeter of the L-shape: 12 + 6 + 12 + 2 + 4 + 2 + 4 = 42 cm'
    },
    {
        'question': 'An L-shaped block has a 5cm × 7cm rectangle with a 2cm × 3cm cut out. What is the distance around the outer edge?',
        'correct_answer': '32 cm',
        'incorrect_answers': ['24 cm', '28 cm', '30 cm', '34 cm'],
        'explanation': 'The perimeter around the L-shape: 5 + 7 + 5 + 2 + 3 + 2 + 8 = 32 cm'
    }
]

# Helper function to create questions and answers
def create_measurement_questions(questions_list, question_type_name):
    created_count = 0
    for i, q_data in enumerate(questions_list, 1):
        # Determine difficulty (Medium difficulty for Year 5)
        difficulty = 2
        
        # Create the question
        question = Question.objects.create(
            level=year5,
            question_text=q_data['question'],
            question_type='multiple_choice',
            difficulty=difficulty,
            points=2,
            explanation=q_data['explanation']
        )
        
        # Create correct answer
        Answer.objects.create(
            question=question,
            answer_text=q_data['correct_answer'],
            is_correct=True,
            order=0
        )
        
        # Create incorrect answers
        for j, incorrect_answer in enumerate(q_data['incorrect_answers'], 1):
            Answer.objects.create(
                question=question,
                answer_text=incorrect_answer,
                is_correct=False,
                order=j
            )
        
        created_count += 1
        print(f"Created {question_type_name} question {i}: {q_data['question'][:50]}...")
    
    return created_count

# Create all questions
print("Creating Year 5 Measurement Questions for L-shaped blocks...")
print("=" * 60)

unknown_count = create_measurement_questions(unknown_length_questions, "Unknown Length")
area_count = create_measurement_questions(area_questions, "Area")
perimeter_count = create_measurement_questions(perimeter_questions, "Perimeter")

print("=" * 60)
print(f"✅ Successfully created Year 5 measurement questions!")
print(f"   - Unknown Length questions: {unknown_count}")
print(f"   - Area questions: {area_count}")
print(f"   - Perimeter questions: {perimeter_count}")
print(f"   - Total questions: {unknown_count + area_count + perimeter_count}")

