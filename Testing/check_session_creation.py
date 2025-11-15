"""
Script to check why multiple session IDs might be created for a single quiz attempt.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, StudentFinalAnswer, CustomUser
from django.db.models import Count
from collections import defaultdict

def check_session_creation(username=None):
    """
    Check why multiple sessions might be created for a single quiz attempt.
    """
    print("=" * 100)
    print("SESSION CREATION ANALYSIS")
    print("=" * 100)
    
    if username:
        students = CustomUser.objects.filter(username=username, is_teacher=False)
    else:
        students = CustomUser.objects.filter(is_teacher=False)
    
    if not students.exists():
        print(f"\n[ERROR] No students found" + (f" with username '{username}'" if username else ""))
        return
    
    for student in students:
        print(f"\n{'=' * 100}")
        print(f"STUDENT: {student.username}")
        print(f"{'=' * 100}")
        
        # Get all StudentAnswer records
        all_answers = StudentAnswer.objects.filter(student=student).exclude(session_id='')
        
        # Group by session_id and count answers
        session_stats = all_answers.values('session_id').annotate(
            answer_count=Count('id'),
            level_count=Count('question__level', distinct=True),
            topic_count=Count('question__topic', distinct=True)
        ).order_by('session_id')
        
        print(f"\nTotal StudentAnswer records: {all_answers.count()}")
        print(f"Unique session IDs: {session_stats.count()}")
        
        # Group by level-topic-session
        level_topic_sessions = defaultdict(list)
        for answer in all_answers.select_related('question__level', 'question__topic'):
            if answer.question.level and answer.question.topic:
                key = (answer.question.level.level_number, answer.question.topic.name)
                level_topic_sessions[key].append(answer.session_id)
        
        print(f"\nLevel-Topic-Session Analysis:")
        print(f"{'Level':<10} {'Topic':<20} {'Unique Sessions':<20} {'Total Answers':<15}")
        print("-" * 100)
        
        for (level_num, topic_name), session_ids in sorted(level_topic_sessions.items()):
            unique_sessions = len(set(session_ids))
            total_answers = len(session_ids)
            level_name = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
            print(f"{level_name:<10} {topic_name:<20} {unique_sessions:<20} {total_answers:<15}")
            
            # Check for duplicate session IDs
            session_counts = defaultdict(int)
            for sid in session_ids:
                session_counts[sid] += 1
            
            duplicates = {sid: count for sid, count in session_counts.items() if count > 1}
            if duplicates:
                print(f"  [WARNING] Duplicate session IDs found:")
                for sid, count in duplicates.items():
                    print(f"    {sid[:36]}... appears {count} times")
        
        # Check StudentFinalAnswer records
        final_answers = StudentFinalAnswer.objects.filter(student=student)
        print(f"\nStudentFinalAnswer records: {final_answers.count()}")
        
        if final_answers.exists():
            print(f"\nStudentFinalAnswer by Level-Topic:")
            print(f"{'Level':<10} {'Topic':<20} {'Attempts':<15} {'Best Points':<15}")
            print("-" * 100)
            
            for fa in final_answers.select_related('level', 'topic').order_by('level__level_number', 'topic__name', 'attempt_number'):
                level_name = f"Year {fa.level.level_number}" if fa.level.level_number < 100 else f"Level {fa.level.level_number}"
                print(f"{level_name:<10} {fa.topic.name:<20} {fa.attempt_number:<15} {fa.points_earned:<15}")
        
        # Analyze session creation patterns
        print(f"\n{'=' * 100}")
        print("SESSION CREATION PATTERN ANALYSIS")
        print(f"{'=' * 100}")
        
        # Check if sessions have very few answers (might indicate session was cleared/restarted)
        incomplete_sessions = []
        for stat in session_stats:
            if stat['answer_count'] < 5:  # Less than 5 answers
                incomplete_sessions.append(stat)
        
        if incomplete_sessions:
            print(f"\n[INFO] Found {len(incomplete_sessions)} sessions with < 5 answers (might indicate session restart):")
            for stat in incomplete_sessions[:10]:  # Show first 10
                session_id = stat['session_id']
                answers = all_answers.filter(session_id=session_id)
                levels = answers.values_list('question__level__level_number', flat=True).distinct()
                topics = answers.values_list('question__topic__name', flat=True).distinct()
                print(f"  Session: {session_id[:36]}...")
                print(f"    Answers: {stat['answer_count']}")
                print(f"    Levels: {list(levels)}")
                print(f"    Topics: {list(topics)}")
        
        # Check for sessions that span multiple topics (shouldn't happen in one quiz)
        multi_topic_sessions = []
        for stat in session_stats:
            if stat['topic_count'] > 1:
                multi_topic_sessions.append(stat)
        
        if multi_topic_sessions:
            print(f"\n[WARNING] Found {len(multi_topic_sessions)} sessions with multiple topics:")
            for stat in multi_topic_sessions[:5]:  # Show first 5
                session_id = stat['session_id']
                answers = all_answers.filter(session_id=session_id)
                topics = answers.values_list('question__topic__name', flat=True).distinct()
                print(f"  Session: {session_id[:36]}...")
                print(f"    Topics: {list(topics)}")
                print(f"    Answers: {stat['answer_count']}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Check session creation patterns')
    parser.add_argument('--username', type=str, help='Specific username to check (optional)')
    args = parser.parse_args()
    
    check_session_creation(username=args.username)

