#!/usr/bin/env python
"""
Calculate and update statistics (average and sigma) for each topic-level combination
This should be called whenever a student completes an exercise or beats their record
"""
import os
import sys
import django
import math

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, StudentAnswer, TopicLevelStatistics, CustomUser
from django.db.models import Q
from collections import defaultdict
from datetime import date

def calculate_age_from_dob(date_of_birth):
    """
    Calculate age from date of birth (integer years only, ignoring months).
    For example: 6 years and 4 months -> returns 6
    """
    if not date_of_birth:
        return None
    today = date.today()
    # Calculate age in years only (integer, no rounding)
    # If birthday hasn't occurred this year, subtract 1
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age

def get_or_create_age_level(age):
    """Get or create a Level object for a specific age (for Basic Facts statistics)"""
    # Use level_number = 2000 + age to avoid conflicts with regular levels (2-9) and Basic Facts (100+)
    age_level_number = 2000 + age
    age_level, created = Level.objects.get_or_create(
        level_number=age_level_number,
        defaults={'title': f"Age {age}"}
    )
    return age_level

def get_or_create_formatted_topic(level_number, topic_name):
    """Get or create a Topic with formatted name for Basic Facts: {level_number}_{topic_name}"""
    formatted_name = f"{level_number}_{topic_name}"
    topic, created = Topic.objects.get_or_create(name=formatted_name)
    return topic

