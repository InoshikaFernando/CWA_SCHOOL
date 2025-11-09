#!/usr/bin/env python
"""
Delete questions with invalid image paths
Invalid paths are those directly under questions/* (e.g., questions/image1.png)
instead of proper subdirectories (e.g., questions/year6/measurements/image1.png)
WARNING: This will permanently delete questions from the database
"""
import os
import sys
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, StudentAnswer
from django.db.models import Count

def is_invalid_image_path(image_path):
    """
    Check if image path is invalid
    Valid: questions/year6/measurements/image1.png (year*/topic/filename)
    Invalid: questions/image1.png (directly under questions/)
    Invalid: questions/year6/image1.png (missing topic subdirectory)
    """
    if not image_path:
        return False
    
    # Normalize path separators
    image_path = image_path.replace('\\', '/')
    
    # Valid pattern: questions/year*/topic/filename.ext
    # Must have at least: questions/year*/topic/filename
    # Pattern breakdown:
    # - ^questions/ - starts with questions/
    # - year\d+/ - year followed by digits (year2, year3, year5, etc.)
    # - [^/]+/ - topic name (one or more non-slash chars)
    # - [^/]+$ - filename (one or more non-slash chars at end)
    valid_pattern = r'^questions/year\d+/[^/]+/[^/]+$'
    
    # If it doesn't match the valid pattern, it's invalid
    return not bool(re.match(valid_pattern, image_path))

def delete_questions_with_invalid_image_paths(dry_run=True):
    """
    Delete questions with invalid image paths
    
    Args:
        dry_run: If True, only show what would be deleted without making changes
    """
    
    print("=" * 80)
    if dry_run:
        print("DRY RUN MODE - No questions will be deleted")
    else:
        print("EXECUTION MODE - Questions WILL BE DELETED")
    print("=" * 80)
    print()
    
    print("[INFO] Finding questions with invalid image paths...\n")
    
    # Get all questions with images
    questions_with_images = Question.objects.exclude(
        image__isnull=True
    ).exclude(
        image=''
    ).select_related('level', 'topic').annotate(
        answer_count=Count('answers')
    ).order_by('id')
    
    invalid_questions = []
    
    for question in questions_with_images:
        image_path = question.image.name if question.image else None
        
        if is_invalid_image_path(image_path):
            student_answer_count = StudentAnswer.objects.filter(question=question).count()
            invalid_questions.append({
                'question': question,
                'image_path': image_path,
                'student_answer_count': student_answer_count
            })
    
    if not invalid_questions:
        print("[OK] No questions with invalid image paths found!")
        return
    
    print(f"[INFO] Found {len(invalid_questions)} question(s) with invalid image paths:\n")
    print("=" * 80)
    print("QUESTIONS WITH INVALID IMAGE PATHS")
    print("=" * 80)
    
    for item in invalid_questions:
        q = item['question']
        safe_text = q.question_text[:60].encode('ascii', 'ignore').decode('ascii')
        if len(q.question_text) > 60:
            safe_text += "..."
        
        print(f"\nQuestion ID {q.id}:")
        print(f"  Text: {safe_text}")
        print(f"  Level: {q.level}")
        print(f"  Topic: {q.topic.name if q.topic else 'None'}")
        print(f"  Answers: {item['student_answer_count']}")
        print(f"  Invalid Image Path: {item['image_path']}")
        
        if item['student_answer_count'] > 0:
            print(f"  WARNING: Has {item['student_answer_count']} student answer(s)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total questions with invalid image paths: {len(invalid_questions)}")
    
    # Count questions with student answers
    questions_with_student_answers = sum(
        1 for item in invalid_questions
        if item['student_answer_count'] > 0
    )
    
    if questions_with_student_answers > 0:
        print(f"Questions with student answers: {questions_with_student_answers}")
        print("  (Student answers will also be deleted)")
    
    if dry_run:
        print("\n" + "=" * 80)
        print("[DRY RUN] This was a dry run. No questions were deleted.")
        print("         Run with --execute to actually delete these questions.")
        print("=" * 80)
        return
    
    # Actually delete
    print("\n[INFO] Starting deletion...\n")
    
    deleted_count = 0
    deleted_with_student_answers = 0
    
    for item in invalid_questions:
        question = item['question']
        question_id = question.id
        has_student_answers = item['student_answer_count'] > 0
        
        if has_student_answers:
            print(f"[WARNING] Deleting Question ID {question_id} with {item['student_answer_count']} student answer(s)...")
            deleted_with_student_answers += 1
        
        # Delete the question (cascade will delete answers and student answers)
        question.delete()
        deleted_count += 1
        
        if deleted_count % 10 == 0:
            print(f"  [PROGRESS] Deleted {deleted_count} questions...")
    
    print("\n" + "=" * 80)
    print("DELETION SUMMARY")
    print("=" * 80)
    print(f"Total questions deleted: {deleted_count}")
    print(f"Questions with student answers deleted: {deleted_with_student_answers}")
    print("\n[OK] Deletion complete!")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Delete questions with invalid image paths (directly under questions/*)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This will permanently delete questions from the database!

The script will:
- Find questions with image paths directly under questions/* (e.g., questions/image1.png)
- Delete these questions (valid paths are like questions/year6/measurements/image1.png)

Examples:
  # Dry run (show what would be deleted)
  python delete_questions_with_invalid_image_paths.py
  
  # Actually delete questions
  python delete_questions_with_invalid_image_paths.py --execute
        """
    )
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the questions (default is dry run)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if not dry_run:
        print("\n" + "!" * 80)
        print("WARNING: You are about to DELETE questions with invalid image paths!")
        print("!" * 80)
        print()
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("Cancelled. No questions were deleted.")
            sys.exit(0)
        print()
    
    delete_questions_with_invalid_image_paths(dry_run=dry_run)

