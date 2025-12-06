#!/usr/bin/env python
"""
Common utilities for adding/updating questions across all year/topic scripts.
This module provides reusable functions for:
- Finding existing questions (duplicate detection)
- Creating/updating questions
- Creating/updating answers
"""
import os
import random
from maths.models import Question, Answer


def find_existing_question(level, topic, question_text, image_path=None, correct_answer=None, wrong_answers=None):
    """
    Find an existing question that matches the given criteria.
    
    For questions with images: Must match BOTH question_text AND image_path
    For questions without images: Matches by question_text only (if unique)
    
    Args:
        level: Level object
        topic: Topic object
        question_text: Question text to match
        image_path: Optional image path (if provided, must match)
        correct_answer: Optional correct answer text (for stricter matching)
        wrong_answers: Optional list of wrong answers (for stricter matching)
    
    Returns:
        Question object if found, None otherwise
    """
    # Base query: match by level, topic, and question_text
    query = Question.objects.filter(
        level=level,
        topic=topic,
        question_text=question_text
    )
    
    if image_path:
        # Must match both question_text AND image
        image_name = os.path.basename(image_path)
        image_name_without_ext = os.path.splitext(image_name)[0]
        
        # Try to find by exact image path first
        existing = query.filter(image=image_path).first()
        if not existing:
            # Fallback: match by image filename (handles Django filename suffixes)
            for q in query:
                if q.image:
                    eq_image_name = q.image.name if q.image.name else ""
                    eq_image_basename = os.path.basename(eq_image_name)
                    eq_image_name_without_ext = os.path.splitext(eq_image_basename)[0]
                    
                    # Remove Django suffix if present (e.g., image5_abc123 -> image5)
                    if '_' in eq_image_name_without_ext:
                        eq_image_base = eq_image_name_without_ext.split('_')[0]
                    else:
                        eq_image_base = eq_image_name_without_ext
                    
                    # Match if the base name (without extension and Django suffix) matches
                    if image_name_without_ext == eq_image_base or image_name in q.image.name or q.image.name.endswith(image_name):
                        existing = q
                        break
        
        # If we have additional criteria (correct_answer, wrong_answers), verify them
        if existing and (correct_answer is not None or wrong_answers is not None):
            if not verify_answer_match(existing, correct_answer, wrong_answers):
                return None
        
        return existing
    else:
        # No image: match by question_text only (but only if no image questions exist with same text)
        # Only match if the existing question also has no image
        existing = query.filter(image__isnull=True).first()
        if not existing and query.count() == 1:
            # Only one question with this text exists, use it
            existing = query.first()
        
        # If we have additional criteria, verify them
        if existing and (correct_answer is not None or wrong_answers is not None):
            if not verify_answer_match(existing, correct_answer, wrong_answers):
                return None
        
        return existing


def verify_answer_match(question, correct_answer=None, wrong_answers=None):
    """
    Verify that a question's answers match the expected correct_answer and wrong_answers.
    
    Args:
        question: Question object
        correct_answer: Expected correct answer text (optional)
        wrong_answers: Expected list of wrong answers (optional)
    
    Returns:
        True if answers match, False otherwise
    """
    existing_answers = Answer.objects.filter(question=question)
    existing_correct = existing_answers.filter(is_correct=True).first()
    
    # Check correct answer if provided
    if correct_answer is not None:
        if not existing_correct or existing_correct.answer_text != correct_answer:
            return False
    
    # Check wrong answers if provided
    if wrong_answers is not None:
        existing_wrong = list(existing_answers.filter(is_correct=False).values_list('answer_text', flat=True))
        if len(existing_wrong) != len(wrong_answers):
            return False
        if set(existing_wrong) != set(wrong_answers):
            return False
    
    return True


def create_answers_for_question(question, question_type, correct_answer, wrong_answers=None):
    """
    Create answers for a question. Deletes existing answers first.
    
    Args:
        question: Question object
        question_type: 'multiple_choice', 'true_false', or 'short_answer'
        correct_answer: Correct answer text
        wrong_answers: List of wrong answers (for multiple_choice/true_false)
    
    Returns:
        Number of answers created
    """
    # Delete existing answers
    Answer.objects.filter(question=question).delete()
    
    if question_type == "multiple_choice" or question_type == "true_false":
        if not correct_answer:
            return 0
        
        wrong_answers = wrong_answers or []
        # Mix correct and wrong answers
        all_answers = [correct_answer] + wrong_answers
        random.shuffle(all_answers)
        
        order = 0
        for answer_text in all_answers:
            is_correct = (answer_text == correct_answer)
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
                order=order
            )
            order += 1
        
        return len(all_answers)
    
    elif question_type == "short_answer":
        if correct_answer:
            Answer.objects.create(
                question=question,
                answer_text=correct_answer,
                is_correct=True,
                order=0
            )
            return 1
    
    return 0


