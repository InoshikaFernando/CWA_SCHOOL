#!/usr/bin/env python
"""
Add sample Year 3 Fractions results to the progress table
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, Level, StudentAnswer, CustomUser
from django.db.models import Q

def add_year3_fractions_results():
    """Add sample Year 3 Fractions results for a student"""
    
    # Get Year 3 level
    level_3 = Level.objects.filter(level_number=3).first()
    if not level_3:
        print("❌ Error: Year 3 level not found!")
        return
    
    # Get Fractions questions for Year 3
    # Questions that contain fraction-related keywords
    fractions_questions = Question.objects.filter(
        level=level_3
    ).filter(
        Q(question_text__icontains='numerator') |
        Q(question_text__icontains='denominator') |
        Q(question_text__icontains='fraction') |
        Q(question_text__icontains='coloured') |
        Q(question_text__icontains='shaded')
    ).distinct()
    
    if not fractions_questions.exists():
        print("❌ Error: No Fractions questions found for Year 3!")
        print("   Make sure you've run add_fractions_year3.py first.")
        return
    
    print(f"📝 Found {fractions_questions.count()} Fractions questions for Year 3")
    
    # Get or use first student
    students = CustomUser.objects.filter(is_teacher=False)
    if not students.exists():
        print("❌ Error: No students found in the database!")
        print("   Please create a student account first.")
        return
    
    # Use first student (or you can modify to specify a username)
    student = students.first()
    print(f"👤 Using student: {student.username}")
    
    # Generate a unique session ID for this attempt
    session_id = f"year3_fractions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n🔄 Creating Year 3 Fractions results...")
    print(f"   Session ID: {session_id}")
    
    # Get a subset of questions (e.g., 12 questions as per YEAR_QUESTION_COUNTS)
    question_limit = 12
    selected_questions = list(fractions_questions)[:question_limit]
    
    created_count = 0
    correct_count = 0
    total_points = 0
    total_time = 0
    
    for i, question in enumerate(selected_questions, 1):
        # Get correct answer
        correct_answer = Answer.objects.filter(question=question, is_correct=True).first()
        
        if not correct_answer:
            print(f"  ⚠️  Question {i}: No correct answer found, skipping...")
            continue
        
        # Randomly decide if answer is correct (80% correct rate for realistic data)
        is_correct = random.random() < 0.8
        
        if is_correct:
            selected_answer = correct_answer
            points_earned = question.points
            correct_count += 1
        else:
            # Select a wrong answer
            wrong_answers = Answer.objects.filter(question=question, is_correct=False)
            if wrong_answers.exists():
                selected_answer = random.choice(list(wrong_answers))
            else:
                selected_answer = correct_answer  # Fallback
            points_earned = 0
        
        # Random time between 5-30 seconds per question
        time_taken = random.randint(5, 30)
        total_time += time_taken
        
        # Create or update student answer
        student_answer, created = StudentAnswer.objects.update_or_create(
            student=student,
            question=question,
            defaults={
                'selected_answer': selected_answer,
                'is_correct': is_correct,
                'points_earned': points_earned,
                'session_id': session_id,
                'time_taken_seconds': time_taken,
                'answered_at': timezone.now() - timedelta(minutes=len(selected_questions) - i)
            }
        )
        
        if created:
            created_count += 1
            status = "✅" if is_correct else "❌"
            print(f"  {status} Question {i}: {question.question_text[:50]}... ({'Correct' if is_correct else 'Wrong'})")
        
        total_points += points_earned
    
    # Calculate score percentage
    max_points = sum(q.points for q in selected_questions)
    score_percentage = (total_points / max_points * 100) if max_points > 0 else 0
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count} answers")
    print(f"   ✅ Correct: {correct_count}/{len(selected_questions)}")
    print(f"   📈 Points: {total_points}/{max_points} ({score_percentage:.2f}%)")
    print(f"   ⏱️  Total Time: {total_time}s ({total_time//60}m {total_time%60}s)")
    print(f"\n✅ Year 3 Fractions results added successfully!")
    print(f"   The progress should now appear in the dashboard for {student.username}")

if __name__ == "__main__":
    print("🔄 Adding Year 3 Fractions results...\n")
    add_year3_fractions_results()
    print("\n✅ Done!")

