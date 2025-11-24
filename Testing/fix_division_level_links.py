"""
Script to fix Division level links - unlink levels 130-139 from Division topic
if they have no questions, since questions are only in 121-127.
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

def fix_division_level_links(dry_run=True):
    """
    Unlink levels 130-139 from Division topic if they have no Division questions.
    These levels should not appear on the website if they're empty.
    """
    print("=" * 100)
    if dry_run:
        print("FIXING DIVISION LEVEL LINKS (DRY RUN)")
    else:
        print("FIXING DIVISION LEVEL LINKS")
    print("=" * 100)
    
    # Get Division topic
    division_topic = Topic.objects.filter(name="Division").first()
    if not division_topic:
        print("\n[ERROR] Division topic not found")
        return
    
    print(f"\nDivision Topic: {division_topic.name} (ID: {division_topic.id})")
    
    # Get all levels linked to Division topic
    all_division_levels = Level.objects.filter(
        topics=division_topic
    ).order_by('level_number')
    
    print(f"\nTotal levels linked to Division topic: {all_division_levels.count()}")
    
    # Check levels 130-139 specifically
    levels_130_139 = Level.objects.filter(
        topics=division_topic,
        level_number__gte=130,
        level_number__lte=139
    ).order_by('level_number')
    
    print(f"\nLevels 130-139 linked to Division: {levels_130_139.count()}")
    
    if levels_130_139.count() == 0:
        print("\n[OK] No levels 130-139 are linked to Division topic")
        print("This is correct - only levels 121-127 should be linked to Division.")
        return
    
    print(f"\n{'=' * 100}")
    print("LEVELS 130-139 LINKED TO DIVISION (SHOULD BE UNLINKED)")
    print(f"{'=' * 100}")
    print(f"\n{'Level #':<12} {'Title':<50} {'Questions':<12} {'Div Qs':<12} {'Action':<30}")
    print("-" * 100)
    
    levels_to_unlink = []
    
    for level in levels_130_139:
        total_questions = level.questions.count()
        division_questions = level.questions.filter(topic=division_topic).count()
        
        # Check what other topics this level is linked to
        other_topics = [t.name for t in level.topics.all() if t.name != "Division"]
        
        action = ""
        if total_questions == 0:
            action = "Unlink from Division (no questions)"
            levels_to_unlink.append((level, "no_questions"))
        elif division_questions == 0:
            action = "Unlink from Division (no Division questions)"
            levels_to_unlink.append((level, "no_division_questions"))
        else:
            action = "Keep linked (has Division questions)"
        
        print(f"{level.level_number:<12} {level.title[:48]:<50} {total_questions:<12} {division_questions:<12} {action:<30}")
        if other_topics:
            print(f"            Also linked to: {', '.join(other_topics)}")
    
    if not levels_to_unlink:
        print("\n[OK] No levels need to be unlinked")
        return
    
    print(f"\n{'=' * 100}")
    print("SUMMARY OF CHANGES")
    print(f"{'=' * 100}")
    print(f"Levels to unlink from Division: {len(levels_to_unlink)}")
    
    for level, reason in levels_to_unlink:
        print(f"  - Level {level.level_number}: {level.title} (Reason: {reason})")
    
    if not dry_run:
        print(f"\n{'=' * 100}")
        print("UNLINKING LEVELS FROM DIVISION TOPIC")
        print(f"{'=' * 100}")
        
        unlinked_count = 0
        for level, reason in levels_to_unlink:
            level.topics.remove(division_topic)
            unlinked_count += 1
            print(f"[UNLINKED] Level {level.level_number} from Division topic")
        
        print(f"\n[SUCCESS] Unlinked {unlinked_count} levels from Division topic")
        
        # Verify
        remaining = Level.objects.filter(
            topics=division_topic,
            level_number__gte=130,
            level_number__lte=139
        ).count()
        
        if remaining == 0:
            print("[OK] No levels 130-139 are now linked to Division")
        else:
            print(f"[WARNING] {remaining} levels 130-139 are still linked to Division")
    else:
        print(f"\n[DRY RUN] Would unlink {len(levels_to_unlink)} levels from Division topic")
        print("Run with --execute to apply changes")
    
    # Show final state
    print(f"\n{'=' * 100}")
    print("FINAL STATE")
    print(f"{'=' * 100}")
    
    final_division_levels = Level.objects.filter(
        topics=division_topic
    ).order_by('level_number')
    
    print(f"\nTotal levels linked to Division topic: {final_division_levels.count()}")
    for level in final_division_levels:
        div_q = level.questions.filter(topic=division_topic).count()
        print(f"  - Level {level.level_number}: {level.title} ({div_q} Division questions)")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fix Division level topic links')
    parser.add_argument('--execute', action='store_true', help='Actually update the database (default is dry-run)')
    args = parser.parse_args()
    
    fix_division_level_links(dry_run=not args.execute)

