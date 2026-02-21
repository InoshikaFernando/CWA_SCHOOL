#!/usr/bin/env python
"""
Common utility to add/update questions from JSON files.

JSON files are stored in Questions/json_questions/ with naming convention:
    <year>-<topic-slug>.json

The year-topic mapping is derived from YEAR_TOPICS_MAP in views.py.

Usage:
    # Load questions from a specific JSON file
    python add_questions_from_json.py --file 2-measurements.json

    # Load questions for a specific year (all topics)
    python add_questions_from_json.py --year 2

    # Load questions for all years and topics
    python add_questions_from_json.py --all

    # List all expected JSON files (based on YEAR_TOPICS_MAP)
    python add_questions_from_json.py --list
"""
import os
import sys
import json
import re
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')

import django
django.setup()

from maths.models import Level, Topic, Question
from question_utils import process_questions

YEAR_TOPICS_MAP = {
    2: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("Place Values", "place_values_questions", "Place Values"),
    ],
    3: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("Fractions", "fractions_questions", "Fractions"),
        ("Finance", "finance_questions", "Finance"),
        ("Date and Time", "date_time_questions", "Date and Time"),
    ],
    4: [
        ("Fractions", "fractions_questions", "Fractions"),
        ("Integers", "integers_questions", "Integers"),
        ("Place Values", "place_values_questions", "Place Values"),
    ],
    5: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
    ],
    6: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
        ("Whole Numbers", "whole_numbers_questions", "Whole Numbers"),
        ("Factors", "factors_questions", "Factors"),
        ("Angles", "angles_questions", "Angles"),
    ],
    7: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
        ("Integers", "integers_questions", "Integers"),
        ("Factors", "factors_questions", "Factors"),
    ],
    8: [
        ("Trigonometry", "trigonometry_questions", "Trigonometry"),
        ("Integers", "integers_questions", "Integers"),
        ("Factors", "factors_questions", "Factors"),
    ],
}

JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json_questions")


def topic_name_to_slug(topic_name):
    """
    Convert a topic name to a filename-safe slug.

    Examples:
        "Measurements" -> "measurements"
        "Place Values" -> "place-values"
        "BODMAS/PEMDAS" -> "bodmas-pemdas"
        "Date and Time" -> "date-and-time"
        "Whole Numbers" -> "whole-numbers"
    """
    slug = topic_name.lower()
    slug = slug.replace("/", "-")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


def get_json_filename(year, topic_name):
    """
    Get the expected JSON filename for a year-topic combination.

    Args:
        year: Year number (e.g. 2, 3, 4, ...)
        topic_name: Topic name (e.g. "Measurements", "BODMAS/PEMDAS")

    Returns:
        Filename string like "2-measurements.json"
    """
    slug = topic_name_to_slug(topic_name)
    return f"{year}-{slug}.json"


def get_json_filepath(year, topic_name):
    """Get the full path to a JSON question file."""
    return os.path.join(JSON_DIR, get_json_filename(year, topic_name))


def list_expected_files():
    """
    List all expected JSON files based on YEAR_TOPICS_MAP.

    Returns:
        List of (year, topic_name, filename, exists) tuples
    """
    results = []
    for year, topics in sorted(YEAR_TOPICS_MAP.items()):
        for topic_name, _, _ in topics:
            filename = get_json_filename(year, topic_name)
            filepath = os.path.join(JSON_DIR, filename)
            exists = os.path.exists(filepath)
            results.append((year, topic_name, filename, exists))
    return results


