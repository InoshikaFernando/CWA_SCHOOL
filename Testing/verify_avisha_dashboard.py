#!/usr/bin/env python
"""
Verify that avisha.munasinghe's merged session will appear on dashboard
"""
import os
import sys
import django

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, Level, Topic, CustomUser

def verify_avisha_dashboard():
    """Verify avisha.munasinghe's results will appear on dashboard"""
    
    print("=" * 100)
    print("VERIFYING AVISHA.MUNASINGHE'S DASHBOARD RESULTS")
    print("=" * 100)
    print()
    
    # Get student
    student = CustomUser.objects.filter(username="avisha.munasinghe").first()
    if not student:
        print("[ERROR] Student not found!")
        return
    
    # Get level and topic
    level_6 = Level.objects.filter(level_number=6).first()
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    
    if not level_6 or not measurements_topic:
        print("[ERROR] Level 6 or Measurements topic not found!")
        return
    
    # Get all student answers (same as dashboard_detail view)
    student_answers = StudentAnswer.objects.filter(
        student=student
    ).select_related('question', 'question__level', 'question__topic')
    
    # Filter for answers with topics
    student_answers_with_topics = student_answers.filter(question__topic__isnull=False)
    
    # Get unique combinations (same as dashboard_detail)
    unique_level_topic_sessions = student_answers_with_topics.values(
        'question__level__level_number', 
        'question__topic__name',
        'session_id'
    ).distinct()
    
    # Group by level and topic
    level_topic_data = {}
    for item in unique_level_topic_sessions:
        level_num = item['question__level__level_number']
        topic_name = item['question__topic__name']
        session_id = item['session_id']
        
        if not session_id or not topic_name:
            continue
        
        key = (level_num, topic_name)
        if key not in level_topic_data:
            level_topic_data[key] = set()
        level_topic_data[key].add(session_id)
    
    # Check Year 6 Measurements
    year6_measurements_key = (6, "Measurements")
    if year6_measurements_key in level_topic_data:
        session_ids = level_topic_data[year6_measurements_key]
        print(f"[INFO] Year 6 Measurements: {len(session_ids)} unique sessions")
        
        # Get available questions
        available_questions = Question.objects.filter(
            level=level_6,
            topic=measurements_topic
        ).count()
        
        YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
        standard_limit = YEAR_QUESTION_COUNTS.get(6, 20)
        question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
        
        # Dashboard now uses 90% threshold
        partial_threshold = int(question_limit * 0.9)  # 90% of required questions
        
        print(f"  Available questions: {available_questions}")
        print(f"  Question limit: {question_limit}")
        print(f"  Partial threshold (90%): {partial_threshold}")
        print()
        
        completed_sessions = []
        for session_id in session_ids:
            session_answers = student_answers_with_topics.filter(
                session_id=session_id,
                question__level__level_number=6,
                question__topic__name="Measurements"
            )
            answer_count = session_answers.count()
            
            print(f"  Session {session_id[:8]}...: {answer_count} answers")
            
            if answer_count >= partial_threshold:
                completed_sessions.append(session_id)
                first_answer = session_answers.first()
                if first_answer:
                    has_time = first_answer.time_taken_seconds > 0
                    print(f"    - [WILL APPEAR] Meets threshold ({answer_count} >= {partial_threshold})")
                    print(f"    - Has time_taken_seconds: {has_time} ({first_answer.time_taken_seconds if first_answer else 0}s)")
                    if has_time:
                        total_correct = sum(1 for a in session_answers if a.is_correct)
                        percentage = (total_correct / answer_count) if answer_count else 0
                        final_points = (percentage * 100 * 60) / first_answer.time_taken_seconds if first_answer.time_taken_seconds else 0
                        print(f"    - Points: {round(final_points, 2)} ({total_correct}/{answer_count} correct)")
                else:
                    print(f"    - [WILL APPEAR] Meets threshold but no time data")
            else:
                print(f"    - [WON'T APPEAR] Below threshold ({answer_count} < {partial_threshold})")
            print()
        
        print(f"[RESULT] Year 6 Measurements will show {len(completed_sessions)} session(s) on dashboard")
    else:
        print("[WARNING] Year 6 Measurements not found!")

if __name__ == "__main__":
    verify_avisha_dashboard()

