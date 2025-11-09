#!/usr/bin/env python
"""
Update image for spacecraft volume question in production
This will set the image path even if the file doesn't exist locally
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question

# Find the question by text (works for both local and production)
question = Question.objects.filter(
    question_text__icontains="volume of the spacecraft"
).first()

if not question:
    print("Question not found!")
    sys.exit(1)

print(f"Found question ID: {question.id}")
q_text = question.question_text.encode('ascii', 'ignore').decode('ascii')
print(f"Question text: {q_text}")
print(f"Current image: {question.image.name if question.image else 'No image set'}")

# Set the image path (same as in script)
image_path = "questions/year6/measurements/image23.png"
question.image.name = image_path
question.save()

print(f"\n[OK] Updated image path to: {image_path}")
print(f"New image path: {question.image.name}")
print("\nThe image should now display in production!")

