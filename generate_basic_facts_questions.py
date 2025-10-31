#!/usr/bin/env python
"""
Script to generate 10 questions for each Basic Facts level based on their logic.
"""
import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Question, Answer

def generate_addition_questions(level_num, description, level_obj, num_questions=10):
    """Generate questions for Addition levels"""
    questions = []
    
    if level_num == 100:  # Adding two single digits where values are less than 6
        for _ in range(num_questions):
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 101:  # Adding any 2 single digits
        for _ in range(num_questions):
            a = random.randint(0, 9)
            b = random.randint(0, 9)
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 102:  # Adding double digits where you don't have to carry over
        for _ in range(num_questions):
            # First digit sum < 10, second digit sum < 10
            a1 = random.randint(1, 4)
            a2 = random.randint(0, 4)
            b1 = random.randint(1, 4)
            b2 = random.randint(0, 9 - a2)
            a = a1 * 10 + a2
            b = b1 * 10 + b2
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 103:  # Adding double digits where you have to carry
        for _ in range(num_questions):
            # Force carry in units place
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            # Ensure units place sum >= 10
            a_units = a % 10
            b_units = random.randint(10 - a_units, 9)
            b = (b // 10) * 10 + b_units
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 104:  # Adding two 3 digit numbers
        for _ in range(num_questions):
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 105:  # Adding two 4 digits
        for _ in range(num_questions):
            a = random.randint(1000, 9999)
            b = random.randint(1000, 9999)
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    elif level_num == 106:  # Adding two 5 digits
        for _ in range(num_questions):
            a = random.randint(10000, 99999)
            b = random.randint(10000, 99999)
            answer = a + b
            questions.append((f"{a} + {b} = ?", str(answer)))
    
    return questions

def generate_subtraction_questions(level_num, description, level_obj, num_questions=10):
    """Generate questions for Subtraction levels"""
    questions = []
    
    if level_num == 107:  # Subtracting from single digit (big number) a single digit (small number)
        for _ in range(num_questions):
            a = random.randint(5, 9)
            b = random.randint(1, a)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 108:  # Subtraction a single digit from a double digit (no carry over)
        for _ in range(num_questions):
            a = random.randint(10, 99)
            a_units = a % 10
            # Ensure no borrow needed
            b = random.randint(0, a_units)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 109:  # Subtraction a single digit from a double digit (include carryover)
        for _ in range(num_questions):
            a = random.randint(10, 99)
            a_units = a % 10
            # Force borrow by subtracting more than units place
            b = random.randint(a_units + 1, 9)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 110:  # Subtract double digit from a double digit (No negative answers)
        for _ in range(num_questions):
            a = random.randint(20, 99)
            b = random.randint(10, a)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 111:  # Subtraction double digit from a double digit (can result negative values)
        for _ in range(num_questions):
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 112:  # Subtract 3 digit
        for _ in range(num_questions):
            a = random.randint(100, 999)
            b = random.randint(100, a)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    elif level_num == 113:  # Subtract 4 digit
        for _ in range(num_questions):
            a = random.randint(1000, 9999)
            b = random.randint(1000, a)
            answer = a - b
            questions.append((f"{a} - {b} = ?", str(answer)))
    
    return questions

def generate_multiplication_questions(level_num, description, level_obj, num_questions=10):
    """Generate questions for Multiplication levels"""
    questions = []
    
    if level_num == 114:  # Single or double digit multiply by 1, 10
        multipliers = [1, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(1, 99)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 115:  # Single or double digit multiply by 1, 10, 100
        multipliers = [1, 10, 100]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(1, 99)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 116:  # Single or double digit multiply by 5, 10
        multipliers = [5, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(1, 99)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 117:  # Single or double digit multiply by 2, 3, 5, 10
        multipliers = [2, 3, 5, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(1, 99)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 118:  # Double or triple digit multiply by 2, 3, 4, 5, 10
        multipliers = [2, 3, 4, 5, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(10, 999)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 119:  # Double or triple digit multiply by 2, 3, 4, 5, 6, 7, 10
        multipliers = [2, 3, 4, 5, 6, 7, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(10, 999)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    elif level_num == 120:  # Triple digit multiply by 2, 3, 4, 5, 6, 7, 8, 9, 10
        multipliers = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        for _ in range(num_questions):
            multiplier = random.choice(multipliers)
            base = random.randint(100, 999)
            answer = base * multiplier
            questions.append((f"{base} × {multiplier} = ?", str(answer)))
    
    return questions

def generate_division_questions(level_num, description, level_obj, num_questions=10):
    """Generate questions for Division levels"""
    questions = []
    
    if level_num == 121:  # Double digit divide by 1, 10 (should be divisible by 10)
        divisors = [1, 10]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            if divisor == 10:
                # Ensure divisible by 10
                quotient = random.randint(1, 9)
                dividend = quotient * 10
            else:
                dividend = random.randint(10, 99)
                quotient = dividend // divisor
            answer = dividend // divisor
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 122:  # Triple digit divide by 1, 10, 100 (should be divisible by 100)
        divisors = [1, 10, 100]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            if divisor == 100:
                quotient = random.randint(1, 9)
                dividend = quotient * 100
            elif divisor == 10:
                quotient = random.randint(10, 99)
                dividend = quotient * 10
            else:
                dividend = random.randint(100, 999)
                quotient = dividend // divisor
            answer = dividend // divisor
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 123:  # Triple or double digit divide by 5, 10
        divisors = [5, 10]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            quotient = random.randint(10, 99) if divisor == 10 else random.randint(10, 199)
            dividend = quotient * divisor
            answer = quotient
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 124:  # Triple or double digit divide by 2, 3, 5, 10
        divisors = [2, 3, 5, 10]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            answer = quotient
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 125:  # Double or triple digit divide by 2, 3, 4, 5, 10
        divisors = [2, 3, 4, 5, 10]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            answer = quotient
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 126:  # Triple digit divide by 2, 3, 4, 5, 6, 7, 10
        divisors = [2, 3, 4, 5, 6, 7, 10]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            answer = quotient
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    elif level_num == 127:  # Triple digit divide by 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
        divisors = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        for _ in range(num_questions):
            divisor = random.choice(divisors)
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            answer = quotient
            questions.append((f"{dividend} ÷ {divisor} = ?", str(answer)))
    
    return questions

def generate_questions_for_level(level_num, description, level_obj):
    """Generate questions for a specific level based on its description"""
    # Determine which generator to use based on level number ranges
    if 100 <= level_num <= 106:
        questions = generate_addition_questions(level_num, description, level_obj)
    elif 107 <= level_num <= 113:
        questions = generate_subtraction_questions(level_num, description, level_obj)
    elif 114 <= level_num <= 120:
        questions = generate_multiplication_questions(level_num, description, level_obj)
    elif 121 <= level_num <= 127:
        questions = generate_division_questions(level_num, description, level_obj)
    else:
        print(f"⚠️  Unknown level number: {level_num}")
        return
    
    # Create questions in database
    created_count = 0
    for question_text, correct_answer in questions:
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_obj,
            question_text=question_text
        ).first()
        
        if existing:
            print(f"  ⏭️  Question already exists: {question_text}")
            continue
        
        # Create question
        question = Question.objects.create(
            level=level_obj,
            question_text=question_text,
            question_type='short_answer',  # Basic Facts are short answer questions
            difficulty=1,
            points=1
        )
        
        # Create correct answer
        Answer.objects.create(
            question=question,
            answer_text=correct_answer,
            is_correct=True,
            order=0
        )
        
        created_count += 1
    
    return created_count

def main():
    """Generate questions for all Basic Facts levels"""
    # Get all Basic Facts levels (100-127)
    basic_facts_levels = Level.objects.filter(level_number__gte=100, level_number__lte=127).order_by('level_number')
    
    if not basic_facts_levels.exists():
        print("❌ No Basic Facts levels found. Please run create_basic_facts.py first.")
        return
    
    total_created = 0
    for level in basic_facts_levels:
        print(f"\n📝 Generating questions for Level {level.level_number}: {level.title}")
        
        # Check existing questions
        existing_count = level.questions.count()
        if existing_count > 0:
            print(f"  ℹ️  Level already has {existing_count} questions. Generating 10 more...")
        
        created = generate_questions_for_level(level.level_number, level.title, level)
        if created:
            print(f"  ✅ Created {created} new questions")
            total_created += created
        else:
            print(f"  ⚠️  No new questions created (may already exist)")
    
    print(f"\n{'='*60}")
    print(f"✅ Question generation complete!")
    print(f"   Total new questions created: {total_created}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

