#!/usr/bin/env python
"""
Check question image for "What is the volume of the spacecraft?"
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question

# Find the question
question = Question.objects.filter(
    question_text__icontains="volume of the spacecraft"
).first()

if question:
    print(f"Question ID: {question.id}")
    q_text = question.question_text.encode('ascii', 'ignore').decode('ascii')
    print(f"Question Text: {q_text}")
    print(f"Image Path: {question.image.name if question.image else 'No image set'}")
    if question.image:
        print(f"Image URL: {question.image.url if question.image else 'N/A'}")
        # Check if file exists
        from django.conf import settings
        if question.image:
            full_path = os.path.join(settings.MEDIA_ROOT, question.image.name)
            exists = os.path.exists(full_path)
            print(f"Image file exists: {exists}")
            if exists:
                print(f"Full path: {full_path}")
            else:
                print(f"Expected path: {full_path}")
else:
    print("Question not found!")

