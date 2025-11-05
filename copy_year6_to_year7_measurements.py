#!/usr/bin/env python
"""
Copy all Year 6 measurement questions to Year 7
This script duplicates questions and answers from level 6 to level 7.
Images are reused (shared) rather than duplicated.

Usage:
    python copy_year6_to_year7_measurements.py [--yes] [--no-images]
    
    --yes: Skip confirmation prompts (non-interactive mode)
    --no-images: Don't copy/reuse images
"""
import os
import sys
import django
import argparse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Question, Answer
from django.core.files import File

def copy_questions_with_answers(source_level, target_level, copy_images=True):
    """Copy all questions from source_level to target_level, including answers and images
    
    Args:
        source_level: Level to copy questions from (Year 6)
        target_level: Level to copy questions to (Year 7)
        copy_images: If True, copy image files. If False, skip images (questions will have no images).
    """
    
    # Get all questions from year 6
    source_questions = Question.objects.filter(level=source_level)
    
    if not source_questions.exists():
        print(f"❌ No questions found for level {source_level.level_number}")
        return
    
    print(f"📋 Found {source_questions.count()} questions in Year {source_level.level_number}")
    
    copied_count = 0
    skipped_count = 0
    
    for source_question in source_questions:
        # Check if exact same question already exists (by text AND image)
        # Note: We allow copying questions with same text but different images
        existing_questions = Question.objects.filter(
            level=target_level,
            question_text=source_question.question_text
        )
        
        # If question has an image, check if one with same text AND same image path exists
        if source_question.image:
            source_image_name = source_question.image.name
            existing = None
            for q in existing_questions:
                if q.image and q.image.name == source_image_name:
                    existing = q
                    break
        else:
            # If no image, check if any existing question has no image
            existing = existing_questions.filter(image__isnull=True).first()
            if not existing:
                existing = existing_questions.first() if existing_questions.exists() else None
        
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
        
        # Reuse image if it exists (share the same image file, don't duplicate)
        # NOTE: Year 6 measurement questions use images (stored in media/questions/year6/measurements/)
        # Instead of copying the file, we'll reuse the same image file path for Year 7 questions
        if copy_images and source_question.image:
            try:
                # Get the relative path (name) of the image (e.g., 'questions/year6/measurements/image1.png')
                # This is stored relative to MEDIA_ROOT in Django
                image_name = source_question.image.name
                
                # Assign the same image to the new question (reuse the file, don't copy)
                # Django will just reference the same file path
                new_question.image = source_question.image
                new_question.save(update_fields=['image'])
                
                # Extract filename for display
                filename = os.path.basename(image_name)
                print(f"  📷 Reusing image: {filename}")
            except Exception as e:
                print(f"  ⚠️  Error setting image: {e}")
        
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
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Copy Year 6 measurement questions to Year 7')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompts (non-interactive mode)')
    parser.add_argument('--no-images', action='store_true', help='Don\'t copy/reuse images')
    args = parser.parse_args()
    
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
    
    # Determine if we should copy images
    if args.no_images:
        copy_images = False
        print("   ⚠️  Will skip images (questions will have no images)")
    elif args.yes:
        # Non-interactive mode: default to including images
        copy_images = True
        print("   ✅ Will reuse same image files (no duplication)")
    else:
        # Interactive mode: ask user
        print("ℹ️  Year 6 measurement questions include images (diagrams, rulers, etc.)")
        copy_images_input = input("   Include images for Year 7? (yes/no, default=yes): ").strip().lower()
        copy_images = copy_images_input != 'no'
        if copy_images:
            print("   ✅ Will reuse same image files (no duplication)")
        else:
            print("   ⚠️  Will skip images (questions will have no images)")
    
    print()
    
    # Confirm before proceeding (unless --yes flag is used)
    if not args.yes:
        response = input("⚠️  This will copy all Year 6 questions to Year 7. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
    
    # Copy questions
    copy_questions_with_answers(level_6, level_7, copy_images=copy_images)
    
    print("\n✅ Done! All Year 6 measurement questions have been copied to Year 7.")
    print("   Remember to reload your web app on PythonAnywhere after deploying this change.")

if __name__ == "__main__":
    main()

