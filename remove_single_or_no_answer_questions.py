#!/usr/bin/env python
"""
Remove questions that have only one answer or no answers
This script helps clean up incomplete questions in the database
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, StudentAnswer
from django.db.models import Count

def remove_single_or_no_answer_questions(dry_run=True, level_number=None, topic_name=None):
    """
    Remove questions with 0 or 1 answer
    
    Args:
        dry_run: If True, only show what would be deleted without making changes
        level_number: Optional - filter by specific level (e.g., 6 for Year 6)
        topic_name: Optional - filter by specific topic (e.g., "Measurements")
    """
    
    print("[INFO] Finding questions with 0 or 1 answer...\n")
    
    # Build query
    questions_query = Question.objects.annotate(
        answer_count=Count('answers')
    ).filter(
        answer_count__lte=1  # 0 or 1 answer
    )
    
    if level_number:
        questions_query = questions_query.filter(level__level_number=level_number)
        print(f"[INFO] Filtering by Level: Year {level_number}")
    
    if topic_name:
        questions_query = questions_query.filter(topic__name=topic_name)
        print(f"[INFO] Filtering by Topic: {topic_name}")
    
    print()
    
    # Get questions with 0 or 1 answer
    questions_to_remove = questions_query.select_related('level', 'topic').order_by('id')
    
    if not questions_to_remove.exists():
        print("[OK] No questions found with 0 or 1 answer!")
        return
    
    # Separate by answer count
    questions_with_no_answers = []
    questions_with_one_answer = []
    
    for question in questions_to_remove:
        answer_count = question.answers.count()
        if answer_count == 0:
            questions_with_no_answers.append(question)
        else:
            questions_with_one_answer.append(question)
    
    print("=" * 80)
    print("QUESTIONS TO BE REMOVED")
    print("=" * 80)
    print(f"  Questions with NO answers: {len(questions_with_no_answers)}")
    print(f"  Questions with ONE answer: {len(questions_with_one_answer)}")
    print(f"  Total questions to remove: {len(questions_to_remove)}")
    print()
    
    # Show questions with no answers
    if questions_with_no_answers:
        print("=" * 80)
        print(f"QUESTIONS WITH NO ANSWERS ({len(questions_with_no_answers)}):")
        print("=" * 80)
        for q in questions_with_no_answers:
            safe_text = q.question_text[:80].encode('ascii', 'ignore').decode('ascii')
            image_info = q.image.name if q.image else "(no image)"
            topic_info = q.topic.name if q.topic else "None"
            print(f"  ID {q.id}: [{q.question_type}] {safe_text}... | Level: {q.level} | Topic: {topic_info} | Image: {image_info}")
        print()
    
    # Show questions with one answer
    if questions_with_one_answer:
        print("=" * 80)
        print(f"QUESTIONS WITH ONE ANSWER ({len(questions_with_one_answer)}):")
        print("=" * 80)
        for q in questions_with_one_answer:
            answer = q.answers.first()
            safe_text = q.question_text[:80].encode('ascii', 'ignore').decode('ascii')
            safe_answer = answer.answer_text.encode('ascii', 'ignore').decode('ascii') if answer else "N/A"
            image_info = q.image.name if q.image else "(no image)"
            topic_info = q.topic.name if q.topic else "None"
            correct_marker = "[CORRECT]" if answer and answer.is_correct else "[WRONG]"
            print(f"  ID {q.id}: [{q.question_type}] {safe_text}... | Level: {q.level} | Topic: {topic_info}")
            print(f"    Answer: '{safe_answer}' {correct_marker} | Image: {image_info}")
        print()
    
    if dry_run:
        print("=" * 80)
        print("[DRY RUN] This was a dry run. No questions were deleted.")
        print("         Run with --execute to actually delete these questions.")
        print("=" * 80)
        return
    
    # Actually delete the questions
    print("[INFO] Starting deletion...\n")
    
    deleted_count = 0
    deleted_with_one_answer = 0
    deleted_with_no_answers = 0
    
    for question in questions_to_remove:
        question_id = question.id
        answer_count = question.answers.count()
        has_student_answers = StudentAnswer.objects.filter(question=question).exists()
        
        # Check if question has student answers (attempts)
        if has_student_answers:
            student_answer_count = StudentAnswer.objects.filter(question=question).count()
            print(f"[WARNING] Question ID {question_id} has {student_answer_count} student answer(s). Deleting anyway...")
        
        # Delete the question (answers will be cascade deleted)
        question.delete()
        deleted_count += 1
        
        if answer_count == 0:
            deleted_with_no_answers += 1
        else:
            deleted_with_one_answer += 1
        
        if deleted_count % 10 == 0:
            print(f"  [PROGRESS] Deleted {deleted_count} questions...")
    
    print("\n" + "=" * 80)
    print("DELETION SUMMARY")
    print("=" * 80)
    print(f"  Total questions deleted: {deleted_count}")
    print(f"  - With no answers: {deleted_with_no_answers}")
    print(f"  - With one answer: {deleted_with_one_answer}")
    print("\n[OK] Deletion complete!")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remove questions with 0 or 1 answer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be deleted)
  python remove_single_or_no_answer_questions.py
  
  # Dry run for Year 6 Measurements only
  python remove_single_or_no_answer_questions.py --level 6 --topic Measurements
  
  # Actually delete questions
  python remove_single_or_no_answer_questions.py --execute
  
  # Delete only Year 6 Measurements questions
  python remove_single_or_no_answer_questions.py --execute --level 6 --topic Measurements
        """
    )
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the questions (default is dry run)')
    parser.add_argument('--level', type=int, 
                       help='Filter by level number (e.g., 6 for Year 6)')
    parser.add_argument('--topic', type=str, 
                       help='Filter by topic name (e.g., "Measurements")')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("=" * 80)
        print("DRY RUN MODE - No questions will be deleted")
        print("=" * 80)
        print()
    else:
        print("=" * 80)
        print("EXECUTION MODE - Questions WILL BE DELETED")
        print("=" * 80)
        print()
        response = input("Are you sure you want to delete these questions? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
        print()
    
    remove_single_or_no_answer_questions(
        dry_run=dry_run,
        level_number=args.level,
        topic_name=args.topic
    )

