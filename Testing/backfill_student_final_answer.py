"""
Script to backfill StudentFinalAnswer table from existing StudentAnswer records.
This creates aggregated records for each completed quiz attempt.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, StudentFinalAnswer, Topic, Level, Question
from django.db.models import Q, Count, Sum, Max
from collections import defaultdict
import argparse

def backfill_student_final_answer(dry_run=True):
    """
    Backfill StudentFinalAnswer table from StudentAnswer records.
    
    For each unique (student, session_id, topic, level) combination:
    1. Calculate total points earned
    2. Get attempt_number (increment from previous attempts)
    3. Create StudentFinalAnswer record
    """
    print("=" * 80)
    print("Backfilling StudentFinalAnswer table from StudentAnswer records")
    print("=" * 80)
    
    if dry_run:
        print("\n[DRY RUN MODE] - No changes will be made to the database")
    else:
        print("\n[EXECUTE MODE] - Changes will be saved to the database")
    
    # Get all unique sessions with answers
    sessions = StudentAnswer.objects.exclude(
        session_id=''
    ).values(
        'student', 'session_id', 'question__level', 'question__topic'
    ).annotate(
        answer_count=Count('id'),
        total_points=Sum('points_earned'),
        time_taken=Max('time_taken_seconds')
    ).order_by('student', 'question__level', 'question__topic', 'session_id')
    
    print(f"\nFound {sessions.count()} unique sessions to process")
    
    # Group by student-topic-level to track attempt numbers
    attempt_tracker = defaultdict(int)  # (student_id, topic_id, level_id) -> next_attempt_number
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for session in sessions:
        try:
            student_id = session['student']
            session_id = session['session_id']
            level_id = session['question__level']
            topic_id = session['question__topic']
            
            # Skip if topic or level is None
            if not topic_id or not level_id:
                skipped_count += 1
                continue
            
            # Get the actual objects
            from maths.models import CustomUser
            student = CustomUser.objects.get(id=student_id)
            level = Level.objects.get(id=level_id)
            topic = Topic.objects.get(id=topic_id)
            
            # Check if record already exists
            existing = StudentFinalAnswer.objects.filter(
                student=student,
                session_id=session_id
            ).first()
            
            if existing:
                if not dry_run:
                    # Update existing record
                    existing.topic = topic
                    existing.level = level
                    existing.points_earned = session['total_points'] or 0
                    existing.save()
                    updated_count += 1
                else:
                    updated_count += 1
                continue
            
            # Get next attempt number for this student-topic-level combination
            key = (student_id, topic_id, level_id)
            if key not in attempt_tracker:
                # Find the max attempt number for this combination
                last_attempt = StudentFinalAnswer.objects.filter(
                    student=student,
                    topic=topic,
                    level=level
                ).order_by('-attempt_number').first()
                
                if last_attempt:
                    attempt_tracker[key] = last_attempt.attempt_number + 1
                else:
                    attempt_tracker[key] = 1
            
            attempt_number = attempt_tracker[key]
            attempt_tracker[key] += 1
            
            # Calculate final points using the same formula as views
            # Formula: (percentage * 100 * 60) / time_seconds
            time_seconds = session['time_taken'] or 0
            total_points_earned = session['total_points'] or 0
            answer_count = session['answer_count'] or 0
            
            if time_seconds > 0 and answer_count > 0:
                # Calculate percentage (assuming each question is worth 1 point for percentage)
                # We need to get the actual question points
                session_answers = StudentAnswer.objects.filter(
                    student=student,
                    session_id=session_id,
                    question__level=level,
                    question__topic=topic
                )
                
                # Calculate total possible points from questions
                question_ids = session_answers.values_list('question_id', flat=True).distinct()
                questions = Question.objects.filter(id__in=question_ids)
                total_possible_points = sum(q.points for q in questions)
                
                if total_possible_points > 0:
                    percentage = total_points_earned / total_possible_points
                    final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
                else:
                    final_points = total_points_earned
            else:
                final_points = total_points_earned
            
            final_points = round(final_points, 2)
            
            if not dry_run:
                StudentFinalAnswer.objects.create(
                    student=student,
                    session_id=session_id,
                    topic=topic,
                    level=level,
                    attempt_number=attempt_number,
                    points_earned=final_points
                )
                created_count += 1
            else:
                created_count += 1
                
        except Exception as e:
            error_count += 1
            print(f"[ERROR] Failed to process session {session.get('session_id', 'unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Backfill Summary:")
    print("=" * 80)
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count} (missing topic/level)")
    print(f"Errors: {error_count}")
    print("=" * 80)
    
    if dry_run:
        print("\n[DRY RUN] Run with --execute to apply changes")
    else:
        print("\n[SUCCESS] Backfill completed!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backfill StudentFinalAnswer table from StudentAnswer records')
    parser.add_argument('--execute', action='store_true', help='Execute the backfill (default is dry-run)')
    args = parser.parse_args()
    
    backfill_student_final_answer(dry_run=not args.execute)

