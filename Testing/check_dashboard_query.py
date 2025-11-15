#!/usr/bin/env python
"""
Check what the dashboard query actually returns for Year 6 Measurements
"""
import os
import sys
import django

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Question, Level, Topic, CustomUser
from django.db.models import Count, Q

def check_dashboard_query():
    """Check what the dashboard query returns"""
    
    print("=" * 100)
    print("CHECKING DASHBOARD QUERY FOR YEAR 6 MEASUREMENTS")
    print("=" * 100)
    print()
    
    # Get level and topic
    level_6 = Level.objects.filter(level_number=6).first()
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    
    if not level_6 or not measurements_topic:
        print("[ERROR] Level 6 or Measurements topic not found!")
        return
    
    # Get admin user
    admin = CustomUser.objects.filter(username="admin").first()
    if not admin:
        print("[ERROR] Admin user not found!")
        return
    
    print(f"[INFO] Checking for user: {admin.username} (ID: {admin.id})")
    print()
    
    # Get all student answers (same as dashboard)
    student_answers = StudentAnswer.objects.filter(
        student=admin
    ).select_related('question', 'question__level', 'question__topic')
    
    print(f"[INFO] Total answers for admin: {student_answers.count()}")
    print()
    
    # Filter for Year 6 Measurements
    student_answers_with_topics = student_answers.filter(
        question__level=level_6,
        question__topic=measurements_topic
    ).exclude(session_id='')
    
    print(f"[INFO] Year 6 Measurements answers (with session_id): {student_answers_with_topics.count()}")
    print()
    
    # Get unique combinations (same as dashboard)
    unique_combinations = student_answers_with_topics.values(
        'question__level__level_number',
        'question__topic__name',
        'session_id'
    ).distinct()
    
    print(f"[INFO] Unique (level, topic, session) combinations: {unique_combinations.count()}")
    print()
    
    # Check each combination
    for combo in unique_combinations:
        level_num = combo['question__level__level_number']
        topic_name = combo['question__topic__name']
        session_id = combo['session_id']
        
        print(f"  Level: {level_num}, Topic: {topic_name}, Session: {session_id[:8]}...")
        
        # Get answers for this session
        session_answers = student_answers_with_topics.filter(
            session_id=session_id,
            question__level__level_number=level_num,
            question__topic__name=topic_name
        )
        
        answer_count = session_answers.count()
        print(f"    Answer count: {answer_count}")
        
        # Check question limit
        YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
        standard_limit = YEAR_QUESTION_COUNTS.get(level_num, 20)
        
        # Get available questions
        available_questions = Question.objects.filter(
            level=level_6,
            topic=measurements_topic
        ).count()
        
        question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
        
        print(f"    Question limit: {question_limit} (available: {available_questions}, standard: {standard_limit})")
        print(f"    Meets requirement: {answer_count >= question_limit}")
        
        if answer_count >= question_limit:
            # Check time_taken_seconds
            first_answer = session_answers.first()
            has_time = first_answer and first_answer.time_taken_seconds > 0
            time_value = first_answer.time_taken_seconds if first_answer else 0
            print(f"    Has time_taken_seconds: {has_time} ({time_value}s)")
            
            # Calculate points
            if has_time:
                total_correct = sum(1 for a in session_answers if a.is_correct)
                total_questions = session_answers.count()
                percentage = (total_correct / total_questions) if total_questions else 0
                final_points = (percentage * 100 * 60) / time_value if time_value else 0
                print(f"    Points: {round(final_points, 2)} ({total_correct}/{total_questions} correct)")
        
        print()
    
    # Now check what the dashboard_detail view would return
    print("=" * 100)
    print("SIMULATING DASHBOARD_DETAIL VIEW")
    print("=" * 100)
    print()
    
    # Group by level and topic (same as dashboard_detail)
    level_topic_data = {}
    for answer in student_answers_with_topics:
        level_num = answer.question.level.level_number
        topic_name = answer.question.topic.name if answer.question.topic else "Unknown"
        session_id = answer.session_id
        
        key = (level_num, topic_name)
        if key not in level_topic_data:
            level_topic_data[key] = set()
        level_topic_data[key].add(session_id)
    
    for (level_num, topic_name), session_ids in level_topic_data.items():
        print(f"Level {level_num} - {topic_name}: {len(session_ids)} unique sessions")
        
        # Get available questions
        level_obj = Level.objects.filter(level_number=level_num).first()
        topic_obj = Topic.objects.filter(name=topic_name).first()
        
        if level_obj and topic_obj:
            available_questions = Question.objects.filter(
                level=level_obj,
                topic=topic_obj
            ).count()
        else:
            available_questions = 0
        
        standard_limit = YEAR_QUESTION_COUNTS.get(level_num, 20)
        question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
        
        print(f"  Question limit: {question_limit}")
        print(f"  Available questions: {available_questions}")
        print()
        
        completed_sessions = []
        for session_id in session_ids:
            session_answers = student_answers_with_topics.filter(
                session_id=session_id,
                question__level__level_number=level_num,
                question__topic__name=topic_name
            )
            answer_count = session_answers.count()
            
            if answer_count >= question_limit:
                completed_sessions.append(session_id)
                print(f"    [OK] Session {session_id[:8]}...: {answer_count} answers - WILL APPEAR")
            else:
                print(f"    [SKIP] Session {session_id[:8]}...: {answer_count} answers - NEEDS {question_limit}")
        
        print(f"  Total completed sessions: {len(completed_sessions)}")
        print()

if __name__ == "__main__":
    check_dashboard_query()

