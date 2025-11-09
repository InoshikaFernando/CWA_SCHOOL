#!/usr/bin/env python
"""
Check for duplicate questions in the database
Finds questions with the same question_text and optionally the same image
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Level, Topic
from collections import defaultdict

def check_duplicate_questions(level_number=None, topic_name=None, check_image=True):
    """
    Check for duplicate questions
    
    Args:
        level_number: Optional - filter by specific level (e.g., 6 for Year 6)
        topic_name: Optional - filter by specific topic (e.g., "Measurements")
        check_image: If True, also check if images match
    """
    
    print("[INFO] Checking for duplicate questions...\n")
    
    # Build query
    questions_query = Question.objects.all()
    
    if level_number:
        questions_query = questions_query.filter(level__level_number=level_number)
        print(f"[INFO] Filtering by Level: Year {level_number}")
    
    if topic_name:
        questions_query = questions_query.filter(topic__name=topic_name)
        print(f"[INFO] Filtering by Topic: {topic_name}")
    
    print()
    
    all_questions = questions_query.select_related('level', 'topic').order_by('id')
    
    if not all_questions.exists():
        print("[INFO] No questions found matching the criteria.")
        return
    
    print(f"[INFO] Checking {all_questions.count()} question(s)...\n")
    
    # Group questions by question_text
    questions_by_text = defaultdict(list)
    
    for question in all_questions:
        questions_by_text[question.question_text].append(question)
    
    # Find duplicates (same question text)
    text_duplicates = {text: questions for text, questions in questions_by_text.items() if len(questions) > 1}
    
    if not text_duplicates:
        print("[OK] No duplicate questions found (by question text)!")
        return
    
    print(f"[WARNING] Found {len(text_duplicates)} question text(s) with duplicates:\n")
    print("=" * 80)
    
    total_duplicate_groups = 0
    total_duplicate_questions = 0
    
    for question_text, questions in text_duplicates.items():
        total_duplicate_groups += 1
        total_duplicate_questions += len(questions) - 1  # -1 because we keep one
        
        print(f"\nDuplicate Group {total_duplicate_groups}:")
        print(f"  Question Text: {question_text[:100]}{'...' if len(question_text) > 100 else ''}")
        print(f"  Number of duplicates: {len(questions)}")
        print()
        
        # If checking images, group by image as well
        if check_image:
            questions_by_image = defaultdict(list)
            for q in questions:
                image_name = q.image.name if q.image else "NO_IMAGE"
                questions_by_image[image_name].append(q)
            
            # Show duplicates with same image
            image_duplicates = {img: qs for img, qs in questions_by_image.items() if len(qs) > 1}
            
            if image_duplicates:
                print("  Duplicates with SAME IMAGE:")
                for image_name, q_list in image_duplicates.items():
                    print(f"    Image: {image_name if image_name != 'NO_IMAGE' else '(no image)'}")
                    for q in q_list:
                        print(f"      - Question ID: {q.id}, Level: {q.level}, Topic: {q.topic.name if q.topic else 'None'}")
                print()
            
            # Show questions with different images
            single_image_questions = {img: qs for img, qs in questions_by_image.items() if len(qs) == 1}
            if single_image_questions and len(image_duplicates) < len(questions_by_image):
                print("  Questions with DIFFERENT IMAGES (same text, different image):")
                for image_name, q_list in single_image_questions.items():
                    for q in q_list:
                        print(f"      - Question ID: {q.id}, Image: {image_name if image_name != 'NO_IMAGE' else '(no image)'}, Level: {q.level}, Topic: {q.topic.name if q.topic else 'None'}")
                print()
        else:
            # Just show all duplicates
            for q in questions:
                image_info = q.image.name if q.image else "(no image)"
                print(f"  - Question ID: {q.id}, Level: {q.level}, Topic: {q.topic.name if q.topic else 'None'}, Image: {image_info}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total duplicate groups: {total_duplicate_groups}")
    print(f"  Total duplicate questions (can be removed): {total_duplicate_questions}")
    print(f"  Total questions in duplicate groups: {sum(len(qs) for qs in text_duplicates.values())}")
    print()
    print("[INFO] Check complete.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check for duplicate questions')
    parser.add_argument('--level', type=int, help='Filter by level number (e.g., 6 for Year 6)')
    parser.add_argument('--topic', type=str, help='Filter by topic name (e.g., "Measurements")')
    parser.add_argument('--no-image-check', action='store_true', 
                       help='Do not check if images match (default: check images)')
    
    args = parser.parse_args()
    
    check_duplicate_questions(
        level_number=args.level,
        topic_name=args.topic,
        check_image=not args.no_image_check
    )

