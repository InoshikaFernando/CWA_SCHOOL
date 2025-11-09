#!/usr/bin/env python
"""
Add "Fractions" topic for Year 3 and all associated questions
This script creates the topic, associates it with Year 3, and adds fraction questions
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

def setup_fractions_topic():
    """Create Fractions topic and associate with Year 3"""
    
    # Get or create the "Fractions" topic
    fractions_topic, created = Topic.objects.get_or_create(name="Fractions")
    if created:
        print(f"✅ Created topic: Fractions")
    else:
        print(f"ℹ️  Topic already exists: Fractions")
    
    # Get Year 3 level
    level_3 = Level.objects.filter(level_number=3).first()
    
    if not level_3:
        print("❌ Error: Year 3 level not found!")
        return None
    
    print(f"📋 Found Year 3: {level_3}")
    
    # Check if Fractions is already associated
    if level_3.topics.filter(name="Fractions").exists():
        print("ℹ️  Year 3 already has Fractions topic associated.")
        print(f"   Current topics for Year 3: {', '.join([t.name for t in level_3.topics.all()])}")
    else:
        # Associate Fractions topic with Year 3
        level_3.topics.add(fractions_topic)
        print(f"✅ Successfully associated Fractions topic with Year 3")
        print(f"   Year 3 now has topics: {', '.join([t.name for t in level_3.topics.all()])}")
    
    return fractions_topic, level_3

def add_fractions_questions(fractions_topic, level_3):
    """Add Fractions questions for Year 3"""
    
    # Define questions - numerator and denominator questions
    questions_data = [
        # Numerator questions
        {
            "question_text": "What is the numerator of 1/4?",
            "correct_answer": "1",
            "wrong_answers": ["4", "5", "3"],
            "explanation": "The numerator is the top number in a fraction. In 1/4, the numerator is 1."
        },
        {
            "question_text": "What is the numerator of 2/5?",
            "correct_answer": "2",
            "wrong_answers": ["5", "3", "7"],
            "explanation": "The numerator is the top number in a fraction. In 2/5, the numerator is 2."
        },
        {
            "question_text": "What is the numerator of 3/6?",
            "correct_answer": "3",
            "wrong_answers": ["6", "9", "2"],
            "explanation": "The numerator is the top number in a fraction. In 3/6, the numerator is 3."
        },
        {
            "question_text": "What is the numerator of 4/7?",
            "correct_answer": "4",
            "wrong_answers": ["7", "11", "3"],
            "explanation": "The numerator is the top number in a fraction. In 4/7, the numerator is 4."
        },
        {
            "question_text": "What is the numerator of 5/8?",
            "correct_answer": "5",
            "wrong_answers": ["8", "13", "3"],
            "explanation": "The numerator is the top number in a fraction. In 5/8, the numerator is 5."
        },
        {
            "question_text": "What is the numerator of 2/3?",
            "correct_answer": "2",
            "wrong_answers": ["3", "5", "1"],
            "explanation": "The numerator is the top number in a fraction. In 2/3, the numerator is 2."
        },
        {
            "question_text": "What is the numerator of 3/4?",
            "correct_answer": "3",
            "wrong_answers": ["4", "7", "1"],
            "explanation": "The numerator is the top number in a fraction. In 3/4, the numerator is 3."
        },
        {
            "question_text": "What is the numerator of 1/2?",
            "correct_answer": "1",
            "wrong_answers": ["2", "3", "0"],
            "explanation": "The numerator is the top number in a fraction. In 1/2, the numerator is 1."
        },
        {
            "question_text": "What is the numerator of 6/9?",
            "correct_answer": "6",
            "wrong_answers": ["9", "15", "3"],
            "explanation": "The numerator is the top number in a fraction. In 6/9, the numerator is 6."
        },
        {
            "question_text": "What is the numerator of 7/10?",
            "correct_answer": "7",
            "wrong_answers": ["10", "17", "3"],
            "explanation": "The numerator is the top number in a fraction. In 7/10, the numerator is 7."
        },
        # Denominator questions
        {
            "question_text": "What is the denominator of 1/8?",
            "correct_answer": "8",
            "wrong_answers": ["1", "9", "7"],
            "explanation": "The denominator is the bottom number in a fraction. In 1/8, the denominator is 8."
        },
        {
            "question_text": "What is the denominator of 2/5?",
            "correct_answer": "5",
            "wrong_answers": ["2", "7", "3"],
            "explanation": "The denominator is the bottom number in a fraction. In 2/5, the denominator is 5."
        },
        {
            "question_text": "What is the denominator of 3/6?",
            "correct_answer": "6",
            "wrong_answers": ["3", "9", "5"],
            "explanation": "The denominator is the bottom number in a fraction. In 3/6, the denominator is 6."
        },
        {
            "question_text": "What is the denominator of 4/7?",
            "correct_answer": "7",
            "wrong_answers": ["4", "11", "5"],
            "explanation": "The denominator is the bottom number in a fraction. In 4/7, the denominator is 7."
        },
        {
            "question_text": "What is the denominator of 5/8?",
            "correct_answer": "8",
            "wrong_answers": ["5", "13", "7"],
            "explanation": "The denominator is the bottom number in a fraction. In 5/8, the denominator is 8."
        },
        {
            "question_text": "What is the denominator of 2/3?",
            "correct_answer": "3",
            "wrong_answers": ["2", "5", "1"],
            "explanation": "The denominator is the bottom number in a fraction. In 2/3, the denominator is 3."
        },
        {
            "question_text": "What is the denominator of 3/4?",
            "correct_answer": "4",
            "wrong_answers": ["3", "7", "1"],
            "explanation": "The denominator is the bottom number in a fraction. In 3/4, the denominator is 4."
        },
        {
            "question_text": "What is the denominator of 1/2?",
            "correct_answer": "2",
            "wrong_answers": ["1", "3", "0"],
            "explanation": "The denominator is the bottom number in a fraction. In 1/2, the denominator is 2."
        },
        {
            "question_text": "What is the denominator of 6/9?",
            "correct_answer": "9",
            "wrong_answers": ["6", "15", "3"],
            "explanation": "The denominator is the bottom number in a fraction. In 6/9, the denominator is 9."
        },
        {
            "question_text": "What is the denominator of 7/10?",
            "correct_answer": "10",
            "wrong_answers": ["7", "17", "3"],
            "explanation": "The denominator is the bottom number in a fraction. In 7/10, the denominator is 10."
        },
        # Mixed questions - identify numerator or denominator
        {
            "question_text": "In the fraction 1/4, which number is the numerator?",
            "correct_answer": "1",
            "wrong_answers": ["4", "3", "6"],
            "explanation": "The numerator is the top number. In 1/4, the numerator is 1."
        },
        {
            "question_text": "In the fraction 1/4, which number is the denominator?",
            "correct_answer": "4",
            "wrong_answers": ["1", "3", "5"],
            "explanation": "The denominator is the bottom number. In 1/4, the denominator is 4."
        },
        {
            "question_text": "In the fraction 2/5, which number is the numerator?",
            "correct_answer": "2",
            "wrong_answers": ["5", "7", "3"],
            "explanation": "The numerator is the top number. In 2/5, the numerator is 2."
        },
        {
            "question_text": "In the fraction 2/5, which number is the denominator?",
            "correct_answer": "5",
            "wrong_answers": ["2", "7", "3"],
            "explanation": "The denominator is the bottom number. In 2/5, the denominator is 5."
        },
        {
            "question_text": "In the fraction 3/6, which number is the numerator?",
            "correct_answer": "3",
            "wrong_answers": ["6", "9", "2"],
            "explanation": "The numerator is the top number. In 3/6, the numerator is 3."
        },
        {
            "question_text": "In the fraction 3/6, which number is the denominator?",
            "correct_answer": "6",
            "wrong_answers": ["3", "9", "5"],
            "explanation": "The denominator is the bottom number. In 3/6, the denominator is 6."
        },
        # Fraction comparison questions
        {
            "question_text": "What is the largest fraction between 3/5 and 3/4?",
            "correct_answer": "3/4",
            "wrong_answers": ["3/5", "They are equal", "Cannot compare"],
            "explanation": "To compare 3/5 and 3/4, we can use a common denominator. 3/5 = 12/20 and 3/4 = 15/20. Since 15/20 > 12/20, 3/4 is larger than 3/5."
        },
        {
            "question_text": "What is the largest fraction between 1/2 and 1/3?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/3", "They are equal", "Cannot compare"],
            "explanation": "To compare 1/2 and 1/3, we can use a common denominator. 1/2 = 3/6 and 1/3 = 2/6. Since 3/6 > 2/6, 1/2 is larger than 1/3."
        },
        {
            "question_text": "What is the largest fraction between 2/5 and 2/7?",
            "correct_answer": "2/5",
            "wrong_answers": ["2/7", "They are equal", "Cannot compare"],
            "explanation": "To compare 2/5 and 2/7, we can use a common denominator. 2/5 = 14/35 and 2/7 = 10/35. Since 14/35 > 10/35, 2/5 is larger than 2/7. When numerators are the same, the fraction with the smaller denominator is larger."
        },
        {
            "question_text": "What is the largest fraction between 1/4 and 1/8?",
            "correct_answer": "1/4",
            "wrong_answers": ["1/8", "They are equal", "Cannot compare"],
            "explanation": "To compare 1/4 and 1/8, we can use a common denominator. 1/4 = 2/8 and 1/8 = 1/8. Since 2/8 > 1/8, 1/4 is larger than 1/8. When numerators are the same, the fraction with the smaller denominator is larger."
        },
        # Image-based fraction questions
        {
            "question_text": "What is the fraction shown in the image?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/4", "1/3", "3/4"],
            "explanation": "The image shows 1 part out of 2 equal parts, which is 1/2.",
            "image_path": "questions/year3/fractions/image1.png"
        },
        {
            "question_text": "What fraction is represented in the picture?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/4", "2/4", "1/3"],
            "explanation": "Looking at the image, 1 part out of 2 equal parts is shaded, which represents 1/2.",
            "image_path": "questions/year3/fractions/image1.png"
        },
        {
            "question_text": "What is the fraction of the shaded part in the image?",
            "correct_answer": "1/2",
            "wrong_answers": ["1/4", "3/4", "2/4"],
            "explanation": "The image shows 1 shaded part out of 2 total parts, which is 1/2.",
            "image_path": "questions/year3/fractions/image1.png"
        },
        # Image-based fraction questions using image2.png (1/4)
        {
            "question_text": "What is the fraction shown in the image?",
            "correct_answer": "1/4",
            "wrong_answers": ["1/2", "1/3", "3/4"],
            "explanation": "The image shows 1 part out of 4 equal parts, which is 1/4.",
            "image_path": "questions/year3/fractions/image2.png"
        },
        {
            "question_text": "What fraction is represented in the picture?",
            "correct_answer": "1/4",
            "wrong_answers": ["1/2", "2/4", "1/3"],
            "explanation": "Looking at the image, 1 part out of 4 equal parts is shaded, which represents 1/4.",
            "image_path": "questions/year3/fractions/image2.png"
        },
        {
            "question_text": "What is the fraction of the coloured part in the image?",
            "correct_answer": "1/4",
            "wrong_answers": ["1/2", "3/4", "2/4"],
            "explanation": "The image shows 1 coloured part out of 4 total parts, which is 1/4.",
            "image_path": "questions/year3/fractions/image2.png"
        },
        # Image-based fraction questions using image3.png (1/5)
        {
            "question_text": "What is the fraction shown in the image?",
            "correct_answer": "1/5",
            "wrong_answers": ["1/4", "1/3", "2/5"],
            "explanation": "The image shows 1 part out of 5 equal parts, which is 1/5.",
            "image_path": "questions/year3/fractions/image3.png"
        },
        {
            "question_text": "What fraction is represented in the picture?",
            "correct_answer": "1/5",
            "wrong_answers": ["1/4", "2/5", "1/3"],
            "explanation": "Looking at the image, 1 part out of 5 equal parts is shaded, which represents 1/5.",
            "image_path": "questions/year3/fractions/image3.png"
        },
        {
            "question_text": "What is the fraction of the coloured part in the image?",
            "correct_answer": "1/5",
            "wrong_answers": ["1/4", "3/5", "2/5"],
            "explanation": "The image shows 1 coloured part out of 5 total parts, which is 1/5.",
            "image_path": "questions/year3/fractions/image3.png"
        },
        # Image-based fraction questions using image4.png (2/6)
        {
            "question_text": "What is the fraction shown in the image?",
            "correct_answer": "2/6",
            "wrong_answers": ["1/6", "1/3", "3/6"],
            "explanation": "The image shows 2 parts out of 6 equal parts, which is 2/6.",
            "image_path": "questions/year3/fractions/image4.png"
        },
        {
            "question_text": "What fraction is represented in the picture?",
            "correct_answer": "2/6",
            "wrong_answers": ["1/6", "3/6", "1/3"],
            "explanation": "Looking at the image, 2 parts out of 6 equal parts are shaded, which represents 2/6.",
            "image_path": "questions/year3/fractions/image4.png"
        },
        {
            "question_text": "What is the fraction of the coloured part in the image?",
            "correct_answer": "2/6",
            "wrong_answers": ["1/6", "4/6", "3/6"],
            "explanation": "The image shows 2 coloured parts out of 6 total parts, which is 2/6.",
            "image_path": "questions/year3/fractions/image4.png"
        },
        # Image-based fraction questions using image5.png (5/6)
        {
            "question_text": "What is the fraction shown in the image?",
            "correct_answer": "5/6",
            "wrong_answers": ["4/6", "1/6", "3/6"],
            "explanation": "The image shows 5 parts out of 6 equal parts, which is 5/6.",
            "image_path": "questions/year3/fractions/image5.png"
        },
        {
            "question_text": "What fraction is represented in the picture?",
            "correct_answer": "5/6",
            "wrong_answers": ["4/6", "1/6", "3/6"],
            "explanation": "Looking at the image, 5 parts out of 6 equal parts are shaded, which represents 5/6.",
            "image_path": "questions/year3/fractions/image5.png"
        },
        {
            "question_text": "What is the fraction of the coloured part in the image?",
            "correct_answer": "5/6",
            "wrong_answers": ["4/6", "1/6", "2/6"],
            "explanation": "The image shows 5 coloured parts out of 6 total parts, which is 5/6.",
            "image_path": "questions/year3/fractions/image5.png"
        },
    ]
    
    print(f"\n📝 Adding {len(questions_data)} Fractions questions (numerator and denominator) for Year 3...\n")
    
    created_count = 0
    updated_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_3,
            question_text=q_data["question_text"]
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
                level=level_3,
                topic=fractions_topic,  # Set topic directly on question
                question_text=q_data["question_text"],
                question_type='multiple_choice',
                difficulty=1,
                points=1,
                explanation=q_data.get("explanation", "")
            )
            print(f"  ✅ Created Question {i}: {q_data['question_text'][:50]}...")
            created_count += 1
        
        # Add/update image if specified
        if "image_path" in q_data:
            image_path = q_data["image_path"]
            # Check if image file exists
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
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count} questions")
    print(f"   🔄 Updated: {updated_count} questions")
    print(f"\n✅ All questions are associated with Fractions topic for Year 3")

if __name__ == "__main__":
    print("🔄 Setting up Fractions topic for Year 3...\n")
    result = setup_fractions_topic()
    
    if result:
        fractions_topic, level_3 = result
        print("\n" + "="*60)
        add_fractions_questions(fractions_topic, level_3)
        print("\n✅ Done!")

