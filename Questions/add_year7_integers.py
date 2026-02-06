#!/usr/bin/env python
"""
Add/Update "Integers" questions for Year 7
This script can be run multiple times - it will:
- Add new questions if they don't exist
- Update answers if they've changed
- Skip questions that are already up-to-date
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
from django.core.files import File
from django.conf import settings
from question_utils import process_questions

def setup_integers_topic():
    """Create Integers topic and associate with Year 7"""
    
    # Get or create the "Integers" topic
    # Handle case where multiple topics with same name exist
    integers_topic = Topic.objects.filter(name="Integers").first()
    if not integers_topic:
        integers_topic = Topic.objects.create(name="Integers")
        print(f"[OK] Created topic: Integers")
    else:
        print(f"[INFO] Topic already exists: Integers")
    
    # Get Year 7 level
    level_7 = Level.objects.filter(level_number=7).first()
    
    if not level_7:
        print("[ERROR] Year 7 level not found!")
        return None
    
    print(f"[INFO] Found Year 7: {level_7}")
    
    # Check if Integers is already associated
    if level_7.topics.filter(name="Integers").exists():
        print("[INFO] Year 7 already has Integers topic associated.")
        print(f"   Current topics for Year 7: {', '.join([t.name for t in level_7.topics.all()])}")
    else:
        # Associate Integers topic with Year 7
        level_7.topics.add(integers_topic)
        print(f"[OK] Successfully associated Integers topic with Year 7")
        print(f"   Year 7 now has topics: {', '.join([t.name for t in level_7.topics.all()])}")
    
    return integers_topic, level_7

def add_integers_questions(integers_topic, level_7):
    """Add/Update Integers questions for Year 7"""
    
    # Define all questions - edit this section to add/modify questions
    # NOTE: Questions are identified by exact question_text match
    # To add a new question: Add it to this list
    # To modify a question: Change the data here and re-run the script
    # 
    # Format for each question:
    # {
    #     "question_text": "Your question here",
    #     "correct_answer": "The correct answer",
    #     "wrong_answers": ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
    #     "explanation": "Explanation of the correct answer"
    # }
    
    questions_data = [
        {
            "question_text": "Which of the following is true?",
            "correct_answer": "7 < 16",
            "wrong_answers": ["8 > 11", "15 < 9", "12 < 14"],
            "explanation": "7 is less than 16, making this the true statement. The other options are all false: 8 is not greater than 11, 15 is not less than 9, and 12 is not less than 14."
        },
        {
            "question_text": "Using	numerals, two thousand	and	seventy-six	is:",
            "correct_answer": "2076",
            "wrong_answers": ["276", "20076", "2706"],
            "explanation": "The numeral representation of two thousand and seventy-six is 2076."
        },
        {
            "question_text": "What	is	the	difference	between	76	and	49?",
            "correct_answer": "27",
            "wrong_answers": ["23", "25", "37"],
            "explanation": "The difference between 76 and 49 is 27. This is calculated by subtracting 49 from 76 (76 - 49 = 27). The other options are incorrect: -4 is a negative integer, 0 is neither positive nor negative, and 3 is a positive integer."
        },
        {
            "question_text": "The	place	value	of	9	in	4936	is:",
            "correct_answer": "900",
            "wrong_answers": ["90", "9", "9000"],
            "explanation": "The place value of 9 in the number 4936 is 900, because it is in the hundreds place. The other options are incorrect: 90 would be the place value if 9 were in the tens place, 9 would be the place value if it were in the ones place, and 9000 would be the place value if it were in the thousands place."
        },
        {
            "question_text": "6	× 1000		+		3	× 10		+		2	× 1	is	the	expanded	from	of:",
            "correct_answer": "6032",
            "wrong_answers": ["632", "60032", "603"],
            "explanation": "The expanded form 6 × 1000 + 3 × 10 + 2 × 1 represents the number 6032. This is calculated by multiplying each digit by its place value and then adding them together: (6 × 1000) + (3 × 10) + (2 × 1) = 6000 + 30 + 2 = 6032.",
        },
        {
            "question_text": "The product	of 32 and	4 is:",
            "correct_answer": "128",
            "wrong_answers": ["36", "1280", "12"],
            "explanation": "The product of 32 and 4 is 128, calculated by multiplying the two numbers together (32 × 4 = 128). The other options are incorrect: 36 is the sum of 32 and 4, 1280 is the result of multiplying 32 by 40, and 12 is the result of dividing 32 by 4.",
        },
        {
            "question_text": "The	quotient	of	12	and	4	is:",
            "correct_answer": "3",
            "wrong_answers": ["48", "16", "0.33"],
            "explanation": "The quotient of 12 and 4 is 3, calculated by dividing 12 by 4 (12 ÷ 4 = 3). The other options are incorrect: 48 is the product of 12 and 4, 16 is the result of multiplying 4 by itself, and 0.33 is an approximation of the result of dividing 1 by 3."
        },
        {
            "question_text": "When	651	is	divided	by	8,	the	remainder	is:",
            "correct_answer": "3",
            "wrong_answers": ["81", "1", "8"],
            "explanation": "When 651 is divided by 8, the quotient is 81 with a remainder of 3. This is calculated by performing the division: 651 ÷ 8 = 81 R3. The other options are incorrect: 0 would mean that 651 is perfectly divisible by 8, which it is not; 1 would mean that the remainder is 1, which is also incorrect; and 8 cannot be a remainder when dividing by 8, as the remainder must be less than the divisor."
        },
        {
            "question_text": "When	739	is	rounded	using	leading	digit	approximation,	it	becomes:",
            "correct_answer": "700",
            "wrong_answers": ["740", "730", "800"],
            "explanation": "When rounding 739 using leading digit approximation, we look at the leading digit, which is 7. Since the next digit (3) is less than 5, we round down to 700. The other options are incorrect: 740 would be the result of rounding to the nearest ten, 730 would be the result of rounding to the nearest ten but incorrectly, and 800 would be the result of rounding up, which is not correct in this case."
        },
        {
            "question_text" : "2	+	6	×	(7	−	5)	÷	3	evaluates	to:",
            "correct_answer": "6",
            "wrong_answers": ["8", "10", "4"],
            "explanation": "To evaluate the expression 2 + 6 × (7 − 5) ÷ 3, we follow the order of operations (parentheses, exponents, multiplication and division from left to right, and then addition and subtraction from left to right). First, we evaluate the parentheses: (7 − 5) = 2. Next, we perform the multiplication: 6 × 2 = 12. Then we perform the division: 12 ÷ 3 = 4. Finally, we perform the addition: 2 + 4 = 6. The other options are incorrect because they do not follow the correct order of operations or they contain calculation errors."
        },
        {
            "question_text": "What is the the	place	value	of	the	digit	5 of 856?",
            "correct_answer": "50",
            "wrong_answers": ["500", "5", "5000"],
            "explanation": "In the number 856, the digit 5 is in the tens place. Therefore, its place value is 5 × 10 = 50. The other options are incorrect: 500 is the place value of the digit 8, 5 is the place value of the digit 6, and 5000 is the place value of the digit 8 in a different number."
        },
        {
            "question_text": "What is the the	place	value	of	the	digit	5 of 1544?",
            "correct_answer": "500",
            "wrong_answers": ["50", "5", "5000"],
            "explanation": "In the number 1544, the digit 5 is in the hundreds place. Therefore, its place value is 5 × 100 = 500. The other options are incorrect: 50 is the place value of the digit 4 in the tens place, 5 is the place value of the digit 4 in the ones place, and 5000 is the place value of the digit 1 in the thousands place."
        },
        {
            "question_text": "162	+	327    =	? ",
            "correct_answer": "489",
            "wrong_answers": ["490", "488", "479"],
            "explanation": "The sum of 162 and 327 is 489. This is calculated by adding the numbers: 162 + 327 = 489. The other options are incorrect: 490 is one more than the correct answer, 488 is one less than the correct answer, and 479 is ten less than the correct answer."
        },
        {
            "question_text": "75	−	21	=	? ",
            "correct_answer": "54",
            "wrong_answers": ["55", "53", "56"],
            "explanation": "The difference of 75 and 21 is 54. This is calculated by subtracting the numbers: 75 − 21 = 54. The other options are incorrect: 55 is one more than the correct answer, 53 is one less than the correct answer, and 56 is two more than the correct answer."
        },
        {
            "question_text": "45	+	43	=	? ",
            "correct_answer": "88",
            "wrong_answers": ["89", "87", "86"],
            "explanation": "The sum of 45 and 43 is 88. This is calculated by adding the numbers: 45 + 43 = 88. The other options are incorrect: 89 is one more than the correct answer, 87 is one less than the correct answer, and 86 is two less than the correct answer."
        },
        {
            "question_text": "6	×	19	=	? ",
            "correct_answer": "114",
            "wrong_answers": ["115", "113", "104"],
            "explanation": "The product of 6 and 19 is 114. This is calculated by multiplying the numbers: 6 × 19 = 114. The other options are incorrect: 115 is one more than the correct answer, 113 is one less than the correct answer, and 104 is ten less than the correct answer."
        },
        {
            "question_text": "3	×	28	=	? ",
            "correct_answer": "84",
            "wrong_answers": ["85", "83", "74"],
            "explanation": "The product of 3 and 28 is 84. This is calculated by multiplying the numbers: 3 × 28 = 84. The other options are incorrect: 85 is one more than the correct answer, 83 is one less than the correct answer, and 74 is ten less than the correct answer."
        },
        {
            "question_text": "186	÷	6	=	? ",
            "correct_answer": "31",
            "wrong_answers": ["30", "32", "29"],
            "explanation": "The quotient of 186 and 6 is 31. This is calculated by dividing the numbers: 186 ÷ 6 = 31. The other options are incorrect: 30 is one less than the correct answer, 32 is one more than the correct answer, and 29 is two less than the correct answer."
        },
        {
            "question_text": "1 A	car’s	odometer	shows	7854	kilometres	at	the	start	of	a	journey. When	the	driver	stops	for	lunch,	the	odometer	reads	8012	kilometres.	How	far	has	the	car	travelled?",
            "correct_answer": "158 kilometres",
            "wrong_answers": ["1580 kilometres", "15800 kilometres", "15.8 kilometres"],
            "explanation": "The distance travelled by the car is calculated by subtracting the starting odometer reading from the ending odometer reading: 8012 km - 7854 km = 158 km. The other options are incorrect: 1580 kilometres is ten times the correct answer, 15800 kilometres is one hundred times the correct answer, and 15.8 kilometres is one tenth of the correct answer."
        },
        {
            "question_text": "1 A	car’s	odometer	shows	7854	kilometres	at	the	start-of-a-journey. What will the car’s	odometer read if the car then travels a	further	59	kilometres?",
            "correct_answer": "7913 kilometres",
            "wrong_answers": ["7903 kilometres", "7923 kilometres", "7803 kilometres"],
            "explanation": "The car's odometer will read 7854 km + 59 km = 7913 km. The other options are incorrect: 7903 kilometres is 51 km less than the correct answer, 7923 kilometres is 9 km more than the correct answer, and 7803 kilometres is 51 km less than the correct answer."
        },
        {
            "question_text": "The	sum-of	13	and	double	7	is	multiplied	by	100",
            "correct_answer": "2700",
            "wrong_answers": ["2600", "2800", "270"],
            "explanation": "The sum of 13 and double 7 is 13 + (2 × 7) = 13 + 14 = 27. When this is multiplied by 100, the result is 27 × 100 = 2700. The other options are incorrect: 2600 is one hundred less than the correct answer, 2800 is one hundred more than the correct answer, and 270 is one tenth of the correct answer."
        },
        {
            "question_text": "The	difference	between	123	and	56	is	tripled,	and	then	the	quotient	of	342	and	this	result	is	calculated.	What	is	the	final	answer?",
            "correct_answer": "2",
            "wrong_answers": ["1", "3", "4"],
            "explanation": "The difference between 123 and 56 is 123 - 56 = 67. When this is tripled, we get 67 × 3 = 201. The quotient of 342 and 201 is 342 ÷ 201 = 2. The other options are incorrect: 1 is too small, 3 is too large, and 4 is also too large."
        }

    ]
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for q_data in questions_data:
        question_text = q_data["question_text"]
        
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_7,
            topic=integers_topic,
            question_text=question_text
        ).first()
        
        if existing:
            # Question already exists, update if needed
            existing.explanation = q_data["explanation"]
            existing.save()
            
            # Delete old answers and recreate
            Answer.objects.filter(question=existing).delete()
            
            # Create correct answer
            Answer.objects.create(
                question=existing,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=existing,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )
            
            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [UPDATE] Updated: {safe_text}...")
            updated_count += 1
        else:
            # Create new question
            question = Question.objects.create(
                level=level_7,
                topic=integers_topic,
                question_text=question_text,
                question_type="Multiple Choice",
                difficulty="Medium",
                points=1,
                explanation=q_data["explanation"]
            )
            
            # Create correct answer
            Answer.objects.create(
                question=question,
                answer_text=q_data["correct_answer"],
                is_correct=True,
                order=0
            )
            
            # Create wrong answers in random order
            wrong_answers = q_data["wrong_answers"][:]
            random.shuffle(wrong_answers)
            for idx, wrong_answer in enumerate(wrong_answers):
                Answer.objects.create(
                    question=question,
                    answer_text=wrong_answer,
                    is_correct=False,
                    order=idx + 1
                )
            
            safe_text = question_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [OK] Created: {safe_text}...")
            created_count += 1
    
    print(f"\n[SUMMARY]")
    print(f"   [OK] Created: {created_count} questions")
    print(f"   [UPDATE] Updated: {updated_count} questions")
    print(f"   [SKIP] Skipped: {skipped_count} questions")
    print(f"\n[OK] All Integers questions are associated with Year 7")

if __name__ == "__main__":
    print("[INFO] Setting up Integers topic for Year 7...\n")
    result = setup_integers_topic()
    
    if result:
        integers_topic, level_7 = result
        print("\n" + "="*60)
        add_integers_questions(integers_topic, level_7)
        print("\n[OK] Done!")
