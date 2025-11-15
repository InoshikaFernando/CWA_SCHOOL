#!/usr/bin/env python
"""
Verify that the dashboard data is correct and will display
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

def verify_dashboard_data():
    """Verify dashboard data matches what the view expects"""
    
    print("=" * 100)
    print("VERIFYING DASHBOARD DATA")
    print("=" * 100)
    print()
    
    # Get admin user
    admin = CustomUser.objects.filter(username="admin").first()
    if not admin:
        print("[ERROR] Admin user not found!")
        return
    
    print(f"[INFO] User: {admin.username} (ID: {admin.id})")
    print()
    
    # Simulate the exact dashboard_detail view logic
    from maths.views import dashboard_detail
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/dashboard/detail/')
    request.user = admin
    
    # Get all student answers (same as dashboard_detail)
    student_answers = StudentAnswer.objects.filter(
        student=admin
    ).select_related('question', 'question__level', 'question__topic')
    
    # Filter for answers with topics
    student_answers_with_topics = student_answers.filter(question__topic__isnull=False)
    
    # Get unique combinations
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
    
    print(f"[INFO] Found {len(level_topic_data)} level-topic combinations")
    print()
    
    # Check Year 6 Measurements specifically
    year6_measurements_key = (6, "Measurements")
    if year6_measurements_key in level_topic_data:
        session_ids = level_topic_data[year6_measurements_key]
        print(f"[INFO] Year 6 Measurements: {len(session_ids)} unique sessions")
        
        level_6 = Level.objects.filter(level_number=6).first()
        measurements_topic = Topic.objects.filter(name="Measurements").first()
        
        if level_6 and measurements_topic:
            available_questions = Question.objects.filter(
                level=level_6,
                topic=measurements_topic
            ).count()
            
            YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
            standard_limit = YEAR_QUESTION_COUNTS.get(6, 20)
            question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
            
            print(f"  Available questions: {available_questions}")
            print(f"  Question limit: {question_limit}")
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
                
                if answer_count >= question_limit:
                    completed_sessions.append(session_id)
                    first_answer = session_answers.first()
                    if first_answer:
                        print(f"    - Has time_taken_seconds: {first_answer.time_taken_seconds > 0} ({first_answer.time_taken_seconds}s)")
                        print(f"    - First answer date: {first_answer.answered_at}")
                        total_correct = sum(1 for a in session_answers if a.is_correct)
                        print(f"    - Correct: {total_correct}/{answer_count}")
                        if first_answer.time_taken_seconds > 0:
                            percentage = (total_correct / answer_count) if answer_count else 0
                            final_points = (percentage * 100 * 60) / first_answer.time_taken_seconds if first_answer.time_taken_seconds else 0
                            print(f"    - Points: {round(final_points, 2)}")
                else:
                    print(f"    - [INCOMPLETE] Needs {question_limit} answers")
                print()
            
            print(f"[RESULT] Year 6 Measurements will show {len(completed_sessions)} completed session(s) on dashboard")
        else:
            print("[ERROR] Level 6 or Measurements topic not found!")
    else:
        print("[WARNING] Year 6 Measurements not found in level_topic_data!")
        print(f"Available keys: {list(level_topic_data.keys())}")
    
    print()
    print("=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    print()
    print("If the dashboard is not showing results, try:")
    print("1. Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)")
    print("2. Clear browser cache")
    print("3. Log out and log back in")
    print("4. Make sure you're viewing the 'Detailed Dashboard' page")
    print("5. Check that you're logged in as the correct user (admin)")
    print()

if __name__ == "__main__":
    verify_dashboard_data()