def load_questions_from_json(filepath):
    """
    Load questions from a JSON file.

    Expected JSON format:
    [
        {
            "question_text": "...",
            "question_type": "multiple_choice",  (optional, defaults to "multiple_choice")
            "correct_answer": "...",
            "wrong_answers": ["...", "...", "..."],
            "explanation": "...",  (optional)
            "image_path": "..."   (optional)
        },
        ...
    ]

    Args:
        filepath: Path to the JSON file

    Returns:
        List of question data dictionaries
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array of questions, got {type(data).__name__}"
        )

    questions = []
    for item in data:
        q = {
            "question_text": item.get("question_text", ""),
            "question_type": item.get("question_type", "multiple_choice"),
            "correct_answer": item.get("correct_answer", ""),
            "wrong_answers": item.get("wrong_answers", []),
            "explanation": item.get("explanation", ""),
        }
        if item.get("image_path"):
            q["image_path"] = item["image_path"]
        questions.append(q)

    return questions


def setup_topic_and_level(year, topic_name):
    """
    Get or create the topic and associate it with the year level.

    Args:
        year: Year number (e.g. 2, 3, 4, ...)
        topic_name: Topic name (e.g. "Measurements")

    Returns:
        Tuple of (topic, level) or None if level not found
    """
    topic = Topic.objects.filter(name=topic_name).first()
    if not topic:
        topic = Topic.objects.create(name=topic_name)
        print(f"[OK] Created topic: {topic_name}")
    else:
        print(f"[INFO] Topic already exists: {topic_name}")

    level = Level.objects.filter(level_number=year).first()
    if not level:
        print(f"[ERROR] Year {year} level not found!")
        return None

    print(f"[INFO] Found Year {year}: {level}")

    if level.topics.filter(name=topic_name).exists():
        print(f"[INFO] Year {year} already has {topic_name} topic associated.")
    else:
        level.topics.add(topic)
        print(f"[OK] Associated {topic_name} topic with Year {year}")

    return topic, level


def backfill_topicless_questions(level, topic, questions_data, verbose=True):
    """
    Find existing questions that match by level and question_text but have no
    topic set, and assign the given topic to them.

    This prevents duplicates when questions were previously loaded without a
    topic and ensures they are picked up by topic-based filtering in views.

    Args:
        level: Level object
        topic: Topic object
        questions_data: List of question data dicts (from JSON)
        verbose: Print status messages

    Returns:
        Number of questions backfilled
    """
    question_texts = [q.get("question_text", "").strip() for q in questions_data]
    question_texts = [t for t in question_texts if t]

    topicless = Question.objects.filter(
        level=level,
        topic__isnull=True,
        question_text__in=question_texts,
    )

    count = topicless.count()
    if count == 0:
        if verbose:
            print(f"[INFO] No topicless questions to backfill for this level.")
        return 0

    if verbose:
        print(f"[BACKFILL] Found {count} question(s) without a topic. Assigning '{topic.name}'...")

    for question in topicless:
        question.topic = topic
        question.save()
        if verbose:
            safe_text = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            print(f"  [BACKFILL] {safe_text}...")

    if verbose:
        print(f"[BACKFILL] Assigned topic to {count} existing question(s).")

    return count


def process_json_file(filepath, verbose=True):
    """
    Load questions from a JSON file and add them to the database.

    The year and topic are derived from the filename convention: <year>-<topic-slug>.json

    Args:
        filepath: Path to the JSON file
        verbose: Print status messages

    Returns:
        Dictionary with counts: {'created': int, 'updated': int, 'skipped': int}
        or None on error
    """
    filename = os.path.basename(filepath)

    year, topic_name = resolve_year_topic_from_filename(filename)
    if year is None or topic_name is None:
        print(f"[ERROR] Could not determine year/topic from filename: {filename}")
        return None

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Processing: Year {year} - {topic_name}")
        print(f"File: {filename}")
        print(f"{'=' * 60}")

    questions_data = load_questions_from_json(filepath)
    if not questions_data:
        if verbose:
            print(f"[INFO] No questions found in {filename}")
        return {"created": 0, "updated": 0, "skipped": 0}

    result = setup_topic_and_level(year, topic_name)
    if result is None:
        return None

    topic, level = result

    backfill_count = backfill_topicless_questions(
        level=level,
        topic=topic,
        questions_data=questions_data,
        verbose=verbose,
    )

    results = process_questions(
        level=level,
        topic=topic,
        questions_data=questions_data,
        verbose=verbose,
    )
    results['backfilled'] = backfill_count

    if verbose:
        print(f"\n[OK] Completed Year {year} - {topic_name}")

    return results


def resolve_year_topic_from_filename(filename):
    """
    Resolve year number and topic name from a JSON filename.

    Uses YEAR_TOPICS_MAP to match the slug back to the original topic name.

    Args:
        filename: e.g. "2-measurements.json"

    Returns:
        Tuple of (year, topic_name) or (None, None) if not matched
    """
    name = filename.replace(".json", "")
    match = re.match(r"^(\d+)-(.+)$", name)
    if not match:
        return None, None

    year = int(match.group(1))
    slug = match.group(2)

    if year not in YEAR_TOPICS_MAP:
        print(f"[ERROR] Year {year} not found in YEAR_TOPICS_MAP")
        return None, None

    for topic_name, _, _ in YEAR_TOPICS_MAP[year]:
        if topic_name_to_slug(topic_name) == slug:
            return year, topic_name

    print(f"[ERROR] No topic matching slug '{slug}' for Year {year}")
    return None, None


def process_all(verbose=True):
    """
    Process all JSON files that exist in the json_questions directory.

    Returns:
        Dictionary with total counts
    """
    total = {"created": 0, "updated": 0, "skipped": 0, "backfilled": 0, "errors": 0}

    for year, topic_name, filename, exists in list_expected_files():
        if not exists:
            if verbose:
                print(f"[SKIP] {filename} not found, skipping...")
            continue

        filepath = os.path.join(JSON_DIR, filename)
        result = process_json_file(filepath, verbose=verbose)

        if result is None:
            total["errors"] += 1
        else:
            total["created"] += result.get("created", 0)
            total["updated"] += result.get("updated", 0)
            total["skipped"] += result.get("skipped", 0)
            total["backfilled"] += result.get("backfilled", 0)

    return total


def process_year(year, verbose=True):
    """
    Process all JSON files for a specific year.

    Args:
        year: Year number

    Returns:
        Dictionary with total counts
    """
    if year not in YEAR_TOPICS_MAP:
        print(f"[ERROR] Year {year} not in YEAR_TOPICS_MAP")
        return None

    total = {"created": 0, "updated": 0, "skipped": 0, "backfilled": 0, "errors": 0}

    for topic_name, _, _ in YEAR_TOPICS_MAP[year]:
        filepath = get_json_filepath(year, topic_name)
        if not os.path.exists(filepath):
            if verbose:
                filename = get_json_filename(year, topic_name)
                print(f"[SKIP] {filename} not found, skipping...")
            continue

        result = process_json_file(filepath, verbose=verbose)

        if result is None:
            total["errors"] += 1
        else:
            total["created"] += result.get("created", 0)
            total["updated"] += result.get("updated", 0)
            total["skipped"] += result.get("skipped", 0)
            total["backfilled"] += result.get("backfilled", 0)

    return total


def main():
    parser = argparse.ArgumentParser(
        description="Add/update questions from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_questions_from_json.py --file 2-measurements.json
  python add_questions_from_json.py --year 2
  python add_questions_from_json.py --all
  python add_questions_from_json.py --list
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Process a specific JSON file (name or full path)",
    )
    group.add_argument(
        "--year", "-y",
        type=int,
        help="Process all JSON files for a specific year",
    )
    group.add_argument(
        "--all", "-a",
        action="store_true",
        help="Process all JSON files for all years",
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all expected JSON files and their status",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Show verbose output (default: True)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()
    verbose = not args.quiet

    if args.list:
        print(f"\nExpected JSON files (directory: {JSON_DIR}):\n")
        print(f"{'Year':<6} {'Topic':<20} {'Filename':<30} {'Status':<10}")
        print("-" * 66)
        for year, topic_name, filename, exists in list_expected_files():
            status = "EXISTS" if exists else "MISSING"
            print(f"{year:<6} {topic_name:<20} {filename:<30} {status:<10}")
        return

    if args.file:
        if os.path.isabs(args.file):
            filepath = args.file
        elif os.path.exists(os.path.join(JSON_DIR, args.file)):
            filepath = os.path.join(JSON_DIR, args.file)
        else:
            filepath = args.file

        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            sys.exit(1)

        result = process_json_file(filepath, verbose=verbose)
        if result is None:
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"RESULTS: Created={result['created']}, "
              f"Updated={result['updated']}, Skipped={result['skipped']}, "
              f"Backfilled={result.get('backfilled', 0)}")
        return

    if args.year:
        result = process_year(args.year, verbose=verbose)
        if result is None:
            sys.exit(1)
    elif args.all:
        result = process_all(verbose=verbose)

    print(f"\n{'=' * 60}")
    print("TOTAL RESULTS")
    print(f"{'=' * 60}")
    print(f"  Created: {result['created']}")
    print(f"  Updated: {result['updated']}")
    print(f"  Skipped: {result['skipped']}")
    if result.get('backfilled', 0) > 0:
        print(f"  Backfilled: {result['backfilled']}")
    if result.get("errors", 0) > 0:
        print(f"  Errors: {result['errors']}")


if __name__ == "__main__":
    main()
