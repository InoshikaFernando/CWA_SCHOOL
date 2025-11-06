#!/usr/bin/env python
"""
Script to add answers to Year 6 perimeter questions.
Usage: python add_year6_perimeter_answers.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Answer

# Question IDs and their corresponding images
# You'll need to calculate the perimeter from each image
QUESTIONS_TO_FIX = {
    101: {'image': 'image3.png', 'answer': None},  # Add answer here
    102: {'image': 'image4.png', 'answer': None},  # Add answer here
    103: {'image': 'image5.png', 'answer': None},  # Add answer here
    104: {'image': 'image6.png', 'answer': None},  # Add answer here
    109: {'image': 'image11.png', 'answer': None},  # Add answer here
    110: {'image': 'image12.png', 'answer': None},  # Add answer here
    111: {'image': 'image13.png', 'answer': None},  # Add answer here
}

def add_answers_interactive():
    """Interactively add answers to perimeter questions"""
    print("=" * 80)
    print("ADDING ANSWERS TO YEAR 6 PERIMETER QUESTIONS")
    print("=" * 80)
    print("\nFor each question, you'll need to calculate the perimeter from the image.")
    print("Enter the answer in the format: 'XX cm' or just 'XX'\n")
    
    for q_id, info in QUESTIONS_TO_FIX.items():
        try:
            question = Question.objects.get(id=q_id)
            print(f"\n{'='*80}")
            print(f"Question ID: {q_id}")
            print(f"Image: {info['image']}")
            print(f"Question: {question.question_text}")
            print(f"Explanation: {question.explanation}")
            print(f"{'='*80}")
            
            # Check if answer already exists
            existing_answers = Answer.objects.filter(question=question)
            if existing_answers.exists():
                print(f"[INFO] This question already has {existing_answers.count()} answer(s):")
                for ans in existing_answers:
                    print(f"  - {ans.answer_text} (correct={ans.is_correct})")
                skip = input("  Skip this question? (yes/no): ").strip().lower()
                if skip in ['yes', 'y']:
                    continue
            
            # Get answer from user
            answer_text = input(f"\nEnter the perimeter answer for {info['image']}: ").strip()
            
            if not answer_text:
                print("  [SKIP] No answer provided, skipping...")
                continue
            
            # Add answer
            answer = Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=True,
                order=0
            )
            
            print(f"  [OK] Added answer: {answer_text}")
            
        except Question.DoesNotExist:
            print(f"  [ERROR] Question {q_id} not found!")
            continue
    
    print("\n" + "=" * 80)
    print("FINISHED")
    print("=" * 80)

def add_answers_batch(answers_dict):
    """Add answers in batch from a dictionary"""
    print("=" * 80)
    print("ADDING ANSWERS IN BATCH MODE")
    print("=" * 80)
    
    added_count = 0
    skipped_count = 0
    
    for q_id, answer_text in answers_dict.items():
        if not answer_text:
            print(f"[SKIP] Question {q_id}: No answer provided")
            skipped_count += 1
            continue
        
        try:
            question = Question.objects.get(id=q_id)
            
            # Check if answer already exists
            existing = Answer.objects.filter(
                question=question,
                answer_text=answer_text
            ).first()
            
            if existing:
                print(f"[INFO] Question {q_id}: Answer '{answer_text}' already exists")
                skipped_count += 1
                continue
            
            # Add answer
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=True,
                order=0
            )
            
            print(f"[OK] Question {q_id}: Added answer '{answer_text}'")
            added_count += 1
            
        except Question.DoesNotExist:
            print(f"[ERROR] Question {q_id} not found!")
            skipped_count += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Added {added_count} answer(s), Skipped {skipped_count}")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add answers to Year 6 perimeter questions')
    parser.add_argument('--batch', action='store_true', help='Use batch mode (requires answers in code)')
    parser.add_argument('--answers', type=str, help='Comma-separated answers for IDs 101,102,103,104,109,110,111')
    
    args = parser.parse_args()
    
    if args.answers:
        # Parse comma-separated answers
        answer_list = [a.strip() for a in args.answers.split(',')]
        if len(answer_list) == 7:
            answers_dict = {
                101: answer_list[0],
                102: answer_list[1],
                103: answer_list[2],
                104: answer_list[3],
                109: answer_list[4],
                110: answer_list[5],
                111: answer_list[6],
            }
            add_answers_batch(answers_dict)
        else:
            print(f"[ERROR] Expected 7 answers, got {len(answer_list)}")
    elif args.batch:
        # Use answers from QUESTIONS_TO_FIX if they're filled in
        answers_dict = {q_id: info['answer'] for q_id, info in QUESTIONS_TO_FIX.items()}
        if any(answers_dict.values()):
            add_answers_batch(answers_dict)
        else:
            print("[ERROR] No answers provided in QUESTIONS_TO_FIX dictionary")
            print("Please fill in the answers or use --answers parameter")
    else:
        # Interactive mode
        add_answers_interactive()