def calculate_topic_level_statistics(level_num=None, topic_name=None):
    """
    Calculate average and standard deviation for each topic-level combination
    based on all students' best points for that combination.
    
    For Basic Facts (level_number >= 100):
    - Level is based on student's age (from date_of_birth)
    - Topic is formatted as {level_number}_{topic_name} (e.g., "100_Addition")
    
    Args:
        level_num: Optional level number to calculate for specific level only
        topic_name: Optional topic name to calculate for specific topic only
    """
    print("=" * 80)
    print("CALCULATING TOPIC-LEVEL STATISTICS")
    print("=" * 80)
    
    # Separate Year levels and Basic Facts
    year_answers = StudentAnswer.objects.filter(
        question__topic__isnull=False,
        question__level__level_number__lt=100  # Year levels (2-9)
    ).select_related('question', 'question__level', 'question__topic', 'student')
    
    basic_facts_answers = StudentAnswer.objects.filter(
        question__topic__isnull=False,
        question__level__level_number__gte=100  # Basic Facts (>= 100)
    ).select_related('question', 'question__level', 'question__topic', 'student')
    
    updated_count = 0
    created_count = 0
    
    # Process Year levels (existing logic)
    if level_num is None or level_num < 100:
        # Filter by level if specified
        if level_num is not None:
            year_answers = year_answers.filter(question__level__level_number=level_num)
        
        # Filter by topic if specified
        if topic_name is not None:
            year_answers = year_answers.filter(question__topic__name=topic_name)
        
        # Get unique level-topic combinations (only process each once)
        unique_combinations = year_answers.values(
            'question__level__level_number',
            'question__topic__name'
        ).distinct()
        
        # Convert to set of tuples to ensure true uniqueness
        processed_combinations = set()
        
        YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
        
        for combo in unique_combinations:
            level_num_val = combo['question__level__level_number']
            topic_name_val = combo['question__topic__name']
            
            # Skip if we've already processed this combination
            combo_key = (level_num_val, topic_name_val)
            if combo_key in processed_combinations:
                continue
            processed_combinations.add(combo_key)
            
            try:
                level_obj = Level.objects.get(level_number=level_num_val)
                topic_obj = Topic.objects.filter(name=topic_name_val).first()
                
                if not topic_obj:
                    continue
                
                # Get available questions count
                available_questions = Question.objects.filter(
                    level=level_obj,
                    topic=topic_obj
                ).count()
                
                standard_limit = YEAR_QUESTION_COUNTS.get(level_num_val, 10)
                question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
                
                # Get all students who have completed this topic-level
                # Group by student and session to find best attempt for each student
                student_best_points = {}
                
                # Get all unique student-session combinations for this level-topic
                student_sessions = year_answers.filter(
                    question__level__level_number=level_num_val,
                    question__topic__name=topic_name_val
                ).values('student', 'session_id').distinct()
                
                for student_session in student_sessions:
                    student_id = student_session['student']
                    session_id = student_session['session_id']
                    
                    if not session_id:
                        continue
                    
                    # Get all answers for this student-session combination
                    session_answers = year_answers.filter(
                        student_id=student_id,
                        session_id=session_id,
                        question__level__level_number=level_num_val,
                        question__topic__name=topic_name_val
                    )
                    
                    # Count attempts that meet the full limit OR are close to it (90% threshold)
                    # This matches the dashboard logic
                    partial_threshold = int(question_limit * 0.9)  # 90% of required questions
                    if session_answers.count() < partial_threshold:
                        continue
                    
                    # Calculate points for this attempt
                    first_answer = session_answers.first()
                    if first_answer and first_answer.time_taken_seconds > 0:
                        total_correct = sum(1 for a in session_answers if a.is_correct)
                        total_questions = session_answers.count()
                        time_seconds = first_answer.time_taken_seconds
                        
                        percentage = (total_correct / total_questions) if total_questions else 0
                        final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
                    else:
                        final_points = sum(a.points_earned for a in session_answers)
                    
                    # Track best points for each student
                    if student_id not in student_best_points:
                        student_best_points[student_id] = final_points
                    else:
                        student_best_points[student_id] = max(student_best_points[student_id], final_points)
                
                # Calculate statistics
                if len(student_best_points) >= 2:  # Need at least 2 students for meaningful statistics
                    points_list = list(student_best_points.values())
                    avg = sum(points_list) / len(points_list)
                    
                    # Calculate standard deviation
                    variance = sum((x - avg) ** 2 for x in points_list) / len(points_list)
                    sigma = math.sqrt(variance)
                    
                    # Get or create statistics record
                    stats, created = TopicLevelStatistics.objects.get_or_create(
                        level=level_obj,
                        topic=topic_obj,
                        defaults={
                            'average_points': round(avg, 2),
                            'sigma': round(sigma, 2),
                            'student_count': len(student_best_points)
                        }
                    )
                    
                    if not created:
                        # Update existing record
                        stats.average_points = round(avg, 2)
                        stats.sigma = round(sigma, 2)
                        stats.student_count = len(student_best_points)
                        stats.save()
                        updated_count += 1
                    else:
                        created_count += 1
                    
                    print(f"  {'[CREATED]' if created else '[UPDATED]'} Year {level_num_val} - {topic_name_val}: "
                          f"avg={round(avg, 2)}, sigma={round(sigma, 2)}, n={len(student_best_points)}")
                else:
                    # Not enough data - set to defaults or skip
                    stats, created = TopicLevelStatistics.objects.get_or_create(
                        level=level_obj,
                        topic=topic_obj,
                        defaults={
                            'average_points': 0,
                            'sigma': 0,
                            'student_count': len(student_best_points)
                        }
                    )
                    if not created:
                        stats.student_count = len(student_best_points)
                        stats.save()
                    # Skip printing for individual combinations with not enough data to reduce noise
                    if len(student_best_points) == 1:
                        print(f"  [SKIP] Year {level_num_val} - {topic_name_val}: Only 1 student (need 2+ for statistics)")
            except Exception as e:
                print(f"  [ERROR] Year {level_num_val} - {topic_name_val}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # Process Basic Facts levels (group by age and formatted topic)
    if level_num is None or level_num >= 100:
        # Filter by level if specified
        if level_num is not None:
            basic_facts_answers = basic_facts_answers.filter(question__level__level_number=level_num)
        
        # Filter by topic if specified
        if topic_name is not None:
            basic_facts_answers = basic_facts_answers.filter(question__topic__name=topic_name)
        
        # Group Basic Facts by (age, level_number, topic_name)
        age_level_topic_combinations = defaultdict(lambda: defaultdict(lambda: {'students': set(), 'sessions': []}))
        
        # Get all unique student-session combinations for Basic Facts
        student_sessions = basic_facts_answers.values('student', 'session_id', 'question__level__level_number', 'question__topic__name').distinct()
        
        for student_session in student_sessions:
            student_id = student_session['student']
            session_id = student_session['session_id']
            level_num_val = student_session['question__level__level_number']
            topic_name_val = student_session['question__topic__name']
            
            if not session_id:
                continue
            
            # Get student to calculate age
            try:
                student = CustomUser.objects.get(id=student_id)
                age = calculate_age_from_dob(student.date_of_birth)
                if not age:
                    continue  # Skip if no date of birth
            except CustomUser.DoesNotExist:
                continue
            
            # Format topic name: {level_number}_{topic_name}
            formatted_topic_name = f"{level_num_val}_{topic_name_val}"
            
            # Store session info
            age_level_topic_combinations[age][formatted_topic_name]['students'].add(student_id)
            age_level_topic_combinations[age][formatted_topic_name]['sessions'].append({
                'student_id': student_id,
                'session_id': session_id,
                'level_number': level_num_val,
                'topic_name': topic_name_val
            })
        
        # Process each age-topic combination
        for age, topics_dict in age_level_topic_combinations.items():
            for formatted_topic_name, data in topics_dict.items():
                # Get level_number and original topic_name from formatted name
                # Format is: {level_number}_{topic_name}
                parts = formatted_topic_name.rsplit('_', 1)
                if len(parts) != 2:
                    continue
                try:
                    level_num_val = int(parts[0])
                    original_topic_name = parts[1]
                except ValueError:
                    continue
                
                # Get or create age level and formatted topic
                age_level = get_or_create_age_level(age)
                formatted_topic = get_or_create_formatted_topic(level_num_val, original_topic_name)
                
                # Get available questions count (for the original level and topic)
                original_level = Level.objects.filter(level_number=level_num_val).first()
                original_topic = Topic.objects.filter(name=original_topic_name).first()
                
                if not original_level or not original_topic:
                    continue
                
                available_questions = Question.objects.filter(
                    level=original_level,
                    topic=original_topic
                ).count()
                
                # Basic Facts typically have 10 questions per level
                question_limit = min(available_questions, 10) if available_questions > 0 else 10
                
                # Calculate best points for each student
                student_best_points = {}
                
                for session_info in data['sessions']:
                    student_id = session_info['student_id']
                    session_id = session_info['session_id']
                    level_num_val = session_info['level_number']
                    topic_name_val = session_info['topic_name']
                    
                    # Get all answers for this student-session combination
                    session_answers = basic_facts_answers.filter(
                        student_id=student_id,
                        session_id=session_id,
                        question__level__level_number=level_num_val,
                        question__topic__name=topic_name_val
                    )
                    
                    # Only count full attempts
                    if session_answers.count() < question_limit:
                        continue
                    
                    # Calculate points for this attempt
                    first_answer = session_answers.first()
                    if first_answer and first_answer.time_taken_seconds > 0:
                        total_correct = sum(1 for a in session_answers if a.is_correct)
                        total_questions = session_answers.count()
                        time_seconds = first_answer.time_taken_seconds
                        
                        percentage = (total_correct / total_questions) if total_questions else 0
                        final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
                    else:
                        final_points = sum(a.points_earned for a in session_answers)
                    
                    # Track best points for each student
                    if student_id not in student_best_points:
                        student_best_points[student_id] = final_points
                    else:
                        student_best_points[student_id] = max(student_best_points[student_id], final_points)
                
                # Calculate statistics
                if len(student_best_points) >= 2:  # Need at least 2 students
                    points_list = list(student_best_points.values())
                    avg = sum(points_list) / len(points_list)
                    
                    # Calculate standard deviation
                    variance = sum((x - avg) ** 2 for x in points_list) / len(points_list)
                    sigma = math.sqrt(variance)
                    
                    # Update or create statistics record
                    stats, created = TopicLevelStatistics.objects.get_or_create(
                        level=age_level,
                        topic=formatted_topic,
                        defaults={
                            'average_points': round(avg, 2),
                            'sigma': round(sigma, 2),
                            'student_count': len(student_best_points)
                        }
                    )
                    
                    if not created:
                        stats.average_points = round(avg, 2)
                        stats.sigma = round(sigma, 2)
                        stats.student_count = len(student_best_points)
                        stats.save()
                        updated_count += 1
                    else:
                        created_count += 1
                    
                    print(f"  {'[CREATED]' if created else '[UPDATED]'} Age {age} - {formatted_topic_name}: "
                          f"avg={round(avg, 2)}, sigma={round(sigma, 2)}, n={len(student_best_points)}")
    
    print("\n" + "=" * 80)
    print("STATISTICS CALCULATION COMPLETE")
    print("=" * 80)
    print(f"Created: {created_count} records")
    print(f"Updated: {updated_count} records")
    print("=" * 80)
    
    return created_count + updated_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate topic-level statistics')
    parser.add_argument('--level', type=int, help='Calculate for specific level only')
    parser.add_argument('--topic', type=str, help='Calculate for specific topic only')
    args = parser.parse_args()
    
    calculate_topic_level_statistics(level_num=args.level, topic_name=args.topic)

