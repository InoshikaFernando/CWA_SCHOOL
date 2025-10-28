#!/usr/bin/env python
"""
Script to add questions with images to the database.

Usage:
1. Place your image file in this directory
2. Run: python add_question_with_image.py
3. Follow the prompts to enter question details
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from practice.models import Question, Answer, Level
from django.core.files import File

def add_question():
    level = Level.objects.get(level_number=5)
    
    # Get question details
    image_path = input("Enter image file path (e.g., q1_diagram.png): ").strip()
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found!")
        return
    
    question_text = input("Enter question text: ").strip()
    
    print("\nEnter answer options (press Enter on empty line when done):")
    answers = []
    while True:
        answer = input("Answer option: ").strip()
        if not answer:
            break
        is_correct = input("Is this the correct answer? (yes/no): ").strip().lower() == 'yes'
        answers.append({'text': answer, 'is_correct': is_correct})
    
    explanation = input("\nEnter explanation (optional): ").strip()
    
    # Create question
    question = Question.objects.create(
        level=level,
        question_text=question_text,
        explanation=explanation
    )
    
    # Add image
    with open(image_path, 'rb') as f:
        question.image.save(os.path.basename(image_path), File(f), save=True)
    
    # Add answers
    for order, ans in enumerate(answers):
        Answer.objects.create(
            question=question,
            answer_text=ans['text'],
            is_correct=ans['is_correct'],
            order=order
        )
    
    print(f"\n✅ Question created successfully! ID: {question.id}")

if __name__ == '__main__':
    add_question()

