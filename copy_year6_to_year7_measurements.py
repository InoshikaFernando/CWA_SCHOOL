#!/usr/bin/env python
"""
Copy all Year 6 measurement questions to Year 7
This script duplicates questions, answers, and images from level 6 to level 7
"""
import os
import sys
import django
from shutil import copy2

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Question, Answer
from django.core.files import File

def copy_questions_with_answers(source_level, target_level):
    """Copy all questions from source_level to target_level, including answers and images"""
    
    # Get all questions from year 6
    source_questions = Question.objects.filter(level=source_level)
    
    if not source_questions.exists():
        print(f"❌ No questions found for level {source_level.level_number}")
        return
    
    print(f"📋 Found {source_questions.count()} questions in Year {source_level.level_number}")
    
    copied_count = 0
    skipped_count = 0
    
    for source_question in source_questions:
        # Check if question already exists in target level (by text)
        existing = Question.objects.filter(
            level=target_level,
            question_text=source_question.question_text
        ).first()
        
        if existing:
            print(f"  ⏭️  Question already exists in Year {target_level.level_number}: {source_question.question_text[:50]}...")
            skipped_count += 1
            continue
        
        # Create new question for year 7
        new_question = Question.objects.create(
            level=target_level,
            question_text=source_question.question_text,
            question_type=source_question.question_type,
            difficulty=source_question.difficulty,
            points=source_question.points,
            explanation=source_question.explanation,
            # Note: image will be copied separately
        )
        
        # Copy image if it exists
        if source_question.image:
            try:
                # Get the image file path
                image_path = source_question.image.path
                if os.path.exists(image_path):
                    # Open the file and save it to the new question
                    with open(image_path, 'rb') as f:
                        # Extract just the filename from the path
                        filename = os.path.basename(image_path)
                        new_question.image.save(filename, File(f), save=True)
                        print(f"  📷 Copied image: {filename}")
                else:
                    print(f"  ⚠️  Image file not found: {image_path}")
            except Exception as e:
                print(f"  ⚠️  Error copying image: {e}")
        
        # Copy all answers for this question
        source_answers = Answer.objects.filter(question=source_question)
        for source_answer in source_answers:
            Answer.objects.create(
                question=new_question,
                answer_text=source_answer.answer_text,
                is_correct=source_answer.is_correct,
                order=source_answer.order
            )
        
        print(f"  ✅ Copied: {source_question.question_text[:50]}... ({source_answers.count()} answers)")
        copied_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Copied: {copied_count} questions")
    print(f"   ⏭️  Skipped: {skipped_count} questions (already exist)")
    print(f"   📝 Total: {source_questions.count()} questions processed")

def main():
    """Main function to copy year 6 questions to year 7"""
    
    # Get level 6 and level 7
    level_6 = Level.objects.filter(level_number=6).first()
    level_7 = Level.objects.filter(level_number=7).first()
    
    if not level_6:
        print("❌ Error: Year 6 level not found!")
        return
    
    if not level_7:
        print("❌ Error: Year 7 level not found!")
        return
    
    print(f"🔄 Copying questions from Year {level_6.level_number} to Year {level_7.level_number}")
    print(f"   Source: {level_6}")
    print(f"   Target: {level_7}\n")
    
    # Confirm before proceeding
    response = input("⚠️  This will copy all Year 6 questions to Year 7. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Copy questions
    copy_questions_with_answers(level_6, level_7)
    
    print("\n✅ Done! All Year 6 measurement questions have been copied to Year 7.")
    print("   Remember to reload your web app on PythonAnywhere after deploying this change.")

if __name__ == "__main__":
    main()

