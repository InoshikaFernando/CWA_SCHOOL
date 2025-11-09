#!/usr/bin/env python
"""
Check for Year 6 measurement questions with only one associated answer object.
This helps identify questions that might be missing wrong answer options.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, Level, Topic

def check_single_answer_questions():
    """
    Checks for Year 6 measurement questions that have only one associated Answer object.
    This might indicate an issue for multiple-choice questions expecting multiple options.
    """
    
    print("[INFO] Checking for Year 6 Measurement questions with single answers...\n")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    if not level_6:
        print("[ERROR] Year 6 level not found. Please ensure Year 6 exists in your database.")
        return
    
    # Get Measurements topic (handle duplicates by using first)
    measurements_topics = Topic.objects.filter(name="Measurements")
    if not measurements_topics.exists():
        print("[ERROR] Measurements topic not found. Please ensure 'Measurements' topic exists.")
        return
    
    # Get all Year 6 Measurement questions (from all Measurements topics in case of duplicates)
    year6_measurement_questions = Question.objects.filter(
        level=level_6,
        topic__name="Measurements"
    ).order_by('id')
    
    if not year6_measurement_questions.exists():
        print("[INFO] No Year 6 Measurement questions found.")
        return
        
    print(f"[INFO] Found {year6_measurement_questions.count()} Year 6 Measurement question(s).\n")
    
    questions_with_single_answer = []
    questions_with_no_answers = []
    questions_with_multiple_answers = []
    
    for question in year6_measurement_questions:
        answer_count = question.answers.count()
        
        if answer_count == 0:
            questions_with_no_answers.append(question)
        elif answer_count == 1:
            questions_with_single_answer.append(question)
        else:
            questions_with_multiple_answers.append(question)
    
    # Report results
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Questions with multiple answers: {len(questions_with_multiple_answers)}")
    print(f"  Questions with single answer: {len(questions_with_single_answer)}")
    print(f"  Questions with no answers: {len(questions_with_no_answers)}")
    print()
    
    if questions_with_single_answer:
        print("=" * 80)
        print(f"[WARNING] Found {len(questions_with_single_answer)} question(s) with only ONE answer:")
        print("=" * 80)
        for q in questions_with_single_answer:
            answer = q.answers.first()
            correct_marker = "[CORRECT]" if answer.is_correct else "[WRONG]"
            
            print(f"\n  Question ID: {q.id}")
            print(f"  Type: {q.question_type}")
            # Safe text encoding
            safe_text = q.question_text[:100].encode('ascii', 'ignore').decode('ascii')
            print(f"  Text: {safe_text}{'...' if len(q.question_text) > 100 else ''}")
            if q.image:
                print(f"  Image: {q.image.name}")
            print(f"  Answer Count: 1")
            safe_answer = answer.answer_text.encode('ascii', 'ignore').decode('ascii')
            print(f"  Single Answer: '{safe_answer}' {correct_marker}")
            print(f"  Topic ID: {q.topic.id if q.topic else 'None'}")
    
    if questions_with_no_answers:
        print("\n" + "=" * 80)
        print(f"[ERROR] Found {len(questions_with_no_answers)} question(s) with NO answers:")
        print("=" * 80)
        for q in questions_with_no_answers:
            print(f"\n  Question ID: {q.id}")
            print(f"  Type: {q.question_type}")
            # Safe text encoding
            safe_text = q.question_text[:100].encode('ascii', 'ignore').decode('ascii')
            print(f"  Text: {safe_text}{'...' if len(q.question_text) > 100 else ''}")
            if q.image:
                print(f"  Image: {q.image.name}")
            print(f"  Answer Count: 0")
            print(f"  Topic ID: {q.topic.id if q.topic else 'None'}")
    
    if not questions_with_single_answer and not questions_with_no_answers:
        print("[OK] All Year 6 Measurement questions have multiple answers!")
    
    print("\n" + "=" * 80)
    print("[INFO] Check complete.")
    print("=" * 80)

if __name__ == "__main__":
    check_single_answer_questions()

