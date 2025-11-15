#!/usr/bin/env python
"""
Check avisha.munasinghe's results for Measurements and BODMAS
"""
import os
import sys
import django

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, Level, Topic, CustomUser
from django.db.models import Count

def check_avisha_results():
    """Check avisha.munasinghe's results"""
    
    print("=" * 100)
    print("CHECKING AVISHA.MUNASINGHE'S RESULTS")
    print("=" * 100)
    print()
    
    # Get student
    student = CustomUser.objects.filter(username="avisha.munasinghe").first()
    if not student:
        print("[ERROR] Student avisha.munasinghe not found!")
        return
    
    print(f"[INFO] Student: {student.username} (ID: {student.id})")
    print()
    
    # Get all student answers
    student_answers = StudentAnswer.objects.filter(
        student=student
    ).select_related('question', 'question__level', 'question__topic')
    
    print(f"[INFO] Total answers: {student_answers.count()}")
    print()
    
    # Check Year 6 Measurements
    level_6 = Level.objects.filter(level_number=6).first()
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    bodmas_topic = Topic.objects.filter(name="BODMAS/PEMDAS").first()
    
    if level_6:
        print(f"[INFO] Year 6 Level: {level_6}")
        
        # Check Measurements
        if measurements_topic:
            measurements_answers = student_answers.filter(
                question__level=level_6,
                question__topic=measurements_topic
            ).exclude(session_id='')
            
            print(f"\n[INFO] Year 6 Measurements answers: {measurements_answers.count()}")
            
            if measurements_answers.exists():
                # Get unique sessions
                unique_sessions = measurements_answers.values('session_id').distinct()
                print(f"  Unique sessions: {unique_sessions.count()}")
                
                YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
                question_limit = YEAR_QUESTION_COUNTS.get(6, 20)
                
                available_questions = Question.objects.filter(
                    level=level_6,
                    topic=measurements_topic
                ).count()
                question_limit = min(available_questions, question_limit) if available_questions > 0 else question_limit
                
                print(f"  Question limit: {question_limit} (available: {available_questions})")
                print()
                
                for session_data in unique_sessions:
                    session_id = session_data['session_id']
                    session_answers = measurements_answers.filter(session_id=session_id)
                    answer_count = session_answers.count()
                    
                    print(f"  Session {session_id[:8]}...: {answer_count} answers")
                    if answer_count >= question_limit:
                        first_answer = session_answers.first()
                        print(f"    - [COMPLETE] Will appear on dashboard")
                        print(f"    - Time: {first_answer.time_taken_seconds if first_answer else 0}s")
                        print(f"    - Date: {first_answer.answered_at if first_answer else 'N/A'}")
                    else:
                        print(f"    - [INCOMPLETE] Needs {question_limit} answers (has {answer_count})")
                    print()
            else:
                print("  [WARNING] No Measurements answers found!")
        
        # Check BODMAS
        if bodmas_topic:
            bodmas_answers = student_answers.filter(
                question__level=level_6,
                question__topic=bodmas_topic
            ).exclude(session_id='')
            
            print(f"\n[INFO] Year 6 BODMAS answers: {bodmas_answers.count()}")
            
            if bodmas_answers.exists():
                # Get unique sessions
                unique_sessions = bodmas_answers.values('session_id').distinct()
                print(f"  Unique sessions: {unique_sessions.count()}")
                
                YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
                question_limit = YEAR_QUESTION_COUNTS.get(6, 20)
                
                available_questions = Question.objects.filter(
                    level=level_6,
                    topic=bodmas_topic
                ).count()
                question_limit = min(available_questions, question_limit) if available_questions > 0 else question_limit
                
                print(f"  Question limit: {question_limit} (available: {available_questions})")
                print()
                
                for session_data in unique_sessions:
                    session_id = session_data['session_id']
                    session_answers = bodmas_answers.filter(session_id=session_id)
                    answer_count = session_answers.count()
                    
                    print(f"  Session {session_id[:8]}...: {answer_count} answers")
                    if answer_count >= question_limit:
                        first_answer = session_answers.first()
                        print(f"    - [COMPLETE] Will appear on dashboard")
                        print(f"    - Time: {first_answer.time_taken_seconds if first_answer else 0}s")
                        print(f"    - Date: {first_answer.answered_at if first_answer else 'N/A'}")
                    else:
                        print(f"    - [INCOMPLETE] Needs {question_limit} answers (has {answer_count})")
                    print()
            else:
                print("  [WARNING] No BODMAS answers found!")
    
    # Check all answers grouped by level and topic
    print("\n" + "=" * 100)
    print("ALL ANSWERS BY LEVEL AND TOPIC")
    print("=" * 100)
    print()
    
    answers_by_level_topic = student_answers.values(
        'question__level__level_number',
        'question__topic__name'
    ).annotate(
        count=Count('id'),
        sessions=Count('session_id', distinct=True)
    ).order_by('question__level__level_number', 'question__topic__name')
    
    for item in answers_by_level_topic:
        level_num = item['question__level__level_number']
        topic_name = item['question__topic__name'] or "No Topic"
        count = item['count']
        sessions = item['sessions']
        print(f"Year {level_num} - {topic_name}: {count} answers, {sessions} unique sessions")
    
    print()
    print("=" * 100)
    print("RECOMMENDATION")
    print("=" * 100)
    print()
    print("If there are incomplete sessions, you can:")
    print("1. Run the fix script to merge/clean incomplete sessions:")
    print("   python Testing/fix_incomplete_sessions.py --level 6 --topic 'Measurements' --execute")
    print("   python Testing/fix_incomplete_sessions.py --level 6 --topic 'BODMAS/PEMDAS' --execute")
    print("2. Or have the student complete the quizzes again")
    print()

if __name__ == "__main__":
    check_avisha_results()

