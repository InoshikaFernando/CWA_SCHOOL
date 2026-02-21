#!/usr/bin/env python
"""
List all questions for a given topic, optionally filtered by year level.

Usage:
    python list_questions_by_topic.py --topic "Place Values"
    python list_questions_by_topic.py --topic "Place Values" --year 4
    python list_questions_by_topic.py --topic "Fractions"
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')

import django
django.setup()

from maths.models import Question, Topic


def list_questions_by_topic(topic_name, year=None):
    topics = Topic.objects.filter(name__iexact=topic_name)

    if not topics.exists():
        print(f"[ERROR] No topic found matching '{topic_name}'.")
        print("\nAvailable topics:")
        for t in Topic.objects.all().order_by('name').values_list('name', flat=True).distinct():
            print(f"  - {t}")
        return

    filters = {"topic__in": topics}
    if year is not None:
        filters["level__level_number"] = year

    questions = Question.objects.filter(**filters).select_related(
        'level', 'topic'
    ).order_by('level__level_number', 'id')

    total = questions.count()

    if total == 0:
        label = f"Year {year} " if year else ""
        print(f"[INFO] No questions found for {label}topic '{topic_name}'.")
        return

    label = f"Year {year} - " if year else ""
    print(f"\n{'=' * 80}")
    print(f"{label}{topic_name}  ({total} question(s))")
    print(f"{'=' * 80}")

    current_level = None
    for q in questions:
        level_num = q.level.level_number if q.level else "N/A"
        if level_num != current_level:
            current_level = level_num
            level_count = questions.filter(level__level_number=level_num).count()
            print(f"\n  Year {level_num}  ({level_count} question(s))")
            print(f"  {'-' * 76}")

        safe_text = q.question_text[:70].encode('ascii', 'ignore').decode('ascii')
        if len(q.question_text) > 70:
            safe_text += "..."
        has_image = "IMG" if q.image else "   "
        print(f"    [ID={q.id}] [{has_image}] [{q.question_type:<15}] {safe_text}")

    print(f"\n{'=' * 80}")
    print(f"TOTAL: {total} question(s)")


def main():
    parser = argparse.ArgumentParser(
        description="List questions for a given topic",
    )
    parser.add_argument(
        "--topic", "-t",
        required=True,
        help="Topic name (case-insensitive), e.g. 'Place Values', 'Fractions'",
    )
    parser.add_argument(
        "--year", "-y",
        type=int,
        help="Filter by year level (e.g. 4)",
    )

    args = parser.parse_args()
    list_questions_by_topic(args.topic, args.year)


if __name__ == "__main__":
    main()
