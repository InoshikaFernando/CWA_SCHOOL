"""
Comprehensive script to fix all Division-related issues:
1. Fix question topics (already done, but verify)
2. Unlink empty levels 130-139 from Division topic
3. Check for duplicate levels
4. Ensure only levels 121-127 with questions are linked to Division
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, Question
from django.db.models import Count

def fix_all_division_issues(dry_run=True):
    """
    Comprehensive fix for all Division-related issues.
    """
    print("=" * 100)
    if dry_run:
        print("FIXING ALL DIVISION ISSUES (DRY RUN)")
    else:
        print("FIXING ALL DIVISION ISSUES")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Step 1: Check for duplicate levels (same level_number)
    print(f"\n{'=' * 100}")
    print("STEP 1: CHECKING FOR DUPLICATE LEVELS")
    print(f"{'=' * 100}")
    
    # Find levels with duplicate level_numbers
    duplicate_levels = Level.objects.values('level_number').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicate_levels.exists():
        print(f"\n[ISSUE] Found {duplicate_levels.count()} level numbers with duplicates:")
        for item in duplicate_levels:
            level_num = item['level_number']
            count = item['count']
            print(f"  Level {level_num}: {count} duplicate levels")
            
            # Show all levels with this number
            levels = Level.objects.filter(level_number=level_num)
            for level in levels:
                linked_topics = [t.name for t in level.topics.all()]
                question_count = level.questions.count()
                print(f"    - ID {level.id}: {level.title}")
                print(f"      Topics: {', '.join(linked_topics)}")
                print(f"      Questions: {question_count}")
    else:
        print("\n[OK] No duplicate level numbers found")
    
    # Step 2: Check all levels linked to Division
    print(f"\n{'=' * 100}")
    print("STEP 2: CHECKING ALL LEVELS LINKED TO DIVISION TOPIC")
    print(f"{'=' * 100}")
    
    all_division_levels = Level.objects.filter(
        topics=division_topic
    ).order_by('level_number')
    
    print(f"\nTotal levels linked to Division: {all_division_levels.count()}")
    
    if all_division_levels.count() > 7:
        print(f"\n[ISSUE] More than 7 levels linked to Division (expected: 121-127 only)")
    
    print(f"\n{'Level #':<12} {'ID':<8} {'Title':<50} {'Questions':<12} {'Div Qs':<12} {'Action':<30}")
    print("-" * 100)
    
    levels_to_unlink = []
    levels_to_keep = []
    
    for level in all_division_levels:
        total_questions = level.questions.count()
        division_questions = level.questions.filter(topic=division_topic).count()
        
        action = ""
        should_unlink = False
        
        if 121 <= level.level_number <= 127:
            if division_questions > 0:
                action = "Keep (correct level with Division questions)"
                levels_to_keep.append(level)
            else:
                action = "Keep but fix questions (correct level, wrong topic)"
                should_unlink = False  # Don't unlink, just fix questions
        elif 130 <= level.level_number <= 139:
            if division_questions == 0:
                action = "Unlink (empty level, questions are in 121-127)"
                levels_to_unlink.append(level)
                should_unlink = True
            else:
                action = "Keep (has Division questions)"
                levels_to_keep.append(level)
        else:
            # Other level numbers
            if division_questions == 0:
                action = "Unlink (wrong level number, no Division questions)"
                levels_to_unlink.append(level)
                should_unlink = True
            else:
                action = "Review (unexpected level number with Division questions)"
        
        print(f"{level.level_number:<12} {level.id:<8} {level.title[:48]:<50} {total_questions:<12} {division_questions:<12} {action:<30}")
    
    # Step 3: Fix question topics in levels 121-127
    print(f"\n{'=' * 100}")
    print("STEP 3: VERIFYING QUESTION TOPICS IN LEVELS 121-127")
    print(f"{'=' * 100}")
    
    levels_121_127 = Level.objects.filter(
        level_number__gte=121,
        level_number__lte=127
    ).order_by('level_number')
    
    questions_to_fix = []
    for level in levels_121_127:
        wrong_topic_questions = level.questions.exclude(topic=division_topic).exclude(topic__isnull=True)
        no_topic_questions = level.questions.filter(topic__isnull=True)
        
        if wrong_topic_questions.exists() or no_topic_questions.exists():
            wrong_count = wrong_topic_questions.count()
            no_topic_count = no_topic_questions.count()
            print(f"Level {level.level_number}: {wrong_count} wrong topic, {no_topic_count} no topic")
            questions_to_fix.extend(list(wrong_topic_questions))
            questions_to_fix.extend(list(no_topic_questions))
    
    if questions_to_fix:
        print(f"\n[ISSUE] {len(questions_to_fix)} questions need topic fix")
        if not dry_run:
            for question in questions_to_fix:
                question.topic = division_topic
                question.save()
            print(f"[FIXED] Updated {len(questions_to_fix)} questions to Division topic")
    else:
        print("\n[OK] All questions in levels 121-127 have correct Division topic")
    
    # Step 4: Unlink empty levels
    print(f"\n{'=' * 100}")
    print("STEP 4: UNLINKING EMPTY LEVELS FROM DIVISION TOPIC")
    print(f"{'=' * 100}")
    
    if levels_to_unlink:
        print(f"\nLevels to unlink: {len(levels_to_unlink)}")
        for level in levels_to_unlink:
            print(f"  - Level {level.level_number} (ID {level.id}): {level.title}")
        
        if not dry_run:
            for level in levels_to_unlink:
                level.topics.remove(division_topic)
            print(f"\n[FIXED] Unlinked {len(levels_to_unlink)} levels from Division topic")
        else:
            print(f"\n[DRY RUN] Would unlink {len(levels_to_unlink)} levels from Division topic")
    else:
        print("\n[OK] No levels need to be unlinked")
    
    # Final summary
    print(f"\n{'=' * 100}")
    print("FINAL SUMMARY")
    print(f"{'=' * 100}")
    
    final_division_levels = Level.objects.filter(
        topics=division_topic
    ).order_by('level_number')
    
    print(f"\nTotal levels linked to Division: {final_division_levels.count()}")
    print("\nLevels that will appear on /basic-facts/Division/:")
    for level in final_division_levels:
        div_q = level.questions.filter(topic=division_topic).count()
        display_level = level.level_number - 120 if 121 <= level.level_number <= 127 else level.level_number
        print(f"  - Level {level.level_number} (displays as Level {display_level}): {div_q} Division questions")
    
    if final_division_levels.count() == 7:
        print("\n[SUCCESS] Exactly 7 Division levels (121-127) - this is correct!")
    elif final_division_levels.count() > 7:
        print(f"\n[WARNING] {final_division_levels.count()} levels linked to Division (expected 7)")
        print("Run with --execute to unlink empty levels")
    else:
        print(f"\n[INFO] {final_division_levels.count()} levels linked to Division")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fix all Division-related issues')
    parser.add_argument('--execute', action='store_true', help='Actually update the database (default is dry-run)')
    args = parser.parse_args()
    
    fix_all_division_issues(dry_run=not args.execute)

