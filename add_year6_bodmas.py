#!/usr/bin/env python
"""
Add "BODMAS/PEMDAS" topic for Year 6 and all associated questions
This script creates the topic, associates it with Year 6, and adds BODMAS questions
"""
import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question, Answer

def setup_bodmas_topic():
    """Create BODMAS/PEMDAS topic and associate with Year 6"""
    
    # Get or create the "BODMAS/PEMDAS" topic
    # Handle case where multiple topics with same name exist
    bodmas_topic = Topic.objects.filter(name="BODMAS/PEMDAS").first()
    if not bodmas_topic:
        bodmas_topic = Topic.objects.create(name="BODMAS/PEMDAS")
        print(f"[OK] Created topic: BODMAS/PEMDAS")
    else:
        print(f"[INFO] Topic already exists: BODMAS/PEMDAS")
    
    # Get Year 6 level
    level_6 = Level.objects.filter(level_number=6).first()
    
    if not level_6:
        print("[ERROR] Year 6 level not found!")
        return None
    
    print(f"[INFO] Found Year 6: {level_6}")
    
    # Check if BODMAS/PEMDAS is already associated
    if level_6.topics.filter(name="BODMAS/PEMDAS").exists():
        print("[INFO] Year 6 already has BODMAS/PEMDAS topic associated.")
        print(f"   Current topics for Year 6: {', '.join([t.name for t in level_6.topics.all()])}")
    else:
        # Associate BODMAS/PEMDAS topic with Year 6
        level_6.topics.add(bodmas_topic)
        print(f"[OK] Successfully associated BODMAS/PEMDAS topic with Year 6")
        print(f"   Year 6 now has topics: {', '.join([t.name for t in level_6.topics.all()])}")
    
    return bodmas_topic, level_6

