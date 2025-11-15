#!/usr/bin/env python
"""
Diagnose why Year 6 measurements results might be disappearing from dashboard.
Checks:
1. Are results saved to database?
2. Do they have session_id?
3. Do questions have correct topic?
4. Do they meet dashboard requirements?
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, Level, Topic, CustomUser
from django.db.models import Count, Q

def diagnose_year6_measurements_results():
    """Diagnose Year 6 measurements results"""
    
    print("=" * 100)
    print("YEAR 6 MEASUREMENTS RESULTS DIAGNOSIS")
    print("=" * 100)
    print()
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return
    
    # Get Measurements topic
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        print("[ERROR] Measurements topic not found!")
        return
    
    print(f"[INFO] Year 6 Level: {level_6}")
    print(f"[INFO] Measurements Topic: {measurements_topic}")
    print()
    
    # Get all Year 6 measurements questions
    year6_measurements_questions = Question.objects.filter(
        level=level_6,
        topic=measurements_topic
    )
    print(f"[INFO] Total Year 6 Measurements questions: {year6_measurements_questions.count()}")
    print()
    
    # Get all student answers for Year 6 measurements
    all_answers = StudentAnswer.objects.filter(
        question__level=level_6,
        question__topic=measurements_topic
    ).select_related('student', 'question')
    
    print(f"[INFO] Total Year 6 Measurements answers in database: {all_answers.count()}")
    print()
    
    if all_answers.count() == 0:
        print("[WARNING] No answers found in database!")
        print("   This means results are not being saved.")
        return
    
    # Check session_id
    answers_with_session = all_answers.exclude(session_id='').exclude(session_id__isnull=True)
    answers_without_session = all_answers.filter(Q(session_id='') | Q(session_id__isnull=True))
    
    print(f"[INFO] Answers with session_id: {answers_with_session.count()}")
    print(f"[INFO] Answers without session_id: {answers_without_session.count()}")
    print()
    
    if answers_without_session.count() > 0:
        print("[WARNING] Some answers don't have session_id!")
        print("   These will NOT appear on the dashboard (dashboard filters out empty session_ids)")
        print()
    
    # Group by student
    students_with_answers = all_answers.values('student').distinct()
    print(f"[INFO] Students with Year 6 Measurements answers: {students_with_answers.count()}")
    print()
    
    # Check each student
    for student_data in students_with_answers:
        student_id = student_data['student']
        student = CustomUser.objects.get(id=student_id)
        
        print(f"\n{'='*100}")
        print(f"STUDENT: {student.username} (ID: {student.id})")
        print(f"{'='*100}")
        
        student_answers = all_answers.filter(student=student)
        print(f"Total answers: {student_answers.count()}")
        
        # Check session_ids
        session_ids = student_answers.exclude(session_id='').values_list('session_id', flat=True).distinct()
        session_ids_list = [s for s in session_ids if s]
        print(f"Unique session IDs: {len(session_ids_list)}")
        
        if len(session_ids_list) == 0:
            print("[ERROR] No valid session IDs found!")
            print("   This student's results will NOT appear on dashboard.")
            continue
        
        # Check each session
        print(f"\nSession breakdown:")
        for session_id in session_ids_list[:10]:  # Show first 10 sessions
            session_answers = student_answers.filter(session_id=session_id)
            answer_count = session_answers.count()
            
            # Check if questions have correct topic
            questions_with_topic = session_answers.filter(question__topic=measurements_topic).count()
            
            # Check time_taken_seconds
            has_time = session_answers.filter(time_taken_seconds__gt=0).exists()
            time_value = session_answers.first().time_taken_seconds if session_answers.exists() else 0
            
            # Dashboard requirement: need at least question_limit answers
            YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
            question_limit = YEAR_QUESTION_COUNTS.get(6, 20)
            
            meets_requirement = answer_count >= question_limit
            
            status = "[OK]" if meets_requirement else "[INCOMPLETE]"
            print(f"  {status} Session {session_id[:8]}...: {answer_count} answers (need {question_limit})")
            print(f"      - Questions with correct topic: {questions_with_topic}/{answer_count}")
            print(f"      - Has time_taken_seconds: {has_time} ({time_value}s)")
            print(f"      - Will appear on dashboard: {'YES' if meets_requirement else 'NO (not enough answers)'}")
        
        if len(session_ids_list) > 10:
            print(f"  ... and {len(session_ids_list) - 10} more sessions")
    
    print(f"\n{'='*100}")
    print("DASHBOARD REQUIREMENTS CHECK")
    print(f"{'='*100}")
    print()
    print("For results to appear on dashboard, they need:")
    print("  1. Valid session_id (not empty)")
    print("  2. Questions must have correct topic (Measurements)")
    print("  3. At least question_limit answers (Year 6 = 20)")
    print("  4. time_taken_seconds > 0")
    print()
    
    # Check dashboard query
    print("Testing dashboard query:")
    dashboard_answers = StudentAnswer.objects.filter(
        question__level=level_6,
        question__topic=measurements_topic
    ).exclude(session_id='').select_related('question', 'question__level', 'question__topic')
    
    unique_sessions = dashboard_answers.values(
        'question__level__level_number',
        'question__topic__name',
        'session_id'
    ).distinct()
    
    print(f"  Unique (level, topic, session) combinations: {unique_sessions.count()}")
    
    # Filter by student
    for student_data in students_with_answers[:3]:  # Check first 3 students
        student_id = student_data['student']
        student = CustomUser.objects.get(id=student_id)
        
        student_dashboard_answers = dashboard_answers.filter(student=student)
        student_sessions = student_dashboard_answers.values('session_id').distinct()
        valid_sessions = [s['session_id'] for s in student_sessions if s['session_id']]
        
        print(f"\n  Student {student.username}:")
        print(f"    - Valid sessions: {len(valid_sessions)}")
        
        for session_id in valid_sessions[:3]:
            session_answers = student_dashboard_answers.filter(session_id=session_id)
            answer_count = session_answers.count()
            question_limit = 20
            if answer_count >= question_limit:
                print(f"      [OK] Session {session_id[:8]}...: {answer_count} answers - WILL APPEAR")
            else:
                print(f"      [SKIP] Session {session_id[:8]}...: {answer_count} answers - NEEDS {question_limit}")

if __name__ == "__main__":
    diagnose_year6_measurements_results()

