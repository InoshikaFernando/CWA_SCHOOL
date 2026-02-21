#!/usr/bin/env python
"""
List all questions in the database that have no topic assigned.
Groups results by year level for easy review.

Usage:
    python list_topicless_questions.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')

import django
django.setup()

from maths.models import Question, Level


def list_topicless_questions():
    topicless = Question.objects.filter(topic__isnull=True).select_related('level').order_by('level__level_number', 'id')
    total = topicless.count()

    if total == 0:
        print("No topicless questions found.")
        return

    print(f"Found {total} question(s) without a topic:\n")

    current_level = None
    for q in topicless:
        level_num = q.level.level_number if q.level else "N/A"
        if level_num != current_level:
            current_level = level_num
            level_count = topicless.filter(level__level_number=level_num).count()
            print(f"\n{'=' * 70}")
            print(f"Year {level_num}  ({level_count} question(s))")
            print(f"{'=' * 70}")

        safe_text = q.question_text[:80].encode('ascii', 'ignore').decode('ascii')
        has_image = "IMG" if q.image else "   "
        print(f"  [ID={q.id}] [{has_image}] {safe_text}")

    print(f"\n{'=' * 70}")
    print(f"TOTAL: {total} question(s) without a topic")


if __name__ == "__main__":
    list_topicless_questions()
