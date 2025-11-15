#!/usr/bin/env python
"""
Fix incomplete sessions for Year 6 Measurements (and other topics).
Options:
1. Merge incomplete sessions that are likely from the same attempt
2. Delete incomplete sessions
3. Show statistics about incomplete sessions
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, Level, Topic, CustomUser
from django.db.models import Count, Q, Min
from collections import defaultdict

def fix_incomplete_sessions(level_number=6, topic_name="Measurements", merge_sessions=True, dry_run=True, keep_partial=True, partial_threshold=0.9, delete_incomplete=False):
    """
    Fix incomplete sessions by merging them or cleaning them up.
    
    Args:
        level_number: Level to process (default: 6 for Year 6)
        topic_name: Topic name (default: "Measurements")
        merge_sessions: If True, merge incomplete sessions from same student within time window
        dry_run: If True, only show what would be done without making changes
        keep_partial: If True, keep sessions that are close to the limit (default: True)
        partial_threshold: Minimum ratio of answers to keep (default: 0.9 = 90% of required)
        delete_incomplete: If True, delete incomplete sessions that can't be merged (default: False - keep them)
    """
    
    print("=" * 100)
    print(f"FIXING INCOMPLETE SESSIONS - Year {level_number} {topic_name}")
    print("=" * 100)
    print()
    
    if dry_run:
        print("[DRY RUN MODE] - No changes will be made")
        print()
    
    # Get level and topic
    level = Level.objects.filter(level_number=level_number).first()
    if not level:
        print(f"[ERROR] Year {level_number} level not found!")
        return
    
    topic = Topic.objects.filter(name=topic_name).first()
    if not topic:
        print(f"[ERROR] {topic_name} topic not found!")
        return
    
    # Question limit for this level
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level_number, 20)
    
    print(f"[INFO] Level: {level}")
    print(f"[INFO] Topic: {topic}")
    print(f"[INFO] Question limit: {question_limit}")
    print()
    
    # Get all student answers for this level/topic
    all_answers = StudentAnswer.objects.filter(
        question__level=level,
        question__topic=topic
    ).exclude(session_id='').select_related('student', 'question')
    
    # Group by student and session
    student_sessions = defaultdict(list)
    for answer in all_answers:
        key = (answer.student.id, answer.session_id)
        student_sessions[key].append(answer)
    
    print(f"[INFO] Total unique (student, session) combinations: {len(student_sessions)}")
    print()
    
    # Find incomplete sessions
    incomplete_sessions = []
    complete_sessions = []
    
    for (student_id, session_id), answers in student_sessions.items():
        answer_count = len(answers)
        if answer_count < question_limit:
            incomplete_sessions.append((student_id, session_id, answers))
        else:
            complete_sessions.append((student_id, session_id, answers))
    
    print(f"[INFO] Complete sessions (>= {question_limit} answers): {len(complete_sessions)}")
    print(f"[INFO] Incomplete sessions (< {question_limit} answers): {len(incomplete_sessions)}")
    print()
    
    if len(incomplete_sessions) == 0:
        print("[OK] No incomplete sessions found!")
        return
    
    # Group incomplete sessions by student
    incomplete_by_student = defaultdict(list)
    for student_id, session_id, answers in incomplete_sessions:
        incomplete_by_student[student_id].append((session_id, answers))
    
    print(f"[INFO] Students with incomplete sessions: {len(incomplete_by_student)}")
    print()
    
    merged_count = 0
    deleted_count = 0
    kept_count = 0
    
    # Process each student's incomplete sessions
    for student_id, sessions in incomplete_by_student.items():
        student = CustomUser.objects.get(id=student_id)
        print(f"\n{'='*100}")
        print(f"STUDENT: {student.username} (ID: {student_id})")
        print(f"{'='*100}")
        print(f"Incomplete sessions: {len(sessions)}")
        
        if not merge_sessions:
            # Don't merge, just process each session individually
            if delete_incomplete:
                # Delete incomplete sessions
                for session_id, answers in sessions:
                    answer_count = len(answers)
                    if answer_count < question_limit:
                        print(f"  [DELETE] Session {session_id[:8]}...: {answer_count} answers")
                        if not dry_run:
                            StudentAnswer.objects.filter(
                                student=student,
                                question__level=level,
                                question__topic=topic,
                                session_id=session_id
                            ).delete()
                            deleted_count += 1
                    else:
                        print(f"  [KEEP] Session {session_id[:8]}...: {answer_count} answers (complete)")
                        kept_count += 1
            else:
                # Keep all sessions
                for session_id, answers in sessions:
                    answer_count = len(answers)
                    if answer_count >= question_limit:
                        print(f"  [KEEP] Session {session_id[:8]}...: {answer_count} answers (complete)")
                    else:
                        print(f"  [KEEP] Session {session_id[:8]}...: {answer_count} answers (incomplete, keeping)")
                    kept_count += 1
            continue
        
        # Try to merge sessions
        # Sort by earliest answer time
        sessions_with_time = []
        for session_id, answers in sessions:
            earliest_time = min(a.answered_at for a in answers)
            latest_time = max(a.answered_at for a in answers)
            sessions_with_time.append((session_id, answers, earliest_time, latest_time))
        
        sessions_with_time.sort(key=lambda x: x[2])  # Sort by earliest time
        
        # Group sessions that are close in time (within 2 hours) and have non-overlapping questions
        # This handles cases where a student started a quiz, left, and came back
        merged_groups = []
        used_sessions = set()
        
        for i, (session_id, answers, earliest_time, latest_time) in enumerate(sessions_with_time):
            if session_id in used_sessions:
                continue
            
            # Find other sessions within 2 hours that can be merged
            group = [(session_id, answers, earliest_time, latest_time)]
            used_sessions.add(session_id)
            
            answered_question_ids = {a.question.id for a in answers}
            total_answers = len(answers)
            group_earliest = earliest_time
            group_latest = latest_time
            
            # Look for sessions to merge
            for j, (other_session_id, other_answers, other_earliest, other_latest) in enumerate(sessions_with_time[i+1:], i+1):
                if other_session_id in used_sessions:
                    continue
                
                # Check if sessions are close in time (within 2 hours of group's time range)
                time_diff_earliest = abs((other_earliest - group_earliest).total_seconds())
                time_diff_latest = abs((other_latest - group_latest).total_seconds())
                
                # Allow merge if within 2 hours of the group's time range
                if time_diff_earliest > 7200 and time_diff_latest > 7200:  # More than 2 hours apart
                    continue
                
                # Check if questions don't overlap (or minimal overlap)
                other_question_ids = {a.question.id for a in other_answers}
                overlap = answered_question_ids & other_question_ids
                
                # Allow merge if questions don't overlap much (less than 50% overlap)
                # This allows merging even if there's some overlap (student might have re-answered)
                max_questions = max(len(answered_question_ids), len(other_question_ids))
                if max_questions == 0 or len(overlap) / max_questions < 0.5:
                    group.append((other_session_id, other_answers, other_earliest, other_latest))
                    used_sessions.add(other_session_id)
                    answered_question_ids.update(other_question_ids)
                    total_answers += len(other_answers)
                    # Update group time range
                    group_earliest = min(group_earliest, other_earliest)
                    group_latest = max(group_latest, other_latest)
            
            merged_groups.append(group)
        
        # Process each group
        for group in merged_groups:
            if len(group) == 1:
                # Single session - can't merge
                session_id, answers, earliest_time, latest_time = group[0]
                answer_count = len(answers)
                if answer_count >= question_limit:
                    print(f"  [KEEP] Session {session_id[:8]}...: {answer_count} answers (complete)")
                    kept_count += 1
                elif keep_partial and answer_count >= (question_limit * partial_threshold):
                    # Keep partial sessions that are close to the limit
                    print(f"  [KEEP PARTIAL] Session {session_id[:8]}...: {answer_count} answers (close to {question_limit}, keeping)")
                    kept_count += 1
                else:
                    # Session is incomplete and can't be merged
                    if delete_incomplete:
                        print(f"  [DELETE] Session {session_id[:8]}...: {answer_count} answers (cannot merge, too few)")
                        if not dry_run:
                            StudentAnswer.objects.filter(
                                student=student,
                                question__level=level,
                                question__topic=topic,
                                session_id=session_id
                            ).delete()
                            deleted_count += 1
                    else:
                        print(f"  [KEEP] Session {session_id[:8]}...: {answer_count} answers (incomplete, keeping as-is)")
                        kept_count += 1
            else:
                # Multiple sessions - merge them
                total_answers = sum(len(answers) for _, answers, _, _ in group)
                session_ids = [sid for sid, _, _, _ in group]
                unique_question_ids = set()
                for _, answers, _, _ in group:
                    unique_question_ids.update(a.question.id for a in answers)
                unique_answer_count = len(unique_question_ids)
                
                if unique_answer_count >= question_limit:
                    # Merge into first session
                    primary_session_id = group[0][0]
                    print(f"  [MERGE] {len(group)} sessions -> {primary_session_id[:8]}...: {total_answers} total answers, {unique_answer_count} unique questions")
                    
                    if not dry_run:
                        # Calculate total time span for merged session
                        all_earliest = min(earliest for _, _, earliest, _ in group)
                        all_latest = max(latest for _, _, _, latest in group)
                        total_time_span = int((all_latest - all_earliest).total_seconds())
                        
                        # Update all answers to use primary session_id
                        for session_id, _, _, _ in group[1:]:
                            StudentAnswer.objects.filter(
                                student=student,
                                question__level=level,
                                question__topic=topic,
                                session_id=session_id
                            ).update(session_id=primary_session_id)
                        
                        # Update time_taken_seconds to be the total time span
                        primary_answers = StudentAnswer.objects.filter(
                            student=student,
                            question__level=level,
                            question__topic=topic,
                            session_id=primary_session_id
                        )
                        primary_answers.update(time_taken_seconds=total_time_span)
                        
                        merged_count += len(group) - 1
                elif keep_partial and unique_answer_count >= (question_limit * partial_threshold):
                    # Merge but keep as partial (close to limit)
                    primary_session_id = group[0][0]
                    print(f"  [MERGE PARTIAL] {len(group)} sessions -> {primary_session_id[:8]}...: {total_answers} total answers, {unique_answer_count} unique questions (close to {question_limit}, keeping)")
                    
                    if not dry_run:
                        # Calculate total time span for merged session
                        all_earliest = min(earliest for _, _, earliest, _ in group)
                        all_latest = max(latest for _, _, _, latest in group)
                        total_time_span = int((all_latest - all_earliest).total_seconds())
                        
                        # Update all answers to use primary session_id
                        for session_id, _, _, _ in group[1:]:
                            StudentAnswer.objects.filter(
                                student=student,
                                question__level=level,
                                question__topic=topic,
                                session_id=session_id
                            ).update(session_id=primary_session_id)
                        
                        # Update time_taken_seconds to be the total time span
                        primary_answers = StudentAnswer.objects.filter(
                            student=student,
                            question__level=level,
                            question__topic=topic,
                            session_id=primary_session_id
                        )
                        primary_answers.update(time_taken_seconds=total_time_span)
                        
                        merged_count += len(group) - 1
                else:
                    # Still not enough even after merge
                    if delete_incomplete:
                        print(f"  [DELETE] {len(group)} sessions (merged: {total_answers} answers, {unique_answer_count} unique questions, need {question_limit})")
                        if not dry_run:
                            for session_id, _, _, _ in group:
                                StudentAnswer.objects.filter(
                                    student=student,
                                    question__level=level,
                                    question__topic=topic,
                                    session_id=session_id
                                ).delete()
                            deleted_count += len(group)
                    else:
                        print(f"  [KEEP] {len(group)} sessions (merged: {total_answers} answers, {unique_answer_count} unique questions, incomplete but keeping)")
                        # Still merge them into one session for better organization
                        primary_session_id = group[0][0]
                        if not dry_run and len(group) > 1:
                            # Calculate total time span for merged session
                            all_earliest = min(earliest for _, _, earliest, _ in group)
                            all_latest = max(latest for _, _, _, latest in group)
                            total_time_span = int((all_latest - all_earliest).total_seconds())
                            
                            # Update all answers to use primary session_id
                            for session_id, _, _, _ in group[1:]:
                                StudentAnswer.objects.filter(
                                    student=student,
                                    question__level=level,
                                    question__topic=topic,
                                    session_id=session_id
                                ).update(session_id=primary_session_id)
                            
                            # Update time_taken_seconds to be the total time span
                            primary_answers = StudentAnswer.objects.filter(
                                student=student,
                                question__level=level,
                                question__topic=topic,
                                session_id=primary_session_id
                            )
                            primary_answers.update(time_taken_seconds=total_time_span)
                            
                            merged_count += len(group) - 1
                        kept_count += len(group)
    
    print(f"\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}")
    if dry_run:
        print("[DRY RUN] - No changes were made")
        print()
        print("To apply changes, run with --execute flag:")
        print(f"  python Testing/fix_incomplete_sessions.py --level {level_number} --topic '{topic_name}' --execute")
    else:
        print(f"Merged sessions: {merged_count}")
        print(f"Deleted sessions: {deleted_count}")
        print(f"Kept sessions: {kept_count}")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix incomplete sessions by merging or deleting them',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be done)
  python Testing/fix_incomplete_sessions.py
  
  # Fix Year 6 Measurements (dry run)
  python Testing/fix_incomplete_sessions.py --level 6 --topic "Measurements"
  
  # Actually fix Year 6 Measurements
  python Testing/fix_incomplete_sessions.py --level 6 --topic "Measurements" --execute
  
  # Fix all topics for Year 6
  python Testing/fix_incomplete_sessions.py --level 6 --topic "BODMAS/PEMDAS" --execute
        """
    )
    parser.add_argument('--level', type=int, default=6,
                       help='Level number (default: 6)')
    parser.add_argument('--topic', type=str, default='Measurements',
                       help='Topic name (default: Measurements)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually make changes (default: dry run)')
    parser.add_argument('--no-merge', action='store_true',
                       help='Delete incomplete sessions instead of merging')
    parser.add_argument('--no-keep-partial', action='store_true',
                       help='Delete partial sessions even if close to limit (default: keep 90%+)')
    parser.add_argument('--partial-threshold', type=float, default=0.9,
                       help='Minimum ratio to keep partial sessions (default: 0.9 = 90%%)')
    parser.add_argument('--delete-incomplete', action='store_true',
                       help='Delete incomplete sessions that cannot be merged (default: keep all sessions)')
    
    args = parser.parse_args()
    
    fix_incomplete_sessions(
        level_number=args.level,
        topic_name=args.topic,
        merge_sessions=not args.no_merge,
        dry_run=not args.execute,
        keep_partial=not args.no_keep_partial,
        partial_threshold=args.partial_threshold,
        delete_incomplete=args.delete_incomplete
    )

