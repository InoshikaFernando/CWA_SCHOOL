#!/usr/bin/env python
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Topic, Level

# Create topics
topics_data = [
    "Number Patterns",
    "Measurements", 
    "Time",
    "Algebra",
    "Fractions",
    "Geometry",
    "Statistics",
    "Probability"
]

# Create topics
for i, topic_name in enumerate(topics_data, 1):
    topic, created = Topic.objects.get_or_create(name=topic_name)
    print(f"{'Created' if created else 'Found'} topic: {topic_name}")

# Create levels for each topic (Year 1-8)
level_titles = {
    "Number Patterns": [
        "Year 1: Counting patterns",
        "Year 2: Skip counting", 
        "Year 3: Number sequences",
        "Year 4: Arithmetic sequences",
        "Year 5: Geometric sequences",
        "Year 6: Complex patterns",
        "Year 7: Algebraic patterns",
        "Year 8: Advanced sequences"
    ],
    "Measurements": [
        "Year 1: Length and height",
        "Year 2: Weight and capacity",
        "Year 3: Perimeter and area", 
        "Year 4: Volume and surface area",
        "Year 5: Metric conversions",
        "Year 6: Imperial measurements",
        "Year 7: Scale and proportion",
        "Year 8: Advanced measurements"
    ],
    "Time": [
        "Year 1: Reading clocks",
        "Year 2: Time intervals",
        "Year 3: Elapsed time",
        "Year 4: Calendar and dates",
        "Year 5: Time zones", 
        "Year 6: Timetables",
        "Year 7: Speed and distance",
        "Year 8: Advanced time problems"
    ],
    "Algebra": [
        "Year 1: Simple expressions",
        "Year 2: Basic equations",
        "Year 3: Solving equations",
        "Year 4: Linear equations",
        "Year 5: Simultaneous equations",
        "Year 6: Quadratic equations", 
        "Year 7: Inequalities",
        "Year 8: Advanced algebra"
    ],
    "Fractions": [
        "Year 1: Understanding fractions",
        "Year 2: Fraction notation",
        "Year 3: Equivalent fractions",
        "Year 4: Adding fractions",
        "Year 5: Subtracting fractions",
        "Year 6: Multiplying fractions",
        "Year 7: Dividing fractions", 
        "Year 8: Mixed operations"
    ],
    "Geometry": [
        "Year 1: Basic shapes",
        "Year 2: 2D shapes",
        "Year 3: 3D shapes",
        "Year 4: Angles",
        "Year 5: Triangles",
        "Year 6: Circles",
        "Year 7: Transformations",
        "Year 8: Coordinate geometry"
    ],
    "Statistics": [
        "Year 1: Counting and sorting",
        "Year 2: Pictograms", 
        "Year 3: Bar charts",
        "Year 4: Line graphs",
        "Year 5: Mean and median",
        "Year 6: Mode and range",
        "Year 7: Scatter plots",
        "Year 8: Advanced statistics"
    ],
    "Probability": [
        "Year 1: Certain and impossible",
        "Year 2: Likely and unlikely",
        "Year 3: Probability words",
        "Year 4: Probability fractions",
        "Year 5: Probability decimals",
        "Year 6: Probability percentages",
        "Year 7: Tree diagrams",
        "Year 8: Advanced probability"
    ]
}

# Create levels
for topic_name, titles in level_titles.items():
    topic = Topic.objects.get(name=topic_name)
    for year, title in enumerate(titles, 1):
        level, created = Level.objects.get_or_create(
            topic=topic,
            level_number=year,
            defaults={'title': title}
        )
        print(f"{'Created' if created else 'Found'} level: {title}")

print("\n✅ All topics and levels created successfully!")
print(f"Total topics: {Topic.objects.count()}")
print(f"Total levels: {Level.objects.count()}")
