#!/usr/bin/env python
"""
Add "Fractions" topic for Year 4 and all associated questions
This script creates the topic, associates it with Year 4, and adds fraction questions
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

def setup_fractions_topic():
    """Create Fractions topic and associate with Year 4"""
    
    # Get or create the "Fractions" topic (may already exist from Year 3)
    fractions_topic = Topic.objects.filter(name="Fractions").first()
    if not fractions_topic:
        fractions_topic = Topic.objects.create(name="Fractions")
        print(f"✅ Created topic: Fractions")
    else:
        print(f"ℹ️  Topic already exists: Fractions")
    
    # Get Year 4 level
    level_4 = Level.objects.filter(level_number=4).first()
    
    if not level_4:
        print("❌ Error: Year 4 level not found!")
        return None
    
    print(f"📋 Found Year 4: {level_4}")
    
    # Check if Fractions is already associated
    if level_4.topics.filter(name="Fractions").exists():
        print("ℹ️  Year 4 already has Fractions topic associated.")
        print(f"   Current topics for Year 4: {', '.join([t.name for t in level_4.topics.all()])}")
    else:
        # Associate Fractions topic with Year 4
        level_4.topics.add(fractions_topic)
        print(f"✅ Successfully associated Fractions topic with Year 4")
        print(f"   Year 4 now has topics: {', '.join([t.name for t in level_4.topics.all()])}")
    
    return fractions_topic, level_4

def add_fractions_questions(fractions_topic, level_4):
    """Add Fractions questions for Year 4"""
    
    # Define questions - more advanced fraction questions for Year 4
    questions_data = [
        # Equivalent fractions
        {
            "question_text": "Which fraction is equivalent to 1/2?",
            "correct_answer": "2/4",
            "wrong_answers": ["1/3", "2/3", "3/4"],
            "explanation": "1/2 is equivalent to 2/4 because both represent the same value. When you multiply the numerator and denominator of 1/2 by 2, you get 2/4."
        },
        {
            "question_text": "Which fraction is equivalent to 1/3?",
            "correct_answer": "2/6",
            "wrong_answers": ["1/6", "2/3", "3/6"],
            "explanation": "1/3 is equivalent to 2/6 because both represent the same value. When you multiply the numerator and denominator of 1/3 by 2, you get 2/6."
        },
        {
            "question_text": "Which fraction is equivalent to 2/4?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/4", "2/2", "4/2"],
            "explanation": "2/4 is equivalent to 1/2 because both represent the same value. When you divide the numerator and denominator of 2/4 by 2, you get 1/2."
        },
        {
            "question_text": "Which fraction is equivalent to 3/6?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/3", "2/3", "3/3"],
            "explanation": "3/6 is equivalent to 1/2 because both represent the same value. When you divide the numerator and denominator of 3/6 by 3, you get 1/2."
        },
        {
            "question_text": "Which fraction is equivalent to 2/8?",
            "correct_answer": "1/4",
            "wrong_answers": ["1/8", "2/4", "4/8"],
            "explanation": "2/8 is equivalent to 1/4 because both represent the same value. When you divide the numerator and denominator of 2/8 by 2, you get 1/4."
        },
        # Fraction addition (simple)
        {
            "question_text": "What is 1/4 + 1/4?",
            "correct_answer": "2/4",
            "wrong_answers": ["1/8", "2/8", "1/2"],
            "explanation": "When adding fractions with the same denominator, add the numerators and keep the denominator the same. 1/4 + 1/4 = 2/4."
        },
        {
            "question_text": "What is 1/3 + 1/3?",
            "correct_answer": "2/3",
            "wrong_answers": ["1/6", "2/6", "3/3"],
            "explanation": "When adding fractions with the same denominator, add the numerators and keep the denominator the same. 1/3 + 1/3 = 2/3."
        },
        {
            "question_text": "What is 1/5 + 2/5?",
            "correct_answer": "3/5",
            "wrong_answers": ["3/10", "1/5", "2/5"],
            "explanation": "When adding fractions with the same denominator, add the numerators and keep the denominator the same. 1/5 + 2/5 = 3/5."
        },
        {
            "question_text": "What is 2/6 + 1/6?",
            "correct_answer": "3/6",
            "wrong_answers": ["3/12", "1/2", "2/6"],
            "explanation": "When adding fractions with the same denominator, add the numerators and keep the denominator the same. 2/6 + 1/6 = 3/6."
        },
        # Fraction comparison
        {
            "question_text": "Which is larger: 3/4 or 1/2?",
            "correct_answer": "3/4",
            "wrong_answers": ["1/2", "They are equal", "Cannot compare"],
            "explanation": "3/4 is larger than 1/2. To compare, convert 1/2 to 2/4. Since 3/4 > 2/4, 3/4 is larger."
        },
        {
            "question_text": "Which is larger: 2/3 or 1/2?",
            "correct_answer": "2/3",
            "wrong_answers": ["1/2", "They are equal", "Cannot compare"],
            "explanation": "2/3 is larger than 1/2. To compare, convert to common denominator: 2/3 = 4/6 and 1/2 = 3/6. Since 4/6 > 3/6, 2/3 is larger."
        },
        {
            "question_text": "Which is larger: 1/4 or 1/3?",
            "correct_answer": "1/3",
            "wrong_answers": ["1/4", "They are equal", "Cannot compare"],
            "explanation": "1/3 is larger than 1/4. When comparing fractions with the same numerator, the fraction with the smaller denominator is larger."
        },
        {
            "question_text": "Which is larger: 3/5 or 2/5?",
            "correct_answer": "3/5",
            "wrong_answers": ["2/5", "They are equal", "Cannot compare"],
            "explanation": "3/5 is larger than 2/5. When fractions have the same denominator, the fraction with the larger numerator is larger."
        },
        # Fraction of a number
        {
            "question_text": "What is 1/2 of 8?",
            "correct_answer": "4",
            "wrong_answers": ["2", "6", "16"],
            "explanation": "To find 1/2 of 8, divide 8 by 2. 8 ÷ 2 = 4."
        },
        {
            "question_text": "What is 1/3 of 9?",
            "correct_answer": "3",
            "wrong_answers": ["2", "6", "27"],
            "explanation": "To find 1/3 of 9, divide 9 by 3. 9 ÷ 3 = 3."
        },
        {
            "question_text": "What is 1/4 of 12?",
            "correct_answer": "3",
            "wrong_answers": ["2", "4", "48"],
            "explanation": "To find 1/4 of 12, divide 12 by 4. 12 ÷ 4 = 3."
        },
        {
            "question_text": "What is 2/3 of 6?",
            "correct_answer": "4",
            "wrong_answers": ["2", "3", "12"],
            "explanation": "To find 2/3 of 6, first find 1/3 of 6 (which is 2), then multiply by 2. 2 × 2 = 4."
        },
        # Mixed numbers (simple)
        {
            "question_text": "What is 1 1/2 as an improper fraction?",
            "correct_answer": "3/2",
            "wrong_answers": ["2/2", "1/2", "2/1"],
            "explanation": "To convert 1 1/2 to an improper fraction, multiply the whole number (1) by the denominator (2) and add the numerator (1): (1 × 2) + 1 = 3. So 1 1/2 = 3/2."
        },
        {
            "question_text": "What is 2 1/3 as an improper fraction?",
            "correct_answer": "7/3",
            "wrong_answers": ["3/3", "1/3", "6/3"],
            "explanation": "To convert 2 1/3 to an improper fraction, multiply the whole number (2) by the denominator (3) and add the numerator (1): (2 × 3) + 1 = 7. So 2 1/3 = 7/3."
        },
        # Fraction word problems
        {
            "question_text": "Sarah ate 1/4 of a pizza. Tom ate 1/4 of the same pizza. How much pizza did they eat together?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/8", "2/8", "1/4"],
            "explanation": "Sarah ate 1/4 and Tom ate 1/4. Together: 1/4 + 1/4 = 2/4 = 1/2."
        },
        {
            "question_text": "A cake is cut into 8 equal pieces. John eats 3 pieces. What fraction of the cake did John eat?",
            "correct_answer": "3/8",
            "wrong_answers": ["1/8", "3/4", "1/3"],
            "explanation": "The cake is divided into 8 equal pieces, and John ate 3 pieces. So John ate 3/8 of the cake."
        },
        {
            "question_text": "3/4 of a number is 15. What is the whole number?",
            "correct_answer": "20",
            "wrong_answers": ["18", "25", "12"],
            "explanation": "If 3/4 = 15, divide 15 by 3 to find 1/4 = 5. Then multiply 5 × 4 = 20."
        },
        {
            "question_text": "2/5 of a number is 18. What is the whole number?",
            "correct_answer": "45",
            "wrong_answers": ["40", "35", "50"],
            "explanation": "If 2/5 = 18, divide 18 by 2 to find 1/5 = 9. Then multiply 9 × 5 = 45."
        },
        {
            "question_text": "5/8 of a number is 40. What is the whole number?",
            "correct_answer": "64",
            "wrong_answers": ["48", "56", "72"],
            "explanation": "If 5/8 = 40, divide 40 by 5 to find 1/8 = 8. Then multiply 8 × 8 = 64."
        },
        {
            "question_text": "3/10 of a number is 12. What is the whole number?",
            "correct_answer": "40",
            "wrong_answers": ["30", "36", "45"],
            "explanation": "If 3/10 = 12, divide 12 by 3 to find 1/10 = 4. Then multiply 4 × 10 = 40."
        },
        {
            "question_text": "7/9 of a number is 35. What is the whole number?",
            "correct_answer": "45",
            "wrong_answers": ["40", "50", "42"],
            "explanation": "If 7/9 = 35, divide 35 by 7 to find 1/9 = 5. Then multiply 5 × 9 = 45."
        },
        {
            "question_text": "1/3 of the apples in a basket are green. There are 12 green apples. How many apples are there in total?",
            "correct_answer": "36",
            "wrong_answers": ["24", "30", "33"],
            "explanation": "If 1/3 = 12, multiply 12 × 3 = 36 apples in total."
        },
        {
            "question_text": "2/7 of the students in a class are left-handed. If there are 8 left-handed students, how many students are in the class?",
            "correct_answer": "28",
            "wrong_answers": ["24", "32", "35"],
            "explanation": "If 2/7 = 8, divide 8 by 2 to find 1/7 = 4. Then multiply 4 × 7 = 28."
        },
        {
            "question_text": "5/6 of a ribbon measures 25 cm. What is the full length of the ribbon?",
            "correct_answer": "30 cm",
            "wrong_answers": ["28 cm", "32 cm", "36 cm"],
            "explanation": "If 5/6 = 25, divide 25 by 5 to find 1/6 = 5. Then multiply 5 × 6 = 30 cm."
        },
        {
            "question_text": "3/5 of a tank is filled with 24 litres of water. What is the capacity of the tank?",
            "correct_answer": "40 litres",
            "wrong_answers": ["30 litres", "36 litres", "45 litres"],
            "explanation": "If 3/5 = 24, divide 24 by 3 to find 1/5 = 8. Then multiply 8 × 5 = 40 litres."
        },
        {
            "question_text": "4/9 of a cake was eaten, which is 12 slices. How many slices were there in the whole cake?",
            "correct_answer": "27 slices",
            "wrong_answers": ["24 slices", "30 slices", "32 slices"],
            "explanation": "If 4/9 = 12, divide 12 by 4 to find 1/9 = 3. Then multiply 3 × 9 = 27 slices."
        },
        {
            "question_text": "2/3 of a number is 14. What is 1/3?",
            "correct_answer": "7",
            "wrong_answers": ["6", "8", "9"],
            "explanation": "If 2/3 = 14, divide 14 by 2 to find 1/3 = 7."
        },
        {
            "question_text": "5/6 of a number is 20. What is 1/2 of that number?",
            "correct_answer": "12",
            "wrong_answers": ["10", "15", "14"],
            "explanation": "If 5/6 = 20, divide 20 by 5 to find 1/6 = 4. The whole = 24. Half of 24 = 12."
        },
        {
            "question_text": "3/8 of a number is 24. What is the number?",
            "correct_answer": "64",
            "wrong_answers": ["56", "72", "60"],
            "explanation": "If 3/8 = 24, divide 24 by 3 to find 1/8 = 8. Then multiply 8 × 8 = 64."
        },
        {
            "question_text": "1/4 of a number is 9. What is 3/4?",
            "correct_answer": "27",
            "wrong_answers": ["24", "30", "21"],
            "explanation": "If 1/4 = 9, then 3/4 = 9 × 3 = 27."
        },
        {
            "question_text": "2/5 of a number is 10. What is 4/5?",
            "correct_answer": "20",
            "wrong_answers": ["25", "15", "18"],
            "explanation": "If 2/5 = 10, divide 10 by 2 to find 1/5 = 5. Then 4/5 = 5 × 4 = 20."
        }
    ]
    
    # Use shared utility function to process questions
    results = process_questions(
        level=level_4,
        topic=fractions_topic,
        questions_data=questions_data,
        verbose=True
    )
    
    print(f"\n✅ All questions are associated with Fractions topic for Year 4")
    
    # Legacy code below - kept for reference but not used
    """
    created_count = 0
    updated_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists (by text and level)
        existing = Question.objects.filter(
            level=level_4,
            question_text=q_data["question_text"],
            topic=fractions_topic
        ).first()
        
        if existing:
            # Update existing question
            question = existing
            question.explanation = q_data.get("explanation", "")
            # Ensure topic is set
            if not question.topic:
                question.topic = fractions_topic
            question.save()
            
            # Delete old answers to replace with correct ones
            Answer.objects.filter(question=question).delete()
            
            print(f"  🔄 Question {i} already exists, updating answers...")
            updated_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_4,
                topic=fractions_topic,  # Set topic directly on question
                question_text=q_data["question_text"],
                question_type='multiple_choice',
                difficulty=1,
                points=1,
                explanation=q_data.get("explanation", "")
            )
            print(f"  ✅ Created Question {i}: {q_data['question_text'][:50]}...")
            created_count += 1
        
        # Ensure question has topic set and level has topic associated
        if not question.topic:
            question.topic = fractions_topic
            question.save()
        question.level.topics.add(fractions_topic)
        
        # Create answers - mix correct and wrong answers
        all_answers = [q_data["correct_answer"]] + q_data["wrong_answers"]
        # Shuffle order for variety
        random.shuffle(all_answers)
        
        order = 0
        for answer_text in all_answers:
            is_correct = (answer_text == q_data["correct_answer"])
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
                order=order
            )
            order += 1
    """

if __name__ == "__main__":
    print("🔄 Setting up Fractions topic for Year 4...\n")
    result = setup_fractions_topic()
    
    if result:
        fractions_topic, level_4 = result
        print("\n" + "="*60)
        add_fractions_questions(fractions_topic, level_4)
        print("\n✅ Done!")