def add_bodmas_questions(bodmas_topic, level_6):
    """Add BODMAS/PEMDAS questions for Year 6"""
    
    # Define questions - BODMAS/PEMDAS evaluation questions
    questions_data = [
        # Word problems - finding original number
        {
            "question_text": "I add 2, then multiply it by 5. The result is 40. What was the number I thought of?",
            "correct_answer": "6",
            "wrong_answers": ["8", "10", "4"],
            "explanation": "Work backwards: 40 ÷ 5 = 8, then 8 - 2 = 6. So the original number was 6."
        },
        {
            "question_text": "I multiply it by 7, then I subtract 12. The result is 9. What was the number I thought of?",
            "correct_answer": "3",
            "wrong_answers": ["1", "5", "2"],
            "explanation": "Work backwards: 9 + 12 = 21, then 21 ÷ 7 = 3. So the original number was 3."
        },
        {
            "question_text": "I add 11, then multiply it by 7. The result is 63. What was the number I thought of?",
            "correct_answer": "-2",
            "wrong_answers": ["2", "0", "-4"],
            "explanation": "Work backwards: 63 ÷ 7 = 9, then 9 - 11 = -2. So the original number was -2."
        },
        {
            "question_text": "I add 7, then double it. The result is 20. What was the number I thought of?",
            "correct_answer": "3",
            "wrong_answers": ["5", "1", "7"],
            "explanation": "Work backwards: 20 ÷ 2 = 10, then 10 - 7 = 3. So the original number was 3."
        },
        {
            "question_text": "I add 20, double it and subtract 25. The result is 75. What was the number I thought of?",
            "correct_answer": "30",
            "wrong_answers": ["25", "35", "20"],
            "explanation": "Work backwards: 75 + 25 = 100, then 100 ÷ 2 = 50, then 50 - 20 = 30. So the original number was 30."
        },
        # More complex word problems
        {
            "question_text": "I think of a number. I multiply it by 4 and add 9. My answer is 7 times bigger than the number I started with. What number am I thinking of?",
            "correct_answer": "3",
            "wrong_answers": ["2", "4", "5"],
            "explanation": "Let the number be x. Then 4x + 9 = 7x. Solving: 9 = 7x - 4x, so 9 = 3x, therefore x = 3."
        },
        {
            "question_text": "I think of a number. If I multiply the number by 6 and subtract 4, I get the same answer as multiplying it by 3 and adding 14. What number am I thinking of?",
            "correct_answer": "6",
            "wrong_answers": ["4", "8", "5"],
            "explanation": "Let the number be x. Then 6x - 4 = 3x + 14. Solving: 6x - 3x = 14 + 4, so 3x = 18, therefore x = 6."
        },
        {
            "question_text": "Evaluate: 4² + 3³",
            "correct_answer": "43",
            "wrong_answers": ["25", "49", "35"],
            "explanation": "4² = 16 and 3³ = 27. So 16 + 27 = 43"
        },
        {
            "question_text": "Calculate: 456 ÷ 6",
            "correct_answer": "76",
            "wrong_answers": ["75", "77", "74"],
            "explanation": "Dividing: 456 ÷ 6 = 76"
        },
        {
            "question_text": "Evaluate: √100 + 2²",
            "correct_answer": "14",
            "wrong_answers": ["12", "16", "10"],
            "explanation": "√100 = 10 and 2² = 4. So 10 + 4 = 14"
        },
        {
            "question_text": "Write down what BIDMAS/BODMAS stands for.",
            "correct_answer": "Brackets, Indices/Orders, Division, Multiplication, Addition, Subtraction",
            "wrong_answers": [
                "Brackets, Division, Multiplication, Addition, Subtraction",
                "Brackets, Orders, Division, Multiplication, Addition, Subtraction",
                "Brackets, Indices, Division, Multiplication, Addition, Subtraction"
            ],
            "explanation": "BIDMAS/BODMAS stands for: Brackets, Indices/Orders, Division, Multiplication, Addition, Subtraction. This is the order of operations in mathematics."
        },
        {
            "question_text": "Calculate: 9 + 2 × 5",
            "correct_answer": "19",
            "wrong_answers": ["55", "35", "25"],
            "explanation": "Using BODMAS: Multiplication comes before addition. 2 × 5 = 10, then 9 + 10 = 19."
        },
        {
            "question_text": "Calculate: 12 ÷ √16 + 15",
            "correct_answer": "18",
            "wrong_answers": ["16", "20", "14"],
            "explanation": "Using BODMAS: Square root comes first. √16 = 4, then 12 ÷ 4 = 3, then 3 + 15 = 18."
        },
        # Additional BODMAS questions
        {
            "question_text": "Using the digits 4, 6 and 8 exactly once, as well as any operations, create a calculation to which the answer is 12.",
            "correct_answer": "6 × 8 ÷ 4 = 12",
            "wrong_answers": ["8 + 4 = 12", "48 ÷ 4 = 12", "6 + 6 = 12"],
            "explanation": "One solution is 6 × 8 ÷ 4 = 48 ÷ 4 = 12. This uses all three digits (4, 6, 8) exactly once."
        },
        {
            "question_text": "I think of a number. I add 48 and then divide by 3. Finally, I square root my answer and the result is 9. What number am I thinking of?",
            "correct_answer": "195",
            "wrong_answers": ["189", "171", "207"],
            "explanation": "Work backwards: If √(result) = 9, then result = 9² = 81. If (number + 48) ÷ 3 = 81, then number + 48 = 81 × 3 = 243. So number = 243 - 48 = 195."
        },
        {
            "question_text": "I think of a number. If I multiply the number by 7 and subtract 10, I get the same answer as if I multiply the number by 3 and subtract 2. What number am I thinking of?",
            "correct_answer": "2",
            "wrong_answers": ["3", "4", "5"],
            "explanation": "Let the number be x. Then 7x - 10 = 3x - 2. Solving: 7x - 3x = -2 + 10, so 4x = 8, therefore x = 2."
        },
        {
            "question_text": "I think of a number. If I multiply the number by 4 and subtract 2, I get the same answer as multiplying the number by 2 and adding 8. What number am I thinking of?",
            "correct_answer": "5",
            "wrong_answers": ["4", "6", "3"],
            "explanation": "Let the number be x. Then 4x - 2 = 2x + 8. Solving: 4x - 2x = 8 + 2, so 2x = 10, therefore x = 5."
        },
    ]
    
    print(f"\n[INFO] Adding {len(questions_data)} BODMAS/PEMDAS questions for Year 6...\n")
    
    created_count = 0
    updated_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_6,
            question_text=q_data["question_text"]
        ).first()
        
        if existing:
            # Update existing question
            question = existing
            question.explanation = q_data.get("explanation", "")
            # Ensure topic is set
            if not question.topic:
                question.topic = bodmas_topic
            question.save()
            
            # Delete old answers to replace with correct ones
            Answer.objects.filter(question=question).delete()
            
            print(f"  [UPDATE] Question {i} already exists, updating answers...")
            updated_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_6,
                topic=bodmas_topic,  # Set topic directly on question
                question_text=q_data["question_text"],
                question_type='multiple_choice',
                difficulty=1,
                points=1,
                explanation=q_data.get("explanation", "")
            )
            # Safe print that handles Unicode
            safe_text = q_data['question_text'][:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [OK] Created Question {i}: {safe_text}...")
            created_count += 1
        
        # Ensure question has topic set and level has topic associated
        if not question.topic:
            question.topic = bodmas_topic
            question.save()
        question.level.topics.add(bodmas_topic)
        
        # Create answers - mix correct and wrong answers
        all_answers = [q_data["correct_answer"]] + q_data["wrong_answers"]
        # Shuffle order for variety
        random.shuffle(all_answers)
        
        order = 0
        for answer_text in all_answers:
            is_correct = (answer_text == q_data["correct_answer"])
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
                order=order
            )
            order += 1
    
    print(f"\n[SUMMARY]")
    print(f"   [OK] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"\n[OK] All questions are associated with BODMAS/PEMDAS topic for Year 6")

if __name__ == "__main__":
    print("[INFO] Setting up BODMAS/PEMDAS topic for Year 6...\n")
    result = setup_bodmas_topic()
    
    if result:
        bodmas_topic, level_6 = result
        print("\n" + "="*60)
        add_bodmas_questions(bodmas_topic, level_6)
        print("\n[OK] Done!")

