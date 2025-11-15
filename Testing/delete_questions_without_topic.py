#!/usr/bin/env python
"""
Delete all questions without a topic assigned
WARNING: This will permanently delete questions from the database
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, StudentAnswer

def delete_questions_without_topic(dry_run=True):
    """
    Delete all questions that don't have a topic assigned
    
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
    
    # Get all questions without topic
    questions_without_topic = Question.objects.filter(
        topic__isnull=True
    ).select_related('level').order_by('level__level_number', 'id')
    
    total = questions_without_topic.count()
    
    if total == 0:
        print("[OK] No questions without topic found. Nothing to delete.")
        return
    
    print(f"[INFO] Found {total} question(s) without topic:\n")
    
    # Group by level for summary
    questions_by_level = {}
    for question in questions_without_topic:
        level_num = question.level.level_number if question.level else 0
        level_name = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
        
        if level_name not in questions_by_level:
            questions_by_level[level_name] = []
        questions_by_level[level_name].append(question)
    
    # Show summary
    print("Questions to be deleted (grouped by level):")
    print("-" * 80)
    for level_name in sorted(questions_by_level.keys(), key=lambda x: (
        int(x.split()[-1]) if x.split()[-1].isdigit() else 999
    )):
        count = len(questions_by_level[level_name])
        question_ids = [str(q.id) for q in questions_by_level[level_name][:5]]
        if count > 5:
            question_ids.append(f"... and {count - 5} more")
        print(f"  {level_name}: {count} questions (IDs: {', '.join(question_ids)})")
    
    print()
    print("=" * 80)
    print("DETAILED LIST")
    print("=" * 80)
    
    # Show first 20 questions in detail
    for i, question in enumerate(questions_without_topic[:20], 1):
        safe_text = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
        if len(question.question_text) > 60:
            safe_text += "..."
        level_name = f"Year {question.level.level_number}" if question.level and question.level.level_number < 100 else f"Level {question.level.level_number}" if question.level else "No level"
        print(f"  {i}. ID {question.id}: [{question.question_type}] {safe_text} | {level_name}")
    
    if total > 20:
        print(f"  ... and {total - 20} more questions")
    
    print()
    
    # Check for student answers
    questions_with_student_answers = []
    for question in questions_without_topic:
        if StudentAnswer.objects.filter(question=question).exists():
            student_answer_count = StudentAnswer.objects.filter(question=question).count()
            questions_with_student_answers.append({
                'id': question.id,
                'count': student_answer_count
            })
    
    if questions_with_student_answers:
        print("=" * 80)
        print("WARNING: Some questions have student answers")
        print("=" * 80)
        print("These questions have student attempts that will also be deleted:")
        for item in questions_with_student_answers[:10]:
            print(f"  Question ID {item['id']}: {item['count']} student answer(s)")
        if len(questions_with_student_answers) > 10:
            print(f"  ... and {len(questions_with_student_answers) - 10} more")
        print()
    
    if dry_run:
        print("=" * 80)
        print("[DRY RUN] This was a dry run. No questions were deleted.")
        print("         Run with --execute to actually delete these questions.")
        print("=" * 80)
        return
    
    # Actually delete
    print("[INFO] Starting deletion...\n")
    
    deleted_count = 0
    deleted_with_student_answers = 0
    
    for question in questions_without_topic:
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
        description='Delete all questions without a topic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This will permanently delete questions from the database!

Examples:
  # Dry run (show what would be deleted)
  python delete_questions_without_topic.py
  
  # Actually delete questions
  python delete_questions_without_topic.py --execute
        """
    )
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the questions (default is dry run)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if not dry_run:
        print("\n" + "!" * 80)
        print("WARNING: You are about to DELETE questions from the database!")
        print("!" * 80)
        print()
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("Cancelled. No questions were deleted.")
            sys.exit(0)
        print()
    
    delete_questions_without_topic(dry_run=dry_run)

