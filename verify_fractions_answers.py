#!/usr/bin/env python
"""
Verify that Year 3 Fractions questions have correct answer values (numbers instead of fractions)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, Level
from django.db.models import Q

def verify_fractions_answers():
    """Verify that numerator/denominator questions have number answers"""
    
    level_3 = Level.objects.filter(level_number=3).first()
    if not level_3:
        print("❌ Error: Year 3 level not found!")
        return
    
    # Get numerator/denominator questions
    questions = Question.objects.filter(
        level=level_3
    ).filter(
        Q(question_text__icontains='which number is the numerator') |
        Q(question_text__icontains='which number is the denominator')
    )
    
    print(f"🔍 Checking {questions.count()} numerator/denominator questions...\n")
    
    issues_found = False
    
    for question in questions:
        answers = Answer.objects.filter(question=question)
        print(f"Question: {question.question_text[:60]}...")
        
        # Check if any answers are fractions (contain '/')
        fraction_answers = [a for a in answers if '/' in a.answer_text]
        
        if fraction_answers:
            issues_found = True
            print(f"  ❌ ISSUE: Found fraction answers:")
            for ans in fraction_answers:
                print(f"     - '{ans.answer_text}' (correct: {ans.is_correct})")
        else:
            print(f"  ✅ All answers are numbers:")
            for ans in answers:
                print(f"     - '{ans.answer_text}' (correct: {ans.is_correct})")
        print()
    
    if not issues_found:
        print("✅ All numerator/denominator questions have correct number answers!")
    else:
        print("⚠️  Some questions still have fraction answers. Run update scripts to fix them.")

if __name__ == "__main__":
    print("🔍 Verifying Year 3 Fractions answer values...\n")
    verify_fractions_answers()
    print("\n✅ Done!")

