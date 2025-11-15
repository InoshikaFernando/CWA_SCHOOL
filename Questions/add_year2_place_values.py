#!/usr/bin/env python
"""
Add "Place Values" topic for Year 2 and all associated questions
This script creates the topic, associates it with Year 2, and adds all questions
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

def setup_place_values_topic():
    """Create Place Values topic and associate with Year 2"""
    
    # Get or create the "Place Values" topic
    place_values_topic, created = Topic.objects.get_or_create(name="Place Values")
    if created:
        print(f"✅ Created topic: Place Values")
    else:
        print(f"ℹ️  Topic already exists: Place Values")
    
    # Get Year 2 level
    level_2 = Level.objects.filter(level_number=2).first()
    
    if not level_2:
        print("❌ Error: Year 2 level not found!")
        return None
    
    print(f"📋 Found Year 2: {level_2}")
    
    # Check if Place Values is already associated
    if level_2.topics.filter(name="Place Values").exists():
        print("ℹ️  Year 2 already has Place Values topic associated.")
        print(f"   Current topics for Year 2: {', '.join([t.name for t in level_2.topics.all()])}")
    else:
        # Associate Place Values topic with Year 2
        level_2.topics.add(place_values_topic)
        print(f"✅ Successfully associated Place Values topic with Year 2")
        print(f"   Year 2 now has topics: {', '.join([t.name for t in level_2.topics.all()])}")
    
    return place_values_topic, level_2

def add_place_values_questions(place_values_topic, level_2):
    """Add Place Values sequence questions for Year 2"""
    
    # Define questions - forward sequences
    questions_data = [
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 1, 2, 3, 4, 5, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "6, 7, 8, 9, 10",
            "wrong_answers": [
                "5, 6, 7, 8, 9",
                "7, 8, 9, 10, 11",
                "4, 5, 6, 7, 8"
            ],
            "explanation": "Counting forward in 1s from 5: 6, 7, 8, 9, 10"
        },
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 11, 12, 13, 14, 15, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "16, 17, 18, 19, 20",
            "wrong_answers": [
                "15, 16, 17, 18, 19",
                "17, 18, 19, 20, 21",
                "14, 15, 16, 17, 18"
            ],
            "explanation": "Counting forward in 1s from 15: 16, 17, 18, 19, 20"
        },
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 23, 24, 25, 26, 27, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "28, 29, 30, 31, 32",
            "wrong_answers": [
                "27, 28, 29, 30, 31",
                "29, 30, 31, 32, 33",
                "26, 27, 28, 29, 30"
            ],
            "explanation": "Counting forward in 1s from 27: 28, 29, 30, 31, 32"
        },
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 41, 42, 43, 44, 45, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "46, 47, 48, 49, 50",
            "wrong_answers": [
                "45, 46, 47, 48, 49",
                "47, 48, 49, 50, 51",
                "44, 45, 46, 47, 48"
            ],
            "explanation": "Counting forward in 1s from 45: 46, 47, 48, 49, 50"
        },
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 77, 78, 79, 80, 81, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "82, 83, 84, 85, 86",
            "wrong_answers": [
                "81, 82, 83, 84, 85",
                "83, 84, 85, 86, 87",
                "80, 81, 82, 83, 84"
            ],
            "explanation": "Counting forward in 1s from 81: 82, 83, 84, 85, 86"
        },
        {
            "question_text": "Can you complete the following sequence by counting on in 1s? 92, 93, 94, 95, 96, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "97, 98, 99, 100, 101",
            "wrong_answers": [
                "96, 97, 98, 99, 100",
                "98, 99, 100, 101, 102",
                "95, 96, 97, 98, 99"
            ],
            "explanation": "Counting forward in 1s from 96: 97, 98, 99, 100, 101"
        },
        # Backwards sequences
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 10, 9, 8, 7, 6, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "5, 4, 3, 2, 1",
            "wrong_answers": [
                "6, 5, 4, 3, 2",
                "4, 3, 2, 1, 0",
                "7, 6, 5, 4, 3"
            ],
            "explanation": "Counting backwards in 1s from 6: 5, 4, 3, 2, 1"
        },
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 17, 16, 15, 14, 13, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "12, 11, 10, 9, 8",
            "wrong_answers": [
                "13, 12, 11, 10, 9",
                "11, 10, 9, 8, 7",
                "14, 13, 12, 11, 10"
            ],
            "explanation": "Counting backwards in 1s from 13: 12, 11, 10, 9, 8"
        },
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 27, 26, 25, 24, 23, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "22, 21, 20, 19, 18",
            "wrong_answers": [
                "23, 22, 21, 20, 19",
                "21, 20, 19, 18, 17",
                "24, 23, 22, 21, 20"
            ],
            "explanation": "Counting backwards in 1s from 23: 22, 21, 20, 19, 18"
        },
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 39, 38, 37, 36, 35, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "34, 33, 32, 31, 30",
            "wrong_answers": [
                "35, 34, 33, 32, 31",
                "33, 32, 31, 30, 29",
                "36, 35, 34, 33, 32"
            ],
            "explanation": "Counting backwards in 1s from 35: 34, 33, 32, 31, 30"
        },
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 86, 85, 84, 83, 82, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "81, 80, 79, 78, 77",
            "wrong_answers": [
                "82, 81, 80, 79, 78",
                "80, 79, 78, 77, 76",
                "83, 82, 81, 80, 79"
            ],
            "explanation": "Counting backwards in 1s from 82: 81, 80, 79, 78, 77"
        },
        {
            "question_text": "Can you complete the following sequence by counting back in 1s? 107, 106, 105, 104, 103, ___ , ___ , ___ , ___ , ___",
            "correct_answer": "102, 101, 100, 99, 98",
            "wrong_answers": [
                "103, 102, 101, 100, 99",
                "101, 100, 99, 98, 97",
                "104, 103, 102, 101, 100"
            ],
            "explanation": "Counting backwards in 1s from 103: 102, 101, 100, 99, 98"
        },
        # Skip counting by 2s (up to 20)
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 2, 4, 6, 8, ___ , ___",
            "correct_answer": "10, 12",
            "wrong_answers": [
                "9, 10",
                "10, 11",
                "12, 14"
            ],
            "explanation": "Skip counting by 2s: 2, 4, 6, 8, 10, 12"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 1, 3, 5, 7, ___ , ___",
            "correct_answer": "9, 11",
            "wrong_answers": [
                "8, 9",
                "9, 10",
                "11, 13"
            ],
            "explanation": "Skip counting by 2s starting from 1: 1, 3, 5, 7, 9, 11"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 4, 6, 8, 10, ___ , ___",
            "correct_answer": "12, 14",
            "wrong_answers": [
                "11, 12",
                "12, 13",
                "14, 16"
            ],
            "explanation": "Skip counting by 2s: 4, 6, 8, 10, 12, 14"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 3, 5, 7, 9, ___ , ___",
            "correct_answer": "11, 13",
            "wrong_answers": [
                "10, 11",
                "11, 12",
                "13, 15"
            ],
            "explanation": "Skip counting by 2s starting from 3: 3, 5, 7, 9, 11, 13"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 6, 8, 10, 12, ___ , ___",
            "correct_answer": "14, 16",
            "wrong_answers": [
                "13, 14",
                "14, 15",
                "16, 18"
            ],
            "explanation": "Skip counting by 2s: 6, 8, 10, 12, 14, 16"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 5, 7, 9, 11, ___ , ___",
            "correct_answer": "13, 15",
            "wrong_answers": [
                "12, 13",
                "13, 14",
                "15, 17"
            ],
            "explanation": "Skip counting by 2s starting from 5: 5, 7, 9, 11, 13, 15"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 8, 10, 12, 14, ___ , ___",
            "correct_answer": "16, 18",
            "wrong_answers": [
                "15, 16",
                "16, 17",
                "18, 20"
            ],
            "explanation": "Skip counting by 2s: 8, 10, 12, 14, 16, 18"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 7, 9, 11, 13, ___ , ___",
            "correct_answer": "15, 17",
            "wrong_answers": [
                "14, 15",
                "15, 16",
                "17, 19"
            ],
            "explanation": "Skip counting by 2s starting from 7: 7, 9, 11, 13, 15, 17"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 10, 12, 14, 16, ___ , ___",
            "correct_answer": "18, 20",
            "wrong_answers": [
                "17, 18",
                "18, 19",
                "20, 22"
            ],
            "explanation": "Skip counting by 2s: 10, 12, 14, 16, 18, 20"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 2s? 9, 11, 13, 15, ___ , ___",
            "correct_answer": "17, 19",
            "wrong_answers": [
                "16, 17",
                "17, 18",
                "19, 21"
            ],
            "explanation": "Skip counting by 2s starting from 9: 9, 11, 13, 15, 17, 19"
        },
        # Skip counting by 5s (up to 50)
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 5, 10, 15, 20, ___ , ___",
            "correct_answer": "25, 30",
            "wrong_answers": [
                "24, 25",
                "25, 26",
                "30, 35"
            ],
            "explanation": "Skip counting by 5s: 5, 10, 15, 20, 25, 30"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 1, 6, 11, 16, ___ , ___",
            "correct_answer": "21, 26",
            "wrong_answers": [
                "20, 21",
                "21, 22",
                "26, 31"
            ],
            "explanation": "Skip counting by 5s starting from 1: 1, 6, 11, 16, 21, 26"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 10, 15, 20, 25, ___ , ___",
            "correct_answer": "30, 35",
            "wrong_answers": [
                "29, 30",
                "30, 31",
                "35, 40"
            ],
            "explanation": "Skip counting by 5s: 10, 15, 20, 25, 30, 35"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 3, 8, 13, 18, ___ , ___",
            "correct_answer": "23, 28",
            "wrong_answers": [
                "22, 23",
                "23, 24",
                "28, 33"
            ],
            "explanation": "Skip counting by 5s starting from 3: 3, 8, 13, 18, 23, 28"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 15, 20, 25, 30, ___ , ___",
            "correct_answer": "35, 40",
            "wrong_answers": [
                "34, 35",
                "35, 36",
                "40, 45"
            ],
            "explanation": "Skip counting by 5s: 15, 20, 25, 30, 35, 40"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 2, 7, 12, 17, ___ , ___",
            "correct_answer": "22, 27",
            "wrong_answers": [
                "21, 22",
                "22, 23",
                "27, 32"
            ],
            "explanation": "Skip counting by 5s starting from 2: 2, 7, 12, 17, 22, 27"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 20, 25, 30, 35, ___ , ___",
            "correct_answer": "40, 45",
            "wrong_answers": [
                "39, 40",
                "40, 41",
                "45, 50"
            ],
            "explanation": "Skip counting by 5s: 20, 25, 30, 35, 40, 45"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 4, 9, 14, 19, ___ , ___",
            "correct_answer": "24, 29",
            "wrong_answers": [
                "23, 24",
                "24, 25",
                "29, 34"
            ],
            "explanation": "Skip counting by 5s starting from 4: 4, 9, 14, 19, 24, 29"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 25, 30, 35, 40, ___ , ___",
            "correct_answer": "45, 50",
            "wrong_answers": [
                "44, 45",
                "45, 46",
                "50, 55"
            ],
            "explanation": "Skip counting by 5s: 25, 30, 35, 40, 45, 50"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 5s? 6, 11, 16, 21, ___ , ___",
            "correct_answer": "26, 31",
            "wrong_answers": [
                "25, 26",
                "26, 27",
                "31, 36"
            ],
            "explanation": "Skip counting by 5s starting from 6: 6, 11, 16, 21, 26, 31"
        },
        # Skip counting by 10s (up to 100)
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 10, 20, 30, 40, ___ , ___",
            "correct_answer": "50, 60",
            "wrong_answers": [
                "49, 50",
                "50, 51",
                "60, 70"
            ],
            "explanation": "Skip counting by 10s: 10, 20, 30, 40, 50, 60"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 1, 11, 21, 31, ___ , ___",
            "correct_answer": "41, 51",
            "wrong_answers": [
                "40, 41",
                "41, 42",
                "51, 61"
            ],
            "explanation": "Skip counting by 10s starting from 1: 1, 11, 21, 31, 41, 51"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 20, 30, 40, 50, ___ , ___",
            "correct_answer": "60, 70",
            "wrong_answers": [
                "59, 60",
                "60, 61",
                "70, 80"
            ],
            "explanation": "Skip counting by 10s: 20, 30, 40, 50, 60, 70"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 3, 13, 23, 33, ___ , ___",
            "correct_answer": "43, 53",
            "wrong_answers": [
                "42, 43",
                "43, 44",
                "53, 63"
            ],
            "explanation": "Skip counting by 10s starting from 3: 3, 13, 23, 33, 43, 53"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 30, 40, 50, 60, ___ , ___",
            "correct_answer": "70, 80",
            "wrong_answers": [
                "69, 70",
                "70, 71",
                "80, 90"
            ],
            "explanation": "Skip counting by 10s: 30, 40, 50, 60, 70, 80"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 5, 15, 25, 35, ___ , ___",
            "correct_answer": "45, 55",
            "wrong_answers": [
                "44, 45",
                "45, 46",
                "55, 65"
            ],
            "explanation": "Skip counting by 10s starting from 5: 5, 15, 25, 35, 45, 55"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 40, 50, 60, 70, ___ , ___",
            "correct_answer": "80, 90",
            "wrong_answers": [
                "79, 80",
                "80, 81",
                "90, 100"
            ],
            "explanation": "Skip counting by 10s: 40, 50, 60, 70, 80, 90"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 7, 17, 27, 37, ___ , ___",
            "correct_answer": "47, 57",
            "wrong_answers": [
                "46, 47",
                "47, 48",
                "57, 67"
            ],
            "explanation": "Skip counting by 10s starting from 7: 7, 17, 27, 37, 47, 57"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 50, 60, 70, 80, ___ , ___",
            "correct_answer": "90, 100",
            "wrong_answers": [
                "89, 90",
                "90, 91",
                "100, 110"
            ],
            "explanation": "Skip counting by 10s: 50, 60, 70, 80, 90, 100"
        },
        {
            "question_text": "Can you complete the following sequence by skip counting by 10s? 9, 19, 29, 39, ___ , ___",
            "correct_answer": "49, 59",
            "wrong_answers": [
                "48, 49",
                "49, 50",
                "59, 69"
            ],
            "explanation": "Skip counting by 10s starting from 9: 9, 19, 29, 39, 49, 59"
        },
        # Tens and ones place value questions (1-20)
        {
            "question_text": "How many tens and ones does the number 1 have?",
            "correct_answer": "0 tens, 1 one",
            "wrong_answers": [
                "1 ten, 0 ones",
                "0 tens, 0 ones",
                "1 ten, 1 one"
            ],
            "explanation": "The number 1 has 0 tens and 1 one."
        },
        {
            "question_text": "How many tens and ones does the number 2 have?",
            "correct_answer": "0 tens, 2 ones",
            "wrong_answers": [
                "2 tens, 0 ones",
                "0 tens, 1 one",
                "1 ten, 2 ones"
            ],
            "explanation": "The number 2 has 0 tens and 2 ones."
        },
        {
            "question_text": "How many tens and ones does the number 3 have?",
            "correct_answer": "0 tens, 3 ones",
            "wrong_answers": [
                "3 tens, 0 ones",
                "0 tens, 2 ones",
                "1 ten, 3 ones"
            ],
            "explanation": "The number 3 has 0 tens and 3 ones."
        },
        {
            "question_text": "How many tens and ones does the number 4 have?",
            "correct_answer": "0 tens, 4 ones",
            "wrong_answers": [
                "4 tens, 0 ones",
                "0 tens, 3 ones",
                "1 ten, 4 ones"
            ],
            "explanation": "The number 4 has 0 tens and 4 ones."
        },
        {
            "question_text": "How many tens and ones does the number 5 have?",
            "correct_answer": "0 tens, 5 ones",
            "wrong_answers": [
                "5 tens, 0 ones",
                "0 tens, 4 ones",
                "1 ten, 5 ones"
            ],
            "explanation": "The number 5 has 0 tens and 5 ones."
        },
        {
            "question_text": "How many tens and ones does the number 6 have?",
            "correct_answer": "0 tens, 6 ones",
            "wrong_answers": [
                "6 tens, 0 ones",
                "0 tens, 5 ones",
                "1 ten, 6 ones"
            ],
            "explanation": "The number 6 has 0 tens and 6 ones."
        },
        {
            "question_text": "How many tens and ones does the number 7 have?",
            "correct_answer": "0 tens, 7 ones",
            "wrong_answers": [
                "7 tens, 0 ones",
                "0 tens, 6 ones",
                "1 ten, 7 ones"
            ],
            "explanation": "The number 7 has 0 tens and 7 ones."
        },
        {
            "question_text": "How many tens and ones does the number 8 have?",
            "correct_answer": "0 tens, 8 ones",
            "wrong_answers": [
                "8 tens, 0 ones",
                "0 tens, 7 ones",
                "1 ten, 8 ones"
            ],
            "explanation": "The number 8 has 0 tens and 8 ones."
        },
        {
            "question_text": "How many tens and ones does the number 9 have?",
            "correct_answer": "0 tens, 9 ones",
            "wrong_answers": [
                "9 tens, 0 ones",
                "0 tens, 8 ones",
                "1 ten, 9 ones"
            ],
            "explanation": "The number 9 has 0 tens and 9 ones."
        },
        {
            "question_text": "How many tens and ones does the number 10 have?",
            "correct_answer": "1 ten, 0 ones",
            "wrong_answers": [
                "0 tens, 10 ones",
                "1 ten, 1 one",
                "10 tens, 0 ones"
            ],
            "explanation": "The number 10 has 1 ten and 0 ones."
        },
        {
            "question_text": "How many tens and ones does the number 11 have?",
            "correct_answer": "1 ten, 1 one",
            "wrong_answers": [
                "0 tens, 11 ones",
                "1 ten, 0 ones",
                "11 tens, 0 ones"
            ],
            "explanation": "The number 11 has 1 ten and 1 one."
        },
        {
            "question_text": "How many tens and ones does the number 12 have?",
            "correct_answer": "1 ten, 2 ones",
            "wrong_answers": [
                "0 tens, 12 ones",
                "1 ten, 1 one",
                "12 tens, 0 ones"
            ],
            "explanation": "The number 12 has 1 ten and 2 ones."
        },
        {
            "question_text": "How many tens and ones does the number 13 have?",
            "correct_answer": "1 ten, 3 ones",
            "wrong_answers": [
                "0 tens, 13 ones",
                "1 ten, 2 ones",
                "13 tens, 0 ones"
            ],
            "explanation": "The number 13 has 1 ten and 3 ones."
        },
        {
            "question_text": "How many tens and ones does the number 14 have?",
            "correct_answer": "1 ten, 4 ones",
            "wrong_answers": [
                "0 tens, 14 ones",
                "1 ten, 3 ones",
                "14 tens, 0 ones"
            ],
            "explanation": "The number 14 has 1 ten and 4 ones."
        },
        {
            "question_text": "How many tens and ones does the number 15 have?",
            "correct_answer": "1 ten, 5 ones",
            "wrong_answers": [
                "0 tens, 15 ones",
                "1 ten, 4 ones",
                "15 tens, 0 ones"
            ],
            "explanation": "The number 15 has 1 ten and 5 ones."
        },
        {
            "question_text": "How many tens and ones does the number 16 have?",
            "correct_answer": "1 ten, 6 ones",
            "wrong_answers": [
                "0 tens, 16 ones",
                "1 ten, 5 ones",
                "16 tens, 0 ones"
            ],
            "explanation": "The number 16 has 1 ten and 6 ones."
        },
        {
            "question_text": "How many tens and ones does the number 17 have?",
            "correct_answer": "1 ten, 7 ones",
            "wrong_answers": [
                "0 tens, 17 ones",
                "1 ten, 6 ones",
                "17 tens, 0 ones"
            ],
            "explanation": "The number 17 has 1 ten and 7 ones."
        },
        {
            "question_text": "How many tens and ones does the number 18 have?",
            "correct_answer": "1 ten, 8 ones",
            "wrong_answers": [
                "0 tens, 18 ones",
                "1 ten, 7 ones",
                "18 tens, 0 ones"
            ],
            "explanation": "The number 18 has 1 ten and 8 ones."
        },
        {
            "question_text": "How many tens and ones does the number 19 have?",
            "correct_answer": "1 ten, 9 ones",
            "wrong_answers": [
                "0 tens, 19 ones",
                "1 ten, 8 ones",
                "19 tens, 0 ones"
            ],
            "explanation": "The number 19 has 1 ten and 9 ones."
        },
        {
            "question_text": "How many tens and ones does the number 20 have?",
            "correct_answer": "2 tens, 0 ones",
            "wrong_answers": [
                "0 tens, 20 ones",
                "1 ten, 10 ones",
                "20 tens, 0 ones"
            ],
            "explanation": "The number 20 has 2 tens and 0 ones."
        },
    ]
    
    print(f"\n📝 Adding {len(questions_data)} Place Values questions (counting and skip counting) for Year 2...\n")
    
    created_count = 0
    skipped_count = 0
    
    for i, q_data in enumerate(questions_data, 1):
        # Check if question already exists
        existing = Question.objects.filter(
            level=level_2,
            question_text=q_data["question_text"]
        ).first()
        
        if existing:
            # Update topic if not set
            if not existing.topic:
                existing.topic = place_values_topic
                existing.save()
                print(f"  [UPDATE] Question {i}: Set topic to Place Values")
            else:
                print(f"  [SKIP] Question {i} already exists, skipping...")
            skipped_count += 1
            continue
        
        # Create question
        question = Question.objects.create(
            level=level_2,
            topic=place_values_topic,  # Set topic directly on question
            question_text=q_data["question_text"],
            question_type='multiple_choice',
            difficulty=1,
            points=1,
            explanation=q_data["explanation"]
        )
        
        # Ensure question has topic set and level has topic associated
        if not question.topic:
            question.topic = place_values_topic
            question.save()
        question.level.topics.add(place_values_topic)
        
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
        
        print(f"  ✅ Created Question {i}: {q_data['question_text'][:50]}...")
        created_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count} questions")
    print(f"   ⏭️  Skipped: {skipped_count} questions (already exist)")
    print(f"\n✅ All questions are associated with Place Values topic for Year 2")

if __name__ == "__main__":
    print("🔄 Setting up Place Values topic for Year 2...\n")
    result = setup_place_values_topic()
    
    if result:
        place_values_topic, level_2 = result
        print("\n" + "="*60)
        add_place_values_questions(place_values_topic, level_2)
        print("\n✅ Done!")
