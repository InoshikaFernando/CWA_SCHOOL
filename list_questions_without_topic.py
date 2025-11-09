#!/usr/bin/env python
"""
List all questions without a topic assigned
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Level, Topic

def list_questions_without_topic():
    """List all questions that don't have a topic assigned"""
    
    print("=" * 80)
    print("QUESTIONS WITHOUT TOPIC")
    print("=" * 80)
    print()
    
    # Get all questions without topic
    questions_without_topic = Question.objects.filter(
        topic__isnull=True
    ).select_related('level').order_by('level__level_number', 'id')
    
    total = questions_without_topic.count()
    
    if total == 0:
        print("[OK] All questions have a topic assigned!")
        return
    
    print(f"[INFO] Found {total} question(s) without topic:\n")
    print("=" * 80)
    print(f"{'ID':<6} {'Level':<12} {'Type':<15} {'Question Text'}")
    print("=" * 80)
    
    # Group by level for better readability
    questions_by_level = {}
    for question in questions_without_topic:
        level_num = question.level.level_number if question.level else 0
        level_name = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
        
        if level_name not in questions_by_level:
            questions_by_level[level_name] = []
        questions_by_level[level_name].append(question)
    
    # Print grouped by level
    for level_name in sorted(questions_by_level.keys(), key=lambda x: (
        int(x.split()[-1]) if x.split()[-1].isdigit() else 999
    )):
        questions = questions_by_level[level_name]
        print(f"\n{level_name} ({len(questions)} questions):")
        print("-" * 80)
        
        for question in questions:
            safe_text = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            if len(question.question_text) > 60:
                safe_text += "..."
            
            print(f"  ID {question.id:<4} [{question.question_type:<15}] {safe_text}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total questions without topic: {total}")
    print("\nBreakdown by level:")
    for level_name in sorted(questions_by_level.keys(), key=lambda x: (
        int(x.split()[-1]) if x.split()[-1].isdigit() else 999
    )):
        count = len(questions_by_level[level_name])
        print(f"  {level_name}: {count} questions")
    
    print("\n[INFO] These questions need to have a topic assigned.")
    print("       You can use backfill_question_topics.py to automatically assign topics.")

if __name__ == "__main__":
    list_questions_without_topic()

