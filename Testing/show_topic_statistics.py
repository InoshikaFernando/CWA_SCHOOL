#!/usr/bin/env python
"""
Display all records from maths_topiclevelstatistics table.
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import TopicLevelStatistics

def show_topic_statistics():
    """Display all topic-level statistics"""
    
    print("=" * 120)
    print("TOPIC-LEVEL STATISTICS")
    print("=" * 120)
    print()
    
    stats = TopicLevelStatistics.objects.select_related('level', 'topic').order_by('level__level_number', 'topic__name')
    
    if not stats.exists():
        print("No statistics found in the database.")
        return
    
    print(f"Total records: {stats.count()}")
    print()
    print("-" * 120)
    print(f"{'ID':<5} {'Level':<15} {'Topic':<30} {'Avg Points':<12} {'Sigma':<12} {'Students':<10} {'Last Updated':<20}")
    print("-" * 120)
    
    for stat in stats:
        level_name = f"{stat.level.level_number} ({stat.level.title})" if stat.level else "N/A"
        topic_name = stat.topic.name if stat.topic else "N/A"
        avg_points = float(stat.average_points)
        sigma = float(stat.sigma)
        student_count = stat.student_count
        last_updated = stat.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{stat.id:<5} {level_name:<15} {topic_name:<30} {avg_points:<12.2f} {sigma:<12.2f} {student_count:<10} {last_updated:<20}")
    
    print("-" * 120)
    print()
    
    # Show detailed breakdown
    print("DETAILED BREAKDOWN:")
    print("=" * 120)
    print()
    
    for stat in stats:
        print(f"ID: {stat.id}")
        print(f"  Level: {stat.level.level_number} - {stat.level.title}")
        print(f"  Topic: {stat.topic.name}")
        print(f"  Average Points: {stat.average_points}")
        print(f"  Standard Deviation (sigma): {stat.sigma}")
        print(f"  Student Count: {stat.student_count}")
        print(f"  Last Updated: {stat.last_updated}")
        print()
        
        # Show color coding ranges
        if stat.sigma > 0 and stat.student_count >= 2:
            avg = float(stat.average_points)
            sigma = float(stat.sigma)
            print(f"  Color Coding Ranges:")
            print(f"    Dark Green: > {avg + 2*sigma:.2f} (above avg + 2*sigma)")
            print(f"    Green: {avg + sigma:.2f} to {avg + 2*sigma:.2f} (avg + sigma to avg + 2*sigma)")
            print(f"    Light Green: {avg - sigma:.2f} to {avg + sigma:.2f} (avg - sigma to avg + sigma)")
            print(f"    Yellow: {avg - 2*sigma:.2f} to {avg - sigma:.2f} (avg - 2*sigma to avg - sigma)")
            print(f"    Orange: {avg - 3*sigma:.2f} to {avg - 2*sigma:.2f} (avg - 3*sigma to avg - 2*sigma)")
            print(f"    Red: < {avg - 3*sigma:.2f} (below avg - 3*sigma)")
        else:
            print(f"  Color Coding: Not enough data (needs at least 2 students)")
        print("-" * 120)
        print()

if __name__ == "__main__":
    show_topic_statistics()

