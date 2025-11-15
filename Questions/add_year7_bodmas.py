#!/usr/bin/env python
"""
Add/Update "BODMAS/PEMDAS" questions for Year 7
This script copies Year 6 BODMAS questions to Year 7 (similar to measurements)
"""
import os
import sys
import django
import random

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer

def setup_bodmas_topic():
    """Create BODMAS/PEMDAS topic and associate with Year 7"""
    
    # Get or create the "BODMAS/PEMDAS" topic
    # Handle case where multiple topics with same name exist
    bodmas_topic = Topic.objects.filter(name="BODMAS/PEMDAS").first()
    if not bodmas_topic:
        bodmas_topic = Topic.objects.create(name="BODMAS/PEMDAS")
        print(f"[OK] Created topic: BODMAS/PEMDAS")
    else:
        print(f"[INFO] Topic already exists: BODMAS/PEMDAS")
    
    # Get Year 7 level
    level_7 = Level.objects.filter(level_number=7).first()
    
    if not level_7:
        print("[ERROR] Year 7 level not found!")
        return None
    
    print(f"[INFO] Found Year 7: {level_7}")
    
    # Check if BODMAS/PEMDAS is already associated
    if level_7.topics.filter(name="BODMAS/PEMDAS").exists():
        print("[INFO] Year 7 already has BODMAS/PEMDAS topic associated.")
        print(f"   Current topics for Year 7: {', '.join([t.name for t in level_7.topics.all()])}")
    else:
        # Associate BODMAS/PEMDAS topic with Year 7
        level_7.topics.add(bodmas_topic)
        print(f"[OK] Successfully associated BODMAS/PEMDAS topic with Year 7")
        print(f"   Year 7 now has topics: {', '.join([t.name for t in level_7.topics.all()])}")
    
    return bodmas_topic, level_7

def add_bodmas_questions(bodmas_topic, level_7):
    """Add BODMAS/PEMDAS questions for Year 7 by copying from Year 6"""
    
    # Get Year 6 level and BODMAS questions
    level_6 = Level.objects.filter(level_number=6).first()
    if not level_6:
        print("[ERROR] Year 6 level not found! Cannot copy questions.")
        return
    
    # Get all Year 6 BODMAS questions
    year6_bodmas_questions = Question.objects.filter(
        level=level_6,
        topic=bodmas_topic
    )
    
    if not year6_bodmas_questions.exists():
        print("[WARNING] No Year 6 BODMAS questions found. Please run add_year6_bodmas.py first.")
        return
    
    print(f"\n[INFO] Found {year6_bodmas_questions.count()} Year 6 BODMAS questions to copy to Year 7...\n")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for year6_question in year6_bodmas_questions:
        # Check if question already exists in Year 7
        existing = Question.objects.filter(
            level=level_7,
            topic=bodmas_topic,
            question_text=year6_question.question_text
        ).first()
        
        if existing:
            # Question already exists, update it
            question = existing
            question.explanation = year6_question.explanation
            question.save()
            
            # Delete old answers to replace with correct ones
            Answer.objects.filter(question=question).delete()
            
            # Copy answers from Year 6 question
            year6_answers = Answer.objects.filter(question=year6_question).order_by('order')
            for year6_answer in year6_answers:
                Answer.objects.create(
                    question=question,
                    answer_text=year6_answer.answer_text,
                    is_correct=year6_answer.is_correct,
                    order=year6_answer.order
                )
            
            safe_text = year6_question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [UPDATE] Updated: {safe_text}...")
            updated_count += 1
        else:
            # Create new question for Year 7
            question = Question.objects.create(
                level=level_7,
                topic=bodmas_topic,
                question_text=year6_question.question_text,
                question_type=year6_question.question_type,
                difficulty=year6_question.difficulty,
                points=year6_question.points,
                explanation=year6_question.explanation,
                image=year6_question.image  # Copy image reference if exists
            )
            
            # Copy answers from Year 6 question
            year6_answers = Answer.objects.filter(question=year6_question).order_by('order')
            for year6_answer in year6_answers:
                Answer.objects.create(
                    question=question,
                    answer_text=year6_answer.answer_text,
                    is_correct=year6_answer.is_correct,
                    order=year6_answer.order
                )
            
            safe_text = year6_question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [OK] Created: {safe_text}...")
            created_count += 1
    
    print(f"\n[SUMMARY]")
    print(f"   [OK] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"   [SKIP] Skipped: {skipped_count} questions")
    print(f"\n[OK] All BODMAS/PEMDAS questions are associated with Year 7")

if __name__ == "__main__":
    print("[INFO] Setting up BODMAS/PEMDAS topic for Year 7...\n")
    result = setup_bodmas_topic()
    
    if result:
        bodmas_topic, level_7 = result
        print("\n" + "="*60)
        add_bodmas_questions(bodmas_topic, level_7)
        print("\n[OK] Done!")

