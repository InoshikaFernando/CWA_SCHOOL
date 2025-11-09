#!/usr/bin/env python
"""
Database validation script for questions
Validates all questions in the actual database meet the following requirements:
1. All questions should contain multiple answers
2. All questions should belong to a level
3. All questions should belong to a topic
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer, Level, Topic
from django.db.models import Count

def validate_database_questions():
    """
    Validate all questions in the database meet requirements
    """
    
    print("=" * 80)
    print("DATABASE QUESTION VALIDATION")
    print("=" * 80)
    print()
    
    # Get all questions
    all_questions = Question.objects.all().select_related('level', 'topic').annotate(
        answer_count=Count('answers')
    ).order_by('id')
    
    total_questions = all_questions.count()
    print(f"[INFO] Total questions in database: {total_questions}\n")
    
    if total_questions == 0:
        print("[INFO] No questions found in database.")
        return
    
    # Track issues
    issues = {
        'no_level': [],
        'no_topic': [],
        'no_answers': [],
        'single_answer': []
    }
    
    # Validate each question
    for question in all_questions:
        question_id = question.id
        answer_count = question.answer_count
        
        # Check for level
        if not question.level:
            issues['no_level'].append({
                'id': question_id,
                'text': question.question_text[:80],
                'type': question.question_type
            })
        
        # Check for topic
        if not question.topic:
            issues['no_topic'].append({
                'id': question_id,
                'text': question.question_text[:80],
                'type': question.question_type,
                'level': question.level.level_number if question.level else None
            })
        
        # Check for answers
        if answer_count == 0:
            issues['no_answers'].append({
                'id': question_id,
                'text': question.question_text[:80],
                'type': question.question_type,
                'level': question.level.level_number if question.level else None,
                'topic': question.topic.name if question.topic else None
            })
        elif answer_count == 1:
            issues['single_answer'].append({
                'id': question_id,
                'text': question.question_text[:80],
                'type': question.question_type,
                'level': question.level.level_number if question.level else None,
                'topic': question.topic.name if question.topic else None,
                'answer': question.answers.first().answer_text[:50] if question.answers.exists() else None
            })
    
    # Report results
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()
    
    # Questions without level
    if issues['no_level']:
        print(f"[ERROR] QUESTIONS WITHOUT LEVEL: {len(issues['no_level'])}")
        print("-" * 80)
        for issue in issues['no_level']:
            safe_text = issue['text'].encode('ascii', 'ignore').decode('ascii')
            print(f"  ID {issue['id']}: [{issue['type']}] {safe_text}...")
        print()
    else:
        print("[OK] All questions have a level assigned")
        print()
    
    # Questions without topic
    if issues['no_topic']:
        print(f"[ERROR] QUESTIONS WITHOUT TOPIC: {len(issues['no_topic'])}")
        print("-" * 80)
        for issue in issues['no_topic']:
            safe_text = issue['text'].encode('ascii', 'ignore').decode('ascii')
            level_info = f"Year {issue['level']}" if issue['level'] else "No level"
            print(f"  ID {issue['id']}: [{issue['type']}] {safe_text}... | Level: {level_info}")
        print()
    else:
        print("[OK] All questions have a topic assigned")
        print()
    
    # Questions with no answers
    if issues['no_answers']:
        print(f"[ERROR] QUESTIONS WITH NO ANSWERS: {len(issues['no_answers'])}")
        print("-" * 80)
        for issue in issues['no_answers']:
            safe_text = issue['text'].encode('ascii', 'ignore').decode('ascii')
            level_info = f"Year {issue['level']}" if issue['level'] else "No level"
            topic_info = issue['topic'] if issue['topic'] else "No topic"
            print(f"  ID {issue['id']}: [{issue['type']}] {safe_text}... | Level: {level_info} | Topic: {topic_info}")
        print()
    else:
        print("[OK] All questions have at least one answer")
        print()
    
    # Questions with single answer
    if issues['single_answer']:
        print(f"[ERROR] QUESTIONS WITH SINGLE ANSWER: {len(issues['single_answer'])}")
        print("-" * 80)
        for issue in issues['single_answer']:
            safe_text = issue['text'].encode('ascii', 'ignore').decode('ascii')
            safe_answer = issue['answer'].encode('ascii', 'ignore').decode('ascii') if issue['answer'] else "N/A"
            level_info = f"Year {issue['level']}" if issue['level'] else "No level"
            topic_info = issue['topic'] if issue['topic'] else "No topic"
            print(f"  ID {issue['id']}: [{issue['type']}] {safe_text}... | Level: {level_info} | Topic: {topic_info}")
            print(f"    Answer: '{safe_answer}'")
        print()
    else:
        print("[OK] All questions have multiple answers")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_issues = (
        len(issues['no_level']) +
        len(issues['no_topic']) +
        len(issues['no_answers']) +
        len(issues['single_answer'])
    )
    
    print(f"Total questions: {total_questions}")
    print(f"Questions with issues: {total_issues}")
    print(f"Valid questions: {total_questions - total_issues}")
    print()
    
    if total_issues == 0:
        print("[SUCCESS] ALL QUESTIONS ARE VALID!")
        return True
    else:
        print("[WARNING] SOME QUESTIONS NEED ATTENTION")
        print()
        print("Issue breakdown:")
        print(f"  - Questions without level: {len(issues['no_level'])}")
        print(f"  - Questions without topic: {len(issues['no_topic'])}")
        print(f"  - Questions with no answers: {len(issues['no_answers'])}")
        print(f"  - Questions with single answer: {len(issues['single_answer'])}")
        return False

if __name__ == "__main__":
    success = validate_database_questions()
    sys.exit(0 if success else 1)

