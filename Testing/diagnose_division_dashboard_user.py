"""
Diagnose why Division results aren't showing on dashboard for a specific user.
Simulates the exact dashboard_detail query logic.
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Level, Topic, BasicFactsResult, CustomUser
import argparse

def diagnose_division_dashboard(username=None):
    """
    Diagnose Division dashboard display for a specific user.
    """
    print("=" * 100)
    print("DIAGNOSING DIVISION DASHBOARD DISPLAY")
    print("=" * 100)
    
    # Get user
    if username:
        try:
            user = CustomUser.objects.get(username=username)
            print(f"\nChecking for user: {user.username}")
        except CustomUser.DoesNotExist:
            print(f"\n[ERROR] User '{username}' not found")
            return
    else:
        # Get first user with Division results
        division_results = BasicFactsResult.objects.filter(
            level__level_number__gte=121,
            level__level_number__lte=127
        ).select_related('student').first()
        
        if not division_results:
            print("\n[ERROR] No Division results found for any user")
            return
        
        user = division_results.student
        print(f"\nChecking for user: {user.username} (first user with Division results)")
    
    # Simulate dashboard_detail logic
    print(f"\n{'=' * 100}")
    print("SIMULATING DASHBOARD_DETAIL VIEW LOGIC")
    print(f"{'=' * 100}")
    
    # Get Basic Facts levels (>= 100)
    basic_facts_levels = Level.objects.filter(level_number__gte=100)
    
    # Group Basic Facts levels by subtopic (same as dashboard_detail)
    basic_facts_by_subtopic = {}
    for level in basic_facts_levels:
        subtopics = level.topics.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division', 'Place Value Facts'])
        if subtopics.exists():
            subtopic_name = subtopics.first().name
            if subtopic_name not in basic_facts_by_subtopic:
                basic_facts_by_subtopic[subtopic_name] = []
            basic_facts_by_subtopic[subtopic_name].append(level)
    
    # Sort Basic Facts levels within each subtopic
    for subtopic in basic_facts_by_subtopic:
        basic_facts_by_subtopic[subtopic].sort(key=lambda x: x.level_number)
    
    print(f"\nBasic Facts subtopics found: {list(basic_facts_by_subtopic.keys())}")
    
    # Check Division specifically
    if 'Division' not in basic_facts_by_subtopic:
        print("\n[ISSUE] 'Division' not found in basic_facts_by_subtopic!")
        print("This means Division levels are not linked to Division topic correctly.")
        return
    
    division_levels = basic_facts_by_subtopic['Division']
    print(f"\nDivision levels found: {len(division_levels)}")
    for level in division_levels:
        print(f"  - Level {level.level_number}: {level.title}")
    
    # Simulate the progress calculation (same as dashboard_detail)
    print(f"\n{'=' * 100}")
    print("CHECKING BASIC FACTS PROGRESS FOR DIVISION")
    print(f"{'=' * 100}")
    
    basic_facts_progress = {}
    
    # Process Division subtopic
    subtopic_name = 'Division'
    if subtopic_name in basic_facts_by_subtopic:
        levels = basic_facts_by_subtopic[subtopic_name]
        basic_facts_progress[subtopic_name] = []
        
        print(f"\nProcessing {len(levels)} Division levels:")
        
        for level in levels:
            level_num = level.level_number
            
            # This is the exact query from dashboard_detail
            db_results = BasicFactsResult.objects.filter(
                student=user,
                level=level
            ).order_by('-points')
            
            print(f"\n  Level {level_num} (displays as Level {level_num - 120}):")
            print(f"    Query: BasicFactsResult.objects.filter(student={user.username}, level={level_num})")
            print(f"    Results found: {db_results.count()}")
            
            if db_results.exists():
                best_result = db_results.first()
                display_level = level_num - 120
                
                total_attempts = db_results.values('session_id').distinct().count()
                
                print(f"    [OK] Results exist - will be added to dashboard")
                print(f"      Best points: {best_result.points}")
                print(f"      Best score: {best_result.score}/{best_result.total_points}")
                print(f"      Time: {best_result.time_taken_seconds}s")
                print(f"      Attempts: {total_attempts}")
                
                # This is what gets added to basic_facts_progress
                progress_entry = {
                    'display_level': display_level,
                    'level_number': level_num,
                    'best_points': float(best_result.points),
                    'best_time_seconds': best_result.time_taken_seconds,
                    'best_date': best_result.completed_at,
                    'total_attempts': total_attempts,
                    'color_class': 'light-green'  # Default
                }
                basic_facts_progress[subtopic_name].append(progress_entry)
            else:
                print(f"    [ISSUE] No results found - won't appear on dashboard")
                print(f"      Check if user has completed this level")
    
    # Summary
    print(f"\n{'=' * 100}")
    print("SUMMARY")
    print(f"{'=' * 100}")
    
    if 'Division' in basic_facts_progress:
        division_progress = basic_facts_progress['Division']
        print(f"\nDivision progress entries: {len(division_progress)}")
        
        if len(division_progress) > 0:
            print("\nThese should appear on the dashboard:")
            for entry in division_progress:
                print(f"  - Level {entry['display_level']}: {entry['best_points']} points")
            print("\n[OK] Division results should be visible on dashboard")
        else:
            print("\n[ISSUE] No Division progress entries - won't show on dashboard")
            print("Reason: No BasicFactsResult records found for this user's Division levels")
    else:
        print("\n[ISSUE] 'Division' not in basic_facts_progress dictionary")
        print("This means no results were found for any Division level")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diagnose Division dashboard display for a user')
    parser.add_argument('--username', type=str, help='Username to check (optional, uses first user with results if not provided)')
    args = parser.parse_args()
    
    diagnose_division_dashboard(username=args.username)

