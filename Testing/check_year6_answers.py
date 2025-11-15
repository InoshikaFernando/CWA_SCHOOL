#!/usr/bin/env python
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import StudentAnswer, Level, Topic

level_6 = Level.objects.filter(level_number=6).first()
if not level_6:
    print("Year 6 not found")
    sys.exit(1)

# All Year 6 answers
all_answers = StudentAnswer.objects.filter(question__level=level_6)
print(f"Total Year 6 answers: {all_answers.count()}")

# With topic
with_topic = all_answers.filter(question__topic__isnull=False)
print(f"With topic: {with_topic.count()}")

# Without topic
without_topic = all_answers.filter(question__topic__isnull=True)
print(f"Without topic: {without_topic.count()}")

# Check Measurements topic specifically
measurements_topic = Topic.objects.filter(name="Measurements").first()
if measurements_topic:
    measurement_answers = all_answers.filter(question__topic=measurements_topic)
    print(f"Year 6 Measurements answers: {measurement_answers.count()}")
    
    # Check sessions
    sessions = measurement_answers.values_list('session_id', flat=True).distinct()
    sessions = [s for s in sessions if s]
    print(f"Unique session IDs: {len(sessions)}")
    
    if len(sessions) > 0:
        print("\nSession breakdown:")
        for session_id in sessions[:5]:
            session_answers = measurement_answers.filter(session_id=session_id)
            print(f"  Session {session_id[:8]}...: {session_answers.count()} answers")

