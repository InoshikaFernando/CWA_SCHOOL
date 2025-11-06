#!/usr/bin/env python
"""
Validation script to check questions and answers in the database.
Checks for:
- Questions without answers
- Multiple choice questions without correct answers
- Questions with only incorrect answers
- Specific validation for Year 6 measurements
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Question, Answer
from django.db.models import Q

def validate_questions(level_number=None, topic_filter=None):
    """Validate questions and answers
    
    Args:
        level_number: Optional level number to filter (e.g., 6 for Year 6)
        topic_filter: Optional topic filter (e.g., 'measurements')
    """
    
    # Build query
    questions_query = Question.objects.all()
    
    if level_number:
        questions_query = questions_query.filter(level__level_number=level_number)
        print(f"[INFO] Validating questions for Year {level_number}")
    else:
        print(f"[INFO] Validating all questions")
    
    if topic_filter:
        if topic_filter.lower() == 'measurements':
            questions_query = questions_query.filter(
                Q(question_text__icontains='measure') |
                Q(question_text__icontains='length') |
                Q(question_text__icontains='width') |
                Q(question_text__icontains='height') |
                Q(question_text__icontains='centimeter') |
                Q(question_text__icontains='meter') |
                Q(question_text__icontains='kilometer') |
                Q(question_text__icontains='liter') |
                Q(question_text__icontains='gram') |
                Q(question_text__icontains='kilogram') |
                Q(question_text__icontains='unit would you use') |
                Q(question_text__icontains='ruler') |
                Q(question_text__icontains='scale')
            ).exclude(
                Q(question_text__icontains='complete the following sequence') |
                Q(question_text__icontains='counting on') |
                Q(question_text__icontains='counting back') |
                Q(question_text__icontains='skip counting') |
                Q(question_text__icontains='tens and ones') |
                Q(question_text__icontains='How many tens')
            )
            print(f"   Filtering for Measurements topic")
    
    print(f"   Total questions to check: {questions_query.count()}\n")
    
    # Track issues
    issues = {
        'no_answers': [],
        'no_correct_answer': [],
        'only_incorrect_answers': [],
        'multiple_choice_no_options': [],
        'short_answer_with_options': []
    }
    
    # Check each question
    for question in questions_query.select_related('level'):
        answers = Answer.objects.filter(question=question)
        answer_count = answers.count()
        correct_answers = answers.filter(is_correct=True)
        correct_count = correct_answers.count()
        
        # Issue 1: No answers at all
        if answer_count == 0:
            issues['no_answers'].append({
                'question_id': question.id,
                'level': question.level.level_number,
                'question_text': question.question_text[:100],
                'question_type': question.question_type
            })
            continue
        
        # Issue 2: Multiple choice without correct answer
        if question.question_type == 'multiple_choice' and correct_count == 0:
            issues['no_correct_answer'].append({
                'question_id': question.id,
                'level': question.level.level_number,
                'question_text': question.question_text[:100],
                'answer_count': answer_count
            })
        
        # Issue 3: Multiple choice with only one answer (should have multiple options)
        if question.question_type == 'multiple_choice' and answer_count < 2:
            issues['multiple_choice_no_options'].append({
                'question_id': question.id,
                'level': question.level.level_number,
                'question_text': question.question_text[:100],
                'answer_count': answer_count
            })
        
        # Issue 4: Short answer with multiple choice answers
        if question.question_type == 'short_answer' and answer_count > 1:
            issues['short_answer_with_options'].append({
                'question_id': question.id,
                'level': question.level.level_number,
                'question_text': question.question_text[:100],
                'answer_count': answer_count
            })
    
    # Print results
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    
    if total_issues == 0:
        print("\n[OK] All questions are valid!")
        return
    
    # Report issues
    if issues['no_answers']:
        print(f"\n[ERROR] Questions with NO ANSWERS ({len(issues['no_answers'])}):")
        print("-" * 80)
        for issue in issues['no_answers']:
            print(f"  ID {issue['question_id']} | Year {issue['level']} | Type: {issue['question_type']}")
            print(f"  Question: {issue['question_text']}...")
            print()
    
    if issues['no_correct_answer']:
        print(f"\n[ERROR] Multiple Choice questions with NO CORRECT ANSWER ({len(issues['no_correct_answer'])}):")
        print("-" * 80)
        for issue in issues['no_correct_answer']:
            print(f"  ID {issue['question_id']} | Year {issue['level']} | {issue['answer_count']} answers (all incorrect)")
            print(f"  Question: {issue['question_text']}...")
            print()
    
    if issues['multiple_choice_no_options']:
        print(f"\n[WARNING] Multiple Choice questions with INSUFFICIENT OPTIONS ({len(issues['multiple_choice_no_options'])}):")
        print("-" * 80)
        for issue in issues['multiple_choice_no_options']:
            print(f"  ID {issue['question_id']} | Year {issue['level']} | Only {issue['answer_count']} answer(s)")
            print(f"  Question: {issue['question_text']}...")
            print()
    
    if issues['short_answer_with_options']:
        print(f"\n[WARNING] Short Answer questions with MULTIPLE ANSWERS ({len(issues['short_answer_with_options'])}):")
        print("-" * 80)
        for issue in issues['short_answer_with_options']:
            print(f"  ID {issue['question_id']} | Year {issue['level']} | {issue['answer_count']} answers")
            print(f"  Question: {issue['question_text']}...")
            print()
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Found {total_issues} issue(s) across {questions_query.count()} question(s)")
    print("=" * 80)
    
    # Return issues for further processing
    return issues

def fix_missing_answers(level_number=None, topic_filter=None, dry_run=True):
    """Attempt to fix common issues (placeholder for future implementation)"""
    print("\n" + "=" * 80)
    print("FIX MODE (Not implemented yet)")
    print("=" * 80)
    print("This would attempt to fix issues, but requires manual review.")
    print("Please review the issues above and fix them manually.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate questions and answers in the database')
    parser.add_argument('--level', type=int, help='Filter by level number (e.g., 6 for Year 6)')
    parser.add_argument('--topic', type=str, help='Filter by topic (e.g., measurements)')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues (not implemented)')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run mode (default: True)')
    
    args = parser.parse_args()
    
    # Validate
    issues = validate_questions(level_number=args.level, topic_filter=args.topic)
    
    # Fix if requested
    if args.fix:
        fix_missing_answers(level_number=args.level, topic_filter=args.topic, dry_run=args.dry_run)

