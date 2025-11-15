#!/usr/bin/env python
"""Check how many completed sessions exist for statistics calculation"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Level, Topic
from django.db.models import Count

YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}

print("=" * 100)
print("CHECKING COMPLETED SESSIONS FOR STATISTICS")
print("=" * 100)
print()

# Get all year levels
year_levels = Level.objects.filter(level_number__lt=100).order_by('level_number')
topics = Topic.objects.all().order_by('name')

total_completed = 0

for level in year_levels:
    level_num = level.level_number
    question_limit = YEAR_QUESTION_COUNTS.get(level_num, 20)
    partial_threshold = int(question_limit * 0.9)  # 90% threshold
    
    for topic in topics:
        # Check if there are answers for this level-topic
        answers = StudentAnswer.objects.filter(
            question__level=level,
            question__topic=topic
        ).exclude(session_id='')
        
        if answers.exists():
            # Get unique sessions
            sessions = answers.values('session_id').annotate(
                count=Count('id')
            ).filter(count__gte=partial_threshold)
            
            if sessions.exists():
                session_count = sessions.count()
                total_completed += session_count
                print(f"Year {level_num} - {topic.name}: {session_count} completed sessions (>= {partial_threshold} answers)")

print()
print(f"Total completed sessions: {total_completed}")
print()

if total_completed == 0:
    print("[WARNING] No completed sessions found. Statistics cannot be calculated.")
    print("Students need to complete quizzes (90%+ of questions) for statistics to be available.")
else:
    print("[INFO] Run calculate_topic_statistics.py to calculate averages.")

