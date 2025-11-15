#!/usr/bin/env python
"""
Delete duplicate questions from the database
Finds questions with the same question_text and optionally same image,
keeps one (preferably with most answers), and deletes the rest
WARNING: This will permanently delete questions from the database
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, StudentAnswer
from collections import defaultdict
from django.db.models import Count

def delete_duplicate_questions(dry_run=True, check_image=True):
    """
    Delete duplicate questions
    
    Args:
        dry_run: If True, only show what would be deleted without making changes
        check_image: If True, also consider image when identifying duplicates
    """
    
    print("=" * 80)
    if dry_run:
        print("DRY RUN MODE - No questions will be deleted")
    else:
        print("EXECUTION MODE - Questions WILL BE DELETED")
    print("=" * 80)
    print()
    
    print("[INFO] Finding duplicate questions...\n")
    
    # Get all questions
    all_questions = Question.objects.all().select_related('level', 'topic').annotate(
        answer_count=Count('answers')
    ).order_by('id')
    
    # Group questions by question_text
    questions_by_text = defaultdict(list)
    
    for question in all_questions:
        questions_by_text[question.question_text].append(question)
    
    # Find duplicates (same question text)
    text_duplicates = {text: questions for text, questions in questions_by_text.items() if len(questions) > 1}
    
    if not text_duplicates:
        print("[OK] No duplicate questions found!")
        return
    
    print(f"[INFO] Found {len(text_duplicates)} question text(s) with duplicates\n")
    
    # Analyze duplicates and determine which to keep/delete
    duplicates_to_delete = []
    total_duplicates = 0
    
    for question_text, questions in text_duplicates.items():
        # If checking images, group by image as well
        if check_image:
            questions_by_image = defaultdict(list)
            for q in questions:
                image_name = q.image.name if q.image else "NO_IMAGE"
                questions_by_image[image_name].append(q)
            
            # Process each image group separately
            for image_name, q_list in questions_by_image.items():
                if len(q_list) > 1:
                    # These are true duplicates (same text + same image)
                    # Choose which to keep (prefer one with most answers, then lowest ID)
                    q_list.sort(key=lambda x: (-x.answer_count, x.id))
                    question_to_keep = q_list[0]
                    questions_to_delete = q_list[1:]
                    
                    for q in questions_to_delete:
                        duplicates_to_delete.append({
                            'question': q,
                            'keep': question_to_keep,
                            'reason': 'Same text and image'
                        })
                        total_duplicates += 1
        else:
            # Just group by text, ignore images
            questions.sort(key=lambda x: (-x.answer_count, x.id))
            question_to_keep = questions[0]
            questions_to_delete = questions[1:]
            
            for q in questions_to_delete:
                duplicates_to_delete.append({
                    'question': q,
                    'keep': question_to_keep,
                    'reason': 'Same text'
                })
                total_duplicates += 1
    
    if not duplicates_to_delete:
        print("[OK] No duplicate questions to delete!")
        return
    
    print(f"[INFO] Found {total_duplicates} duplicate question(s) to delete:\n")
    print("=" * 80)
    print("DUPLICATES TO BE DELETED")
    print("=" * 80)
    
    # Group by the question being kept
    by_kept_question = defaultdict(list)
    for item in duplicates_to_delete:
        kept_id = item['keep'].id
        by_kept_question[kept_id].append(item)
    
    for kept_id, items in sorted(by_kept_question.items()):
        kept_question = items[0]['keep']
        safe_text = kept_question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
        if len(kept_question.question_text) > 60:
            safe_text += "..."
        
        print(f"\nKeeping Question ID {kept_id}:")
        print(f"  Text: {safe_text}")
        print(f"  Level: {kept_question.level}")
        print(f"  Topic: {kept_question.topic.name if kept_question.topic else 'None'}")
        print(f"  Answers: {kept_question.answer_count}")
        print(f"  Will delete {len(items)} duplicate(s):")
        
        for item in items:
            q = item['question']
            safe_text_del = q.question_text[:50].encode('ascii', 'ignore').decode('ascii')
            image_info = q.image.name if q.image else "(no image)"
            student_answer_count = StudentAnswer.objects.filter(question=q).count()
            
            print(f"    - ID {q.id}: Level {q.level}, Topic {q.topic.name if q.topic else 'None'}, "
                  f"Answers {q.answer_count}, Image {image_info}")
            if student_answer_count > 0:
                print(f"      WARNING: Has {student_answer_count} student answer(s)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total duplicate questions to delete: {total_duplicates}")
    print(f"Unique questions to keep: {len(by_kept_question)}")
    
    # Count questions with student answers
    questions_with_student_answers = sum(
        1 for item in duplicates_to_delete
        if StudentAnswer.objects.filter(question=item['question']).exists()
    )
    
    if questions_with_student_answers > 0:
        print(f"Duplicates with student answers: {questions_with_student_answers}")
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
    
    for item in duplicates_to_delete:
        question = item['question']
        question_id = question.id
        has_student_answers = StudentAnswer.objects.filter(question=question).exists()
        
        if has_student_answers:
            student_answer_count = StudentAnswer.objects.filter(question=question).count()
            print(f"[WARNING] Deleting Question ID {question_id} with {student_answer_count} student answer(s)...")
            deleted_with_student_answers += 1
        
        # Delete the question (cascade will delete answers and student answers)
        question.delete()
        deleted_count += 1
        
        if deleted_count % 10 == 0:
            print(f"  [PROGRESS] Deleted {deleted_count} duplicate questions...")
    
    print("\n" + "=" * 80)
    print("DELETION SUMMARY")
    print("=" * 80)
    print(f"Total duplicate questions deleted: {deleted_count}")
    print(f"Duplicates with student answers deleted: {deleted_with_student_answers}")
    print("\n[OK] Deletion complete!")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Delete duplicate questions from the database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This will permanently delete questions from the database!

The script will:
- Find questions with the same question_text (and optionally same image)
- Keep the question with the most answers (or lowest ID if tied)
- Delete all other duplicates

Examples:
  # Dry run (show what would be deleted)
  python delete_duplicate_questions.py
  
  # Actually delete duplicates
  python delete_duplicate_questions.py --execute
  
  # Delete duplicates without checking images
  python delete_duplicate_questions.py --execute --no-image-check
        """
    )
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the questions (default is dry run)')
    parser.add_argument('--no-image-check', action='store_true',
                       help='Do not check images when identifying duplicates')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    check_image = not args.no_image_check
    
    if not dry_run:
        print("\n" + "!" * 80)
        print("WARNING: You are about to DELETE duplicate questions from the database!")
        print("!" * 80)
        print()
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("Cancelled. No questions were deleted.")
            sys.exit(0)
        print()
    
    delete_duplicate_questions(dry_run=dry_run, check_image=check_image)

