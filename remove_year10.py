#!/usr/bin/env python
"""
Remove Year 10 level from the database
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Question, Answer, StudentAnswer, BasicFactsResult

def remove_year10():
    """Remove Year 10 level and all associated data"""
    
    level_10 = Level.objects.filter(level_number=10).first()
    
    if not level_10:
        print("❌ Year 10 level not found in database.")
        return
    
    print(f"🔍 Year 10 found: {level_10}")
    
    # Check for associated data
    questions_count = Question.objects.filter(level=level_10).count()
    student_answers_count = StudentAnswer.objects.filter(question__level=level_10).count()
    basic_facts_results_count = BasicFactsResult.objects.filter(level=level_10).count()
    
    print(f"\n📊 Associated data:")
    print(f"   Questions: {questions_count}")
    print(f"   Student Answers: {student_answers_count}")
    print(f"   Basic Facts Results: {basic_facts_results_count}")
    
    if questions_count > 0:
        # Delete answers first (they reference questions)
        questions = Question.objects.filter(level=level_10)
        for question in questions:
            Answer.objects.filter(question=question).delete()
        print(f"   ✅ Deleted {questions_count} answer(s)")
    
    # Delete student answers
    if student_answers_count > 0:
        StudentAnswer.objects.filter(question__level=level_10).delete()
        print(f"   ✅ Deleted {student_answers_count} student answer(s)")
    
    # Delete basic facts results
    if basic_facts_results_count > 0:
        BasicFactsResult.objects.filter(level=level_10).delete()
        print(f"   ✅ Deleted {basic_facts_results_count} basic facts result(s)")
    
    # Delete questions
    if questions_count > 0:
        Question.objects.filter(level=level_10).delete()
        print(f"   ✅ Deleted {questions_count} question(s)")
    
    # Finally, delete the level
    level_title = level_10.title
    level_10.delete()
    
    print(f"\n✅ Successfully removed Year 10 level: {level_title}")
    print(f"   All associated data has been deleted.")

if __name__ == "__main__":
    print("⚠️  This will permanently delete Year 10 level and all associated data.")
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        remove_year10()
    else:
        print("❌ Operation cancelled.")

