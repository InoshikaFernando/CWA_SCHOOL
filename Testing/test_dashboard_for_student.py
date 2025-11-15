"""
Test what the dashboard would return for a specific student.
Simulates the dashboard_detail view logic.
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

def test_dashboard_for_student(username):
    """
    Simulate what dashboard_detail would return for a specific student.
    """
    print("=" * 100)
    print(f"TESTING DASHBOARD FOR: {username}")
    print("=" * 100)
    
    try:
        student = CustomUser.objects.get(username=username, is_teacher=False)
    except CustomUser.DoesNotExist:
        print(f"[ERROR] Student '{username}' not found")
        return
    
    # Simulate the dashboard_detail view logic
    from maths.views import calculate_age_from_dob, get_or_create_age_level, get_or_create_formatted_topic
    
    # Get all student answers
    student_answers = StudentAnswer.objects.filter(
        student=student
    ).select_related('question', 'question__level', 'question__topic')
    
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    
    # PRIMARY: Get all level-topic combinations from StudentFinalAnswer table
    final_answer_combinations = StudentFinalAnswer.objects.filter(
        student=student
    ).values(
        'level__level_number',
        'topic__name'
    ).distinct()
    
    print(f"\n[Step 1] StudentFinalAnswer combinations: {final_answer_combinations.count()}")
    for item in final_answer_combinations:
        print(f"  - Year {item['level__level_number']}: {item['topic__name']}")
    
    # Build level_topic_data from StudentFinalAnswer (primary source)
    level_topic_data = {}
    for item in final_answer_combinations:
        level_num = item['level__level_number']
        topic_name = item['topic__name']
        key = (level_num, topic_name)
        if key not in level_topic_data:
            level_topic_data[key] = set()
    
    # FALLBACK: Also get combinations from StudentAnswer
    student_answers_with_topics = student_answers.filter(question__topic__isnull=False)
    unique_level_topic_sessions = student_answers_with_topics.values(
        'question__level__level_number', 
        'question__topic__name',
        'session_id'
    ).distinct()
    
    # Add StudentAnswer combinations
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
    
    print(f"\n[Step 2] Total level-topic combinations: {len(level_topic_data)}")
    for (level_num, topic_name) in level_topic_data.keys():
        print(f"  - Year {level_num}: {topic_name}")
    
    # Process each combination
    progress_by_level = []
    
    for (level_num, topic_name), session_ids in level_topic_data.items():
        attempts_data = []
        completed_session_ids = []
        
        print(f"\n{'=' * 100}")
        print(f"Processing: Year {level_num} - {topic_name}")
        print(f"{'=' * 100}")
        
        # Get level info
        try:
            level_obj = Level.objects.get(level_number=level_num)
            level_name = f"Level {level_num}" if level_num >= 100 else f"Year {level_num}"
        except Level.DoesNotExist:
            print(f"  [ERROR] Level {level_num} not found")
            continue
        
        # Get topic object
        topic_obj = Topic.objects.filter(name=topic_name).first()
        if not topic_obj:
            print(f"  [ERROR] Topic '{topic_name}' not found")
            continue
        
        print(f"  Level: {level_obj} (ID: {level_obj.id})")
        print(f"  Topic: {topic_obj} (ID: {topic_obj.id})")
        
        # PRIMARY: Try to get results from StudentFinalAnswer table
        final_answer_records = StudentFinalAnswer.objects.filter(
            student=student,
            level=level_obj,
            topic=topic_obj
        ).order_by('-points_earned')
        
        print(f"\n  [PRIMARY] StudentFinalAnswer query:")
        print(f"    Filter: student={student.username}, level={level_obj.level_number}, topic={topic_obj.name}")
        print(f"    Found: {final_answer_records.count()} records")
        
        if final_answer_records.exists():
            print(f"  [USING StudentFinalAnswer]")
            for fa in final_answer_records:
                print(f"    - Attempt {fa.attempt_number}: {fa.points_earned} points (Session: {fa.session_id[:36]}...)")
                attempts_data.append({
                    'points': float(fa.points_earned),
                    'time_seconds': 0,
                    'date': fa.last_updated_time
                })
                completed_session_ids.append(fa.session_id)
        else:
            print(f"  [FALLBACK] No StudentFinalAnswer records, using StudentAnswer")
            # This shouldn't happen if we have StudentFinalAnswer records
            pass
        
        if attempts_data:
            points_list = [a['points'] for a in attempts_data]
            best_score = max(points_list)
            best_attempt = max(attempts_data, key=lambda x: x['points'])
            
            print(f"\n  [RESULT] Will appear on dashboard:")
            print(f"    Best points: {best_score}")
            print(f"    Total attempts: {len(attempts_data)}")
            print(f"    Best date: {best_attempt['date']}")
            
            progress_by_level.append({
                'level_number': level_num,
                'level_name': level_name,
                'topic_name': topic_name,
                'total_attempts': len(completed_session_ids),
                'best_points': best_score,
                'best_time_seconds': best_attempt['time_seconds'],
                'best_date': best_attempt['date'],
            })
        else:
            print(f"\n  [RESULT] Will NOT appear on dashboard (no attempts_data)")
    
    print(f"\n{'=' * 100}")
    print(f"FINAL SUMMARY")
    print(f"{'=' * 100}")
    print(f"Total progress items: {len(progress_by_level)}")
    
    if progress_by_level:
        print(f"\nItems that WILL appear on dashboard:")
        for item in progress_by_level:
            print(f"  - {item['level_name']} {item['topic_name']}: {item['best_points']} points ({item['total_attempts']} attempts)")
    else:
        print(f"\n[WARNING] No items will appear on dashboard!")
        print(f"\nDebugging info:")
        print(f"  - StudentFinalAnswer records: {StudentFinalAnswer.objects.filter(student=student).count()}")
        print(f"  - StudentAnswer records: {student_answers.count()}")
        
        # Check if there's a mismatch in level/topic
        final_answers = StudentFinalAnswer.objects.filter(student=student)
        for fa in final_answers:
            print(f"\n  StudentFinalAnswer record:")
            print(f"    Level: {fa.level} (level_number: {fa.level.level_number})")
            print(f"    Topic: {fa.topic} (name: '{fa.topic.name}')")
            print(f"    Points: {fa.points_earned}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test dashboard for a specific student')
    parser.add_argument('--username', type=str, required=True, help='Username to test')
    args = parser.parse_args()
    
    test_dashboard_for_student(args.username)

