#!/usr/bin/env python
"""
Script to add answers to questions that are missing answers.
Usage: python add_answers_to_questions.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer

def show_question_details(question_ids):
    """Show details of questions that need answers"""
    questions = Question.objects.filter(id__in=question_ids).select_related('level')
    
    print("=" * 80)
    print("QUESTIONS NEEDING ANSWERS")
    print("=" * 80)
    
    for q in questions:
        print(f"\nQuestion ID: {q.id}")
        print(f"Level: Year {q.level.level_number}")
        print(f"Type: {q.question_type}")
        print(f"Question Text: {q.question_text}")
        if q.image:
            print(f"Image: {q.image.name}")
        else:
            print("Image: None")
        print(f"Explanation: {q.explanation or '(none)'}")
        print("-" * 80)

def add_answer_to_question(question_id, answer_text, is_correct=True, order=0):
    """Add an answer to a question"""
    try:
        question = Question.objects.get(id=question_id)
        
        # Check if answer already exists
        existing = Answer.objects.filter(
            question=question,
            answer_text=answer_text
        ).first()
        
        if existing:
            print(f"  [INFO] Answer already exists: {answer_text}")
            return existing
        
        answer = Answer.objects.create(
            question=question,
            answer_text=answer_text,
            is_correct=is_correct,
            order=order
        )
        
        print(f"  [OK] Added answer: {answer_text} (correct={is_correct})")
        return answer
    except Question.DoesNotExist:
        print(f"  [ERROR] Question {question_id} not found")
        return None

def interactive_add_answers(question_ids):
    """Interactively add answers to questions"""
    questions = Question.objects.filter(id__in=question_ids).select_related('level').order_by('id')
    
    print("\n" + "=" * 80)
    print("INTERACTIVE ANSWER ADDITION")
    print("=" * 80)
    print("\nFor each question, you'll be prompted to add answers.")
    print("For short_answer questions, add the correct answer.")
    print("For multiple_choice questions, add correct and wrong answers.")
    print("Type 'skip' to skip a question, 'done' when finished.\n")
    
    for q in questions:
        print(f"\n{'='*80}")
        print(f"Question ID: {q.id} | Year {q.level.level_number} | Type: {q.question_type}")
        print(f"Question: {q.question_text}")
        if q.image:
            print(f"Image: {q.image.name}")
        print(f"{'='*80}")
        
        if q.question_type == 'short_answer':
            print("\n[Short Answer Question]")
            answer = input("Enter the correct answer (or 'skip'): ").strip()
            if answer.lower() == 'skip':
                print("  [SKIP] Skipping this question")
                continue
            if answer:
                add_answer_to_question(q.id, answer, is_correct=True, order=0)
        
        elif q.question_type == 'multiple_choice':
            print("\n[Multiple Choice Question]")
            print("Enter answers. Type 'done' when finished adding answers.")
            
            order = 0
            correct_added = False
            
            while True:
                answer_text = input(f"Answer {order + 1} (or 'done'): ").strip()
                if answer_text.lower() == 'done':
                    break
                if not answer_text:
                    continue
                
                is_correct_input = input("  Is this correct? (yes/no): ").strip().lower()
                is_correct = is_correct_input in ['yes', 'y', '1', 'true']
                
                if is_correct:
                    correct_added = True
                
                add_answer_to_question(q.id, answer_text, is_correct=is_correct, order=order)
                order += 1
            
            if not correct_added:
                print("  [WARNING] No correct answer was added!")
        
        print(f"  [OK] Finished with question {q.id}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add answers to questions')
    parser.add_argument('--question-ids', type=int, nargs='+', help='Question IDs to add answers to')
    parser.add_argument('--level', type=int, help='Filter by level number')
    parser.add_argument('--topic', type=str, help='Filter by topic (e.g., measurements)')
    parser.add_argument('--show-only', action='store_true', help='Only show question details, do not add answers')
    
    args = parser.parse_args()
    
    # Get question IDs
    if args.question_ids:
        question_ids = args.question_ids
    else:
        # Find questions without answers
        questions_query = Question.objects.filter(answers__isnull=True)
        
        if args.level:
            questions_query = questions_query.filter(level__level_number=args.level)
        
        if args.topic and args.topic.lower() == 'measurements':
            from django.db.models import Q
            questions_query = questions_query.filter(
                Q(question_text__icontains='measure') |
                Q(question_text__icontains='length') |
                Q(question_text__icontains='width') |
                Q(question_text__icontains='height') |
                Q(question_text__icontains='centimeter') |
                Q(question_text__icontains='meter') |
                Q(question_text__icontains='kilometer')
            )
        
        question_ids = list(questions_query.values_list('id', flat=True))
    
    if not question_ids:
        print("[INFO] No questions found that need answers")
        sys.exit(0)
    
    # Show question details
    show_question_details(question_ids)
    
    if not args.show_only:
        print("\n" + "=" * 80)
        proceed = input(f"\nProceed to add answers to {len(question_ids)} question(s)? (yes/no): ").strip().lower()
        if proceed in ['yes', 'y']:
            interactive_add_answers(question_ids)
        else:
            print("[INFO] Cancelled")

