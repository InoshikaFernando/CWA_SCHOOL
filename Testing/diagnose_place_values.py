#!/usr/bin/env python
"""
Diagnose why Year 4 Place Values questions don't load in the view.
Runs the exact same queries the view uses and reports results.

Usage:
    python Testing/diagnose_place_values.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')

import django
django.setup()

from maths.models import Question, Topic, Level


def diagnose():
    print("=" * 70)
    print("DIAGNOSING YEAR 4 PLACE VALUES")
    print("=" * 70)

    print("\n--- 1. Level objects with level_number=4 ---")
    levels = Level.objects.filter(level_number=4)
    print(f"  Count: {levels.count()}")
    for lv in levels:
        print(f"  Level ID={lv.id}, level_number={lv.level_number}, name='{lv.name}'")

    print("\n--- 2. Topic objects with name='Place Values' ---")
    topics_exact = Topic.objects.filter(name="Place Values")
    print(f"  Exact match (name='Place Values'): {topics_exact.count()}")
    for t in topics_exact:
        print(f"  Topic ID={t.id}, name='{t.name}'")

    topics_iexact = Topic.objects.filter(name__iexact="Place Values")
    print(f"  Case-insensitive match: {topics_iexact.count()}")
    for t in topics_iexact:
        print(f"  Topic ID={t.id}, name='{t.name}'")

    topics_contains = Topic.objects.filter(name__icontains="place")
    print(f"  Contains 'place': {topics_contains.count()}")
    for t in topics_contains:
        print(f"  Topic ID={t.id}, name='{t.name}'")

    print("\n--- 3. Questions with level__level_number=4 AND topic__name='Place Values' ---")
    q1 = Question.objects.filter(level__level_number=4, topic__name="Place Values")
    print(f"  Count: {q1.count()}")

    print("\n--- 4. Questions with level=<Level object> AND topic__name='Place Values' ---")
    if levels.exists():
        level_obj = levels.first()
        q2 = Question.objects.filter(level=level_obj, topic__name="Place Values")
        print(f"  Using Level ID={level_obj.id}: Count={q2.count()}")

        for lv in levels:
            q = Question.objects.filter(level=lv, topic__name="Place Values")
            print(f"  Using Level ID={lv.id}: Count={q.count()}")
    else:
        print("  No Level with level_number=4 found!")

    print("\n--- 5. Questions with level__level_number=4 AND topic__isnull=True ---")
    q3 = Question.objects.filter(level__level_number=4, topic__isnull=True)
    print(f"  Topicless Year 4 questions: {q3.count()}")

    print("\n--- 6. ALL questions with level__level_number=4 grouped by topic ---")
    all_year4 = Question.objects.filter(level__level_number=4).select_related('topic')
    topic_counts = {}
    for q in all_year4:
        t_name = q.topic.name if q.topic else "(NULL)"
        topic_counts[t_name] = topic_counts.get(t_name, 0) + 1
    for t_name, count in sorted(topic_counts.items()):
        print(f"  {t_name}: {count} questions")

    print("\n--- 7. Year 4 Place Values questions - which Level IDs? ---")
    pv_year4 = Question.objects.filter(level__level_number=4, topic__name="Place Values").select_related('level')
    level_ids = set()
    for q in pv_year4:
        level_ids.add(q.level_id)
    print(f"  Distinct level IDs: {level_ids}")
    print(f"  get_object_or_404(Level, level_number=4) would return ID={levels.first().id if levels.exists() else 'N/A'}")
    if levels.exists() and level_ids and levels.first().id not in level_ids:
        print("  *** MISMATCH! The view's Level object ID doesn't match the questions' Level IDs ***")

    print("\n--- 8. Topic-Level M2M for Place Values ---")
    for t in topics_exact:
        linked_levels = t.levels.all()
        print(f"  Topic ID={t.id} linked levels: {[(lv.id, lv.level_number) for lv in linked_levels]}")

    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    diagnose()