def add_or_update_question(level, topic, question_data, verbose=True):
    """
    Add a new question or update an existing one.
    
    Args:
        level: Level object
        topic: Topic object
        question_data: Dictionary with question data:
            - question_text (required)
            - question_type (required): 'multiple_choice', 'true_false', or 'short_answer'
            - correct_answer (optional)
            - wrong_answers (optional, list)
            - explanation (optional)
            - image_path (optional)
        verbose: If True, print status messages
    
    Returns:
        Tuple: (question, created, updated, skipped)
            question: Question object
            created: True if question was created
            updated: True if question was updated
            skipped: True if question was skipped
    """
    question_text = question_data.get("question_text", "").strip()
    if not question_text:
        if verbose:
            print("[SKIP] Empty question text, skipping...")
        return None, False, False, True
    
    question_type = question_data.get("question_type", "multiple_choice")
    correct_answer = question_data.get("correct_answer", "").strip() if question_data.get("correct_answer") else None
    wrong_answers = question_data.get("wrong_answers", [])
    explanation = question_data.get("explanation", "")
    image_path = question_data.get("image_path", "")
    
    # Find existing question
    existing = find_existing_question(
        level=level,
        topic=topic,
        question_text=question_text,
        image_path=image_path if image_path else None,
        correct_answer=correct_answer if question_type in ['multiple_choice', 'true_false'] else None,
        wrong_answers=wrong_answers if question_type in ['multiple_choice', 'true_false'] else None
    )
    
    question_updated = False
    created = False
    updated = False
    skipped = False
    
    if existing:
        question = existing
        question_updated = False
        
        # Update explanation if changed
        if question.explanation != explanation:
            question.explanation = explanation
            question_updated = True
        
        # Ensure topic is set
        if not question.topic:
            question.topic = topic
            question_updated = True
        
        if question_updated:
            question.save()
        
        # Check if answers need updating
        existing_answers = Answer.objects.filter(question=question)
        existing_correct = existing_answers.filter(is_correct=True).first()
        
        # For multiple choice/true false: check if answers match
        if question_type in ["multiple_choice", "true_false"]:
            if correct_answer:
                if not existing_correct or existing_correct.answer_text != correct_answer:
                    # Answers need updating
                    question_updated = True
                else:
                    # Check wrong answers count
                    existing_wrong = existing_answers.filter(is_correct=False)
                    existing_wrong_texts = set(a.answer_text for a in existing_wrong)
                    expected_wrong_texts = set(wrong_answers)
                    
                    if existing_wrong_texts != expected_wrong_texts:
                        # Wrong answers changed, update all
                        question_updated = True
        
        # For short answer: check if correct answer exists and matches
        elif question_type == "short_answer":
            if correct_answer:
                # Only update if answer is provided and different
                if not existing_correct or existing_correct.answer_text != correct_answer:
                    question_updated = True
            else:
                # No answer provided in data, skip updating answers if they already exist
                if existing_answers.exists():
                    if verbose:
                        print(f"  [SKIP] Already has answers, skipping answer update (no answer in data)")
                    skipped = True
                    return question, False, False, True
        
        if question_updated:
            if verbose:
                print(f"  [UPDATE] Updating...")
            updated = True
        else:
            # Check if answers exist - if not, we need to create them
            if not existing_answers.exists():
                if correct_answer or (question_type in ['multiple_choice', 'true_false'] and correct_answer):
                    question_updated = True
                    if verbose:
                        print(f"  [UPDATE] Missing answers, will add them...")
                    updated = True
                else:
                    if verbose:
                        print(f"  [SKIP] No changes needed and no answer provided")
                    skipped = True
                    return question, False, False, True
            else:
                if verbose:
                    print(f"  [SKIP] No changes needed")
                skipped = True
                return question, False, False, True
    else:
        # Create new question
        question = Question.objects.create(
            level=level,
            topic=topic,
            question_text=question_text,
            question_type=question_type,
            difficulty=1,
            points=1,
            explanation=explanation
        )
        if verbose:
            print(f"  [CREATE] Created new question")
        created = True
        question_updated = True
    
    # Set image path if provided
    if image_path:
        # Just set the image path directly without copying the file
        question.image.name = image_path
        question.save()
        if verbose:
            print(f"      [IMAGE] Set image path: {image_path}")
    
    # Ensure question has topic set and level has topic associated
    if not question.topic:
        question.topic = topic
        question.save()
    level.topics.add(topic)
    
    # Create/update answers if question was created or updated
    if question_updated:
        answer_count = create_answers_for_question(
            question=question,
            question_type=question_type,
            correct_answer=correct_answer or "",
            wrong_answers=wrong_answers
        )
        if verbose and answer_count > 0:
            if question_type == "short_answer":
                print(f"      [ANSWERS] Created answer: {correct_answer}")
            else:
                print(f"      [ANSWERS] Created {answer_count} answer(s)")
        elif verbose and not correct_answer and question_type == "short_answer":
            print(f"      [WARNING] No answer provided for short_answer question")
    
    return question, created, updated, skipped


def process_questions(level, topic, questions_data, verbose=True):
    """
    Process a list of questions, adding or updating them as needed.
    
    Args:
        level: Level object
        topic: Topic object
        questions_data: List of question data dictionaries
        verbose: If True, print status messages
    
    Returns:
        Dictionary with counts: {'created': int, 'updated': int, 'skipped': int}
    """
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    if verbose:
        print(f"\n[INFO] Processing {len(questions_data)} questions...\n")
    
    for i, q_data in enumerate(questions_data, 1):
        if verbose:
            print(f"Question {i}: {q_data.get('question_text', '')[:60]}...")
        
        question, created, updated, skipped = add_or_update_question(
            level=level,
            topic=topic,
            question_data=q_data,
            verbose=verbose
        )
        
        if created:
            created_count += 1
        elif updated:
            updated_count += 1
        elif skipped:
            skipped_count += 1
    
    if verbose:
        print(f"\n[SUMMARY]")
        print(f"   [CREATE] Created: {created_count} questions")
        print(f"   [UPDATE] Updated: {updated_count} questions")
        print(f"   [SKIP] Skipped: {skipped_count} questions")
    
    return {
        'created': created_count,
        'updated': updated_count,
        'skipped': skipped_count
    }

