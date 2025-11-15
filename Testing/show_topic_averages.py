#!/usr/bin/env python
"""
Display average points for each topic-level combination in a clean format
"""
import os
import sys
import django

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import TopicLevelStatistics, Level, Topic
from django.db.models import Avg, Count

def show_topic_averages():
    """Display average points for each topic"""
    
    print("=" * 100)
    print("AVERAGE POINTS BY TOPIC AND LEVEL")
    print("=" * 100)
    print()
    
    # Get all statistics, ordered by level and topic
    stats = TopicLevelStatistics.objects.select_related('level', 'topic').order_by(
        'level__level_number', 'topic__name'
    )
    
    if not stats.exists():
        print("No statistics found. Run calculate_topic_statistics.py first.")
        return
    
    # Group by topic to show overall averages
    print("BY TOPIC (across all levels):")
    print("-" * 100)
    print(f"{'Topic':<30} {'Levels':<10} {'Total Students':<15} {'Avg Points':<15} {'Sigma':<15}")
    print("-" * 100)
    
    # Group by topic
    from collections import defaultdict
    topic_data = defaultdict(lambda: {'levels': set(), 'students': 0, 'points': [], 'sigmas': []})
    
    for stat in stats:
        topic_name = stat.topic.name if stat.topic else "Unknown"
        level_num = stat.level.level_number if stat.level else 0
        topic_data[topic_name]['levels'].add(level_num)
        topic_data[topic_name]['students'] += stat.student_count
        if stat.student_count > 0:
            topic_data[topic_name]['points'].append(float(stat.average_points))
            topic_data[topic_name]['sigmas'].append(float(stat.sigma))
    
    for topic_name in sorted(topic_data.keys()):
        data = topic_data[topic_name]
        levels_str = f"{len(data['levels'])} level(s)"
        total_students = data['students']
        
        if data['points']:
            # Weighted average (weighted by student count)
            avg_points = sum(data['points']) / len(data['points']) if data['points'] else 0
            avg_sigma = sum(data['sigmas']) / len(data['sigmas']) if data['sigmas'] else 0
        else:
            avg_points = 0
            avg_sigma = 0
        
        print(f"{topic_name:<30} {levels_str:<10} {total_students:<15} {avg_points:<15.2f} {avg_sigma:<15.2f}")
    
    print()
    print("=" * 100)
    print("BY LEVEL AND TOPIC (detailed):")
    print("-" * 100)
    print(f"{'Year':<8} {'Topic':<30} {'Avg Points':<15} {'Sigma':<15} {'Students':<10} {'Status':<20}")
    print("-" * 100)
    
    for stat in stats:
        level_num = stat.level.level_number if stat.level else 0
        topic_name = stat.topic.name if stat.topic else "Unknown"
        avg_points = float(stat.average_points)
        sigma = float(stat.sigma)
        student_count = stat.student_count
        
        # Determine status
        if student_count == 0:
            status = "No data"
        elif student_count == 1:
            status = "Insufficient data"
        elif sigma == 0:
            status = "No variance"
        else:
            status = "Active"
        
        year_label = f"Year {level_num}" if level_num < 100 else f"Level {level_num}"
        print(f"{year_label:<8} {topic_name:<30} {avg_points:<15.2f} {sigma:<15.2f} {student_count:<10} {status:<20}")
    
    print("-" * 100)
    print()
    
    # Summary statistics
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total topic-level combinations: {stats.count()}")
    
    active_stats = stats.filter(student_count__gte=2)
    print(f"Active combinations (2+ students): {active_stats.count()}")
    
    if active_stats.exists():
        overall_avg = sum(float(s.average_points) for s in active_stats) / active_stats.count()
        print(f"Overall average (across all active topics): {overall_avg:.2f} points")
    
    print()

if __name__ == "__main__":
    show_topic_averages()
