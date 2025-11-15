#!/usr/bin/env python
"""
Script to count students in the database
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import CustomUser

def count_students():
    """Count students in the database"""
    
    # Count all users
    total_users = CustomUser.objects.count()
    
    # Count teachers (is_teacher=True)
    teachers = CustomUser.objects.filter(is_teacher=True).count()
    
    # Count students (is_teacher=False or None)
    students = CustomUser.objects.filter(is_teacher=False).count()
    
    # Count active students
    active_students = CustomUser.objects.filter(is_teacher=False, is_active=True).count()
    
    # Count inactive students
    inactive_students = CustomUser.objects.filter(is_teacher=False, is_active=False).count()
    
    print("=" * 80)
    print("STUDENT COUNT REPORT")
    print("=" * 80)
    print(f"\n[INFO] Total Users: {total_users}")
    print(f"[INFO] Teachers: {teachers}")
    print(f"[INFO] Students: {students}")
    print(f"   - Active: {active_students}")
    print(f"   - Inactive: {inactive_students}")
    print("\n" + "=" * 80)
    
    # Optional: Show breakdown by enrollment status
    from maths.models import Enrollment
    enrolled_students = Enrollment.objects.values('student').distinct().count()
    individual_students = students - enrolled_students
    
    print(f"\n[INFO] Enrollment Breakdown:")
    print(f"   - Enrolled in classes: {enrolled_students}")
    print(f"   - Individual students: {individual_students}")
    print("=" * 80)
    
    return students

if __name__ == "__main__":
    count_students()

