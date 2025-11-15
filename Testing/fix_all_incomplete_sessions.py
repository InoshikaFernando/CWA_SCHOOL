#!/usr/bin/env python
"""
Fix incomplete sessions for all students, all topics, and all levels
This will merge incomplete sessions without deleting them
"""
import os
import sys
import django

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, StudentAnswer
from django.db.models import Count
import importlib.util
import sys

# Import fix_incomplete_sessions function
spec = importlib.util.spec_from_file_location("fix_incomplete_sessions", 
                                               os.path.join(os.path.dirname(__file__), "fix_incomplete_sessions.py"))
fix_module = importlib.util.module_from_spec(spec)
sys.modules["fix_incomplete_sessions"] = fix_module
spec.loader.exec_module(fix_module)
fix_incomplete_sessions = fix_module.fix_incomplete_sessions

def fix_all_incomplete_sessions(dry_run=True):
    """
    Fix incomplete sessions for all level-topic combinations
    """
    print("=" * 100)
    print("FIXING INCOMPLETE SESSIONS FOR ALL STUDENTS")
    print("=" * 100)
    print()
    
    if dry_run:
        print("[DRY RUN MODE] - No changes will be made")
        print()
    
    # Get all levels (year levels, not Basic Facts)
    year_levels = Level.objects.filter(level_number__lt=100).order_by('level_number')
    
    # Get all topics
    topics = Topic.objects.all().order_by('name')
    
    print(f"[INFO] Found {year_levels.count()} year levels")
    print(f"[INFO] Found {topics.count()} topics")
    print()
    
    # Find level-topic combinations that have student answers
    level_topic_combinations = []
    
    for level in year_levels:
        for topic in topics:
            # Check if there are any answers for this level-topic combination
            answer_count = StudentAnswer.objects.filter(
                question__level=level,
                question__topic=topic
            ).exclude(session_id='').count()
            
            if answer_count > 0:
                level_topic_combinations.append((level.level_number, topic.name, answer_count))
    
    print(f"[INFO] Found {len(level_topic_combinations)} level-topic combinations with answers")
    print()
    
    if not level_topic_combinations:
        print("[INFO] No level-topic combinations found with answers")
        return
    
    # Process each combination
    total_merged = 0
    total_deleted = 0
    total_kept = 0
    
    for level_number, topic_name, answer_count in level_topic_combinations:
        print("\n" + "=" * 100)
        print(f"PROCESSING: Year {level_number} - {topic_name} ({answer_count} answers)")
        print("=" * 100)
        print()
        
        # Call the fix function
        # Note: We can't easily get the return values, so we'll just run it
        # The function will print its own summary
        try:
            fix_incomplete_sessions(
                level_number=level_number,
                topic_name=topic_name,
                merge_sessions=True,
                dry_run=dry_run,
                keep_partial=True,
                partial_threshold=0.9,
                delete_incomplete=False  # Don't delete, just merge and keep
            )
        except Exception as e:
            print(f"[ERROR] Failed to process Year {level_number} - {topic_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 100)
    print("ALL PROCESSING COMPLETE")
    print("=" * 100)
    print()
    if dry_run:
        print("[DRY RUN] - No changes were made")
        print()
        print("To apply changes, run with --execute flag:")
        print("  python Testing/fix_all_incomplete_sessions.py --execute")
    else:
        print("[OK] All incomplete sessions have been processed")
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix incomplete sessions for all students, all topics, and all levels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be done)
  python Testing/fix_all_incomplete_sessions.py
  
  # Actually fix all incomplete sessions
  python Testing/fix_all_incomplete_sessions.py --execute
        """
    )
    parser.add_argument('--execute', action='store_true',
                       help='Actually make changes (default: dry run)')
    
    args = parser.parse_args()
    
    fix_all_incomplete_sessions(dry_run=not args.execute)

