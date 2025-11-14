#!/usr/bin/env python
"""
Get all student results across all topics and levels.
Shows comprehensive results for all students.
"""
import os
import sys
import django
from collections import defaultdict
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from maths.models import CustomUser, StudentAnswer, Question, Topic, Level, BasicFactsResult

YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}


def get_question_limit(level_obj, topic_obj):
    """Return the number of questions expected for a full attempt."""
    level_num = level_obj.level_number
    if level_num < 100:
        standard_limit = YEAR_QUESTION_COUNTS.get(level_num, 10)
        available_questions = Question.objects.filter(level=level_obj, topic=topic_obj).count()
        return min(available_questions, standard_limit) if available_questions > 0 else standard_limit
    else:
        # Basic Facts
        available_questions = Question.objects.filter(level=level_obj, topic=topic_obj).count()
        return min(available_questions, 10) if available_questions > 0 else 10


def get_all_student_results():
    """Get comprehensive results for all students."""
    
    print("=" * 100)
    print("ALL STUDENT RESULTS REPORT")
    print("=" * 100)
    print(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get all active students
    students = CustomUser.objects.filter(is_teacher=False, is_active=True).order_by('username')
    total_students = students.count()
    
    print(f"[INFO] Found {total_students} active students\n")
    
    if total_students == 0:
        print("[INFO] No active students found.")
        return
    
    # Get all topics
    all_topics = Topic.objects.all().order_by('name')
    
    # Get all levels
    all_levels = Level.objects.all().order_by('level_number')
    
    # Statistics
    students_with_results = 0
    total_sessions = 0
    total_answers = 0
    
    # Process each student
    for student_idx, student in enumerate(students, 1):
        print("=" * 100)
        print(f"STUDENT {student_idx}/{total_students}: {student.username}")
        print("=" * 100)
        print(f"Name:  {student.get_full_name() or 'N/A'}")
        print(f"Email: {student.email or 'N/A'}")
        print(f"DOB:   {student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else 'N/A'}")
        if student.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - student.date_of_birth.year - ((today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day))
            print(f"Age:   {age} years")
        print()
        
        # Get all student answers
        student_answers = StudentAnswer.objects.filter(
            student=student
        ).select_related('question', 'question__level', 'question__topic')
        
        total_answers_count = student_answers.count()
        total_answers += total_answers_count
        
        if total_answers_count == 0:
            print("[INFO] No answers found for this student.")
            print()
            continue
        
        students_with_results += 1
        
        # Filter answers with topics
        answers_with_topics = student_answers.filter(question__topic__isnull=False)
        
        # Group by level and topic
        level_topic_sessions = defaultdict(lambda: defaultdict(set))
        
        for answer in answers_with_topics:
            if not answer.session_id:
                continue
            level_num = answer.question.level.level_number
            topic_name = answer.question.topic.name if answer.question.topic else "Unknown"
            level_topic_sessions[level_num][topic_name].add(answer.session_id)
        
        # Process Year levels (2-9)
        year_results = {}
        for level_num in sorted([ln for ln in level_topic_sessions.keys() if ln < 100]):
            level_obj = Level.objects.filter(level_number=level_num).first()
            if not level_obj:
                continue
            
            level_name = f"Year {level_num}"
            year_results[level_name] = {}
            
            for topic_name in sorted(level_topic_sessions[level_num].keys()):
                topic_obj = Topic.objects.filter(name=topic_name).first()
                if not topic_obj:
                    continue
                
                sessions = level_topic_sessions[level_num][topic_name]
                question_limit = get_question_limit(level_obj, topic_obj)
                
                session_results = []
                for session_id in sessions:
                    session_answers = answers_with_topics.filter(
                        session_id=session_id,
                        question__level__level_number=level_num,
                        question__topic__name=topic_name
                    )
                    
                    if session_answers.count() < question_limit:
                        continue
                    
                    total_sessions += 1
                    
                    first_answer = session_answers.first()
                    time_seconds = first_answer.time_taken_seconds if first_answer else 0
                    total_questions = session_answers.count()
                    correct_count = sum(1 for a in session_answers if a.is_correct)
                    
                    if time_seconds > 0:
                        percentage = (correct_count / total_questions) if total_questions else 0
                        points = (percentage * 100 * 60) / time_seconds
                    else:
                        points = sum(a.points_earned for a in session_answers)
                    
                    session_results.append({
                        'session_id': session_id,
                        'points': round(points, 2),
                        'correct': correct_count,
                        'total': total_questions,
                        'date': first_answer.answered_at if first_answer else None,
                        'time_seconds': time_seconds
                    })
                
                if session_results:
                    # Get best result
                    best_result = max(session_results, key=lambda x: x['points'])
                    year_results[level_name][topic_name] = {
                        'best': best_result,
                        'all_sessions': session_results,
                        'total_attempts': len(session_results)
                    }
        
        # Process Basic Facts levels (>= 100)
        basic_facts_results = {}
        for level_num in sorted([ln for ln in level_topic_sessions.keys() if ln >= 100]):
            level_obj = Level.objects.filter(level_number=level_num).first()
            if not level_obj:
                continue
            
            # Get Basic Facts results from database
            bf_results = BasicFactsResult.objects.filter(
                student=student,
                level=level_obj
            ).order_by('-points')
            
            if bf_results.exists():
                best_result = bf_results.first()
                basic_facts_results[level_num] = {
                    'best_points': float(best_result.points),
                    'best_time': best_result.time_taken_seconds,
                    'best_date': best_result.completed_at,
                    'total_attempts': bf_results.values('session_id').distinct().count()
                }
        
        # Display Year level results
        if year_results:
            print("YEAR LEVEL RESULTS:")
            print("-" * 100)
            for level_name in sorted(year_results.keys()):
                print(f"\n{level_name}:")
                for topic_name in sorted(year_results[level_name].keys()):
                    data = year_results[level_name][topic_name]
                    best = data['best']
                    date_str = best['date'].strftime("%Y-%m-%d %H:%M") if best['date'] else "Unknown"
                    print(f"  {topic_name}:")
                    print(f"    Best: {best['points']} points ({best['correct']}/{best['total']} correct)")
                    print(f"    Date: {date_str}")
                    print(f"    Time: {best['time_seconds']}s")
                    print(f"    Attempts: {data['total_attempts']}")
        else:
            print("[INFO] No completed Year level sessions found.")
        
        # Display Basic Facts results
        if basic_facts_results:
            print("\nBASIC FACTS RESULTS:")
            print("-" * 100)
            for level_num in sorted(basic_facts_results.keys()):
                data = basic_facts_results[level_num]
                date_str = data['best_date'].strftime("%Y-%m-%d %H:%M") if data['best_date'] else "Unknown"
                print(f"  Level {level_num}:")
                print(f"    Best: {data['best_points']} points")
                print(f"    Time: {data['best_time']}s")
                print(f"    Date: {date_str}")
                print(f"    Attempts: {data['total_attempts']}")
        
        print()
        print(f"Total answers: {total_answers_count}")
        print()
    
    # Summary
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total students: {total_students}")
    print(f"Students with results: {students_with_results}")
    print(f"Total sessions: {total_sessions}")
    print(f"Total answers: {total_answers}")
    print("=" * 100)


if __name__ == "__main__":
    get_all_student_results()

