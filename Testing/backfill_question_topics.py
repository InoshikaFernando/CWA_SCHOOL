#!/usr/bin/env python
"""
Backfill topic field for existing questions based on text patterns
This script assigns topics to questions that don't have a topic set yet
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question, Topic, Level
from django.db.models import Q

def backfill_topics():
    """Assign topics to questions based on text patterns"""
    
    # Get all topics
    bodmas_topic = Topic.objects.filter(name="BODMAS/PEMDAS").first()
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    fractions_topic = Topic.objects.filter(name="Fractions").first()
    place_values_topic = Topic.objects.filter(name="Place Values").first()
    
    # Get questions without topics
    questions_without_topic = Question.objects.filter(topic__isnull=True)
    print(f"[INFO] Found {questions_without_topic.count()} questions without topics")
    
    updated_count = 0
    
    for question in questions_without_topic:
        q_text_lower = question.question_text.lower()
        topic_assigned = False
        
        # Check for BODMAS/PEMDAS
        if not topic_assigned and (
            q_text_lower.startswith('evaluate:') or
            q_text_lower.startswith('calculate:') or
            q_text_lower.startswith('find the missing number:') or
            q_text_lower.startswith('i think of a number') or
            q_text_lower.startswith('i add') or
            q_text_lower.startswith('i multiply') or
            q_text_lower.startswith('using the digits') or
            q_text_lower.startswith('write down what') or
            'bodmas' in q_text_lower or
            'pemdas' in q_text_lower or
            'bidmas' in q_text_lower or
            '_____' in question.question_text
        ) and not any(pattern in q_text_lower for pattern in [
            'cm', 'centimeter', 'meter', 'kilometer', 'width', 'height', 'length',
            'area', 'perimeter', 'volume', 'measure', 'numerator', 'denominator',
            'fraction', 'complete the following sequence', 'counting on', 'counting back',
            'skip counting', 'tens and ones', 'how many tens'
        ]):
            if bodmas_topic:
                question.topic = bodmas_topic
                question.save()
                updated_count += 1
                topic_assigned = True
                # Safe print that handles Unicode
                safe_text = question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
                print(f"  [OK] Assigned BODMAS to: {safe_text}...")
        
        # Check for Place Values (Year 2 patterns + Year 4 patterns)
        if not topic_assigned and (
            'complete the following sequence' in q_text_lower or
            'counting on' in q_text_lower or
            'counting back' in q_text_lower or
            'skip counting' in q_text_lower or
            'tens and ones' in q_text_lower or
            'how many tens' in q_text_lower or
            'place value' in q_text_lower or
            'hundreds + ' in q_text_lower or
            'hundreds =' in q_text_lower or
            'tens place' in q_text_lower or
            'hundreds place' in q_text_lower or
            'thousands place' in q_text_lower or
            'ones place' in q_text_lower or
            'value of the digit' in q_text_lower or
            'where is the digit' in q_text_lower or
            ('hundreds' in q_text_lower and 'tens' in q_text_lower and 'ones' in q_text_lower)
        ) and not any(pattern in q_text_lower for pattern in [
            'which unit would you use', 'measure the length', 'centimeter', 'meter', 'kilometer'
        ]):
            if place_values_topic:
                question.topic = place_values_topic
                question.save()
                updated_count += 1
                topic_assigned = True
                # Safe print that handles Unicode
                safe_text = question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
                print(f"  [OK] Assigned Place Values to: {safe_text}...")
        
        # Check for Measurements
        if not topic_assigned and (
            'measure' in q_text_lower or
            'length' in q_text_lower or
            'width' in q_text_lower or
            'height' in q_text_lower or
            'centimeter' in q_text_lower or
            'meter' in q_text_lower or
            'kilometer' in q_text_lower or
            'unit would you use' in q_text_lower or
            'ruler' in q_text_lower or
            'scale' in q_text_lower
        ) and not any(pattern in q_text_lower for pattern in [
            'complete the following sequence', 'counting on', 'counting back',
            'skip counting', 'tens and ones', 'how many tens'
        ]):
            if measurements_topic:
                question.topic = measurements_topic
                question.save()
                updated_count += 1
                topic_assigned = True
                # Safe print that handles Unicode
                safe_text = question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
                print(f"  [OK] Assigned Measurements to: {safe_text}...")
        
        # Check for Fractions
        if not topic_assigned and (
            'numerator' in q_text_lower or
            'denominator' in q_text_lower or
            'fraction' in q_text_lower
        ):
            if fractions_topic:
                question.topic = fractions_topic
                question.save()
                updated_count += 1
                topic_assigned = True
                # Safe print that handles Unicode
                safe_text = question.question_text[:50].encode('ascii', 'ignore').decode('ascii')
                print(f"  [OK] Assigned Fractions to: {safe_text}...")
    
    print(f"\n[SUMMARY]")
    print(f"   [OK] Updated {updated_count} questions with topics")
    remaining = Question.objects.filter(topic__isnull=True).count()
    if remaining > 0:
        print(f"   [INFO] {remaining} questions still without topics")

if __name__ == "__main__":
    print("[INFO] Backfilling topics for existing questions...\n")
    backfill_topics()
    print("\n[OK] Done!")

