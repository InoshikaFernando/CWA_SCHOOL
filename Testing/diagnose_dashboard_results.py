"""
Diagnostic script to check why dashboard results aren't showing.
Compares StudentAnswer records with StudentFinalAnswer records.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, StudentFinalAnswer, Topic, Level, Question, CustomUser
from django.db.models import Q, Count, Sum, Max
import argparse

def diagnose_dashboard_results(username=None):
    """
    Diagnose why dashboard results aren't showing.
    Compares StudentAnswer vs StudentFinalAnswer records.
    """
    print("=" * 100)
    print("DASHBOARD RESULTS DIAGNOSTIC")
    print("=" * 100)
    
    # Get all students or specific student
    if username:
        students = CustomUser.objects.filter(username=username, is_teacher=False)
    else:
        students = CustomUser.objects.filter(is_teacher=False)
    
    if not students.exists():
        print(f"\n[ERROR] No students found" + (f" with username '{username}'" if username else ""))
        return
    
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    
    for student in students:
        print(f"\n{'=' * 100}")
        print(f"STUDENT: {student.username}")
        print(f"{'=' * 100}")
        
        # Get StudentFinalAnswer records
        final_answers = StudentFinalAnswer.objects.filter(student=student).order_by('level__level_number', 'topic__name', 'attempt_number')
        
        print(f"\n[StudentFinalAnswer] Records: {final_answers.count()}")
        if final_answers.exists():
            print("\nStudentFinalAnswer Records:")
            print(f"{'Level':<10} {'Topic':<20} {'Attempt':<10} {'Points':<10} {'Session ID':<40}")
            print("-" * 100)
            for fa in final_answers:
                level_name = f"Year {fa.level.level_number}" if fa.level.level_number < 100 else f"Level {fa.level.level_number}"
                print(f"{level_name:<10} {fa.topic.name:<20} {fa.attempt_number:<10} {fa.points_earned:<10} {fa.session_id:<40}")
        
        # Get StudentAnswer records grouped by session
        student_answers = StudentAnswer.objects.filter(
            student=student
        ).select_related('question', 'question__level', 'question__topic').exclude(session_id='')
        
        print(f"\n[StudentAnswer] Total records: {student_answers.count()}")
        
        # Group by level, topic, session
        unique_sessions = student_answers.values(
            'question__level__level_number',
            'question__topic__name',
            'session_id'
        ).distinct()
        
        print(f"[StudentAnswer] Unique sessions: {unique_sessions.count()}")
        
        # Group by level and topic
        level_topic_data = {}
        for item in unique_sessions:
            level_num = item['question__level__level_number']
            topic_name = item['question__topic__name']
            session_id = item['session_id']
            
            if not session_id or not topic_name:
                continue
            
            key = (level_num, topic_name)
            if key not in level_topic_data:
                level_topic_data[key] = []
            level_topic_data[key].append(session_id)
        
        print(f"\n[StudentAnswer] Level-Topic combinations: {len(level_topic_data)}")
        
        # Check each level-topic combination
        for (level_num, topic_name), session_ids in level_topic_data.items():
            print(f"\n{'-' * 100}")
            level_name = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
            print(f"Level: {level_name}, Topic: {topic_name}")
            print(f"Sessions: {len(session_ids)}")
            
            # Get level and topic objects
            try:
                level_obj = Level.objects.get(level_number=level_num)
                topic_obj = Topic.objects.filter(name=topic_name).first()
            except Level.DoesNotExist:
                print(f"  [WARNING] Level {level_num} not found")
                continue
            
            if not topic_obj:
                print(f"  [WARNING] Topic '{topic_name}' not found")
                continue
            
            # Check available questions
            available_questions = Question.objects.filter(
                level=level_obj,
                topic=topic_obj
            ).count()
            
            standard_limit = YEAR_QUESTION_COUNTS.get(level_num, 10)
            question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
            partial_threshold = int(question_limit * 0.9)
            
            print(f"  Available questions: {available_questions}")
            print(f"  Standard limit: {standard_limit}")
            print(f"  Question limit: {question_limit}")
            print(f"  Partial threshold (90%): {partial_threshold}")
            
            # Check each session
            completed_sessions = []
            for session_id in session_ids:
                session_answers = student_answers.filter(
                    session_id=session_id,
                    question__level__level_number=level_num,
                    question__topic__name=topic_name
                )
                
                answer_count = session_answers.count()
                first_answer = session_answers.first()
                has_time = first_answer and first_answer.time_taken_seconds > 0
                time_value = first_answer.time_taken_seconds if first_answer else 0
                
                meets_threshold = answer_count >= partial_threshold
                
                print(f"\n  Session: {session_id[:36]}...")
                print(f"    Answer count: {answer_count}")
                print(f"    Meets threshold: {meets_threshold} ({answer_count} >= {partial_threshold})")
                print(f"    Has time: {has_time} ({time_value}s)")
                
                if meets_threshold:
                    completed_sessions.append(session_id)
                    
                    # Calculate points
                    if has_time:
                        total_correct = sum(1 for a in session_answers if a.is_correct)
                        percentage = (total_correct / answer_count) if answer_count else 0
                        final_points = (percentage * 100 * 60) / time_value if time_value else 0
                        print(f"    Points: {round(final_points, 2)} ({total_correct}/{answer_count} correct)")
                    else:
                        total_points = sum(a.points_earned for a in session_answers)
                        print(f"    Points: {total_points} (no time data)")
            
            print(f"\n  Completed sessions (meet threshold): {len(completed_sessions)}")
            
            # Check if there's a matching StudentFinalAnswer record
            matching_final = final_answers.filter(
                level=level_obj,
                topic=topic_obj
            )
            
            print(f"  StudentFinalAnswer records: {matching_final.count()}")
            if matching_final.exists():
                best_final = matching_final.order_by('-points_earned').first()
                print(f"    Best points: {best_final.points_earned} (Attempt {best_final.attempt_number})")
            
            # Summary
            if len(completed_sessions) > 0:
                print(f"  [OK] Should appear on dashboard")
            else:
                print(f"  [ISSUE] Won't appear on dashboard - no sessions meet threshold")
                if len(session_ids) > 0:
                    print(f"    Reason: Sessions exist but don't meet {partial_threshold} answer threshold")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diagnose dashboard results')
    parser.add_argument('--username', type=str, help='Specific username to check (optional)')
    args = parser.parse_args()
    
    diagnose_dashboard_results(username=args.username)

