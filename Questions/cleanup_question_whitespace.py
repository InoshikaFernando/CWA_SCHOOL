#!/usr/bin/env python
"""
Clean up whitespace in question_text fields in the database
Removes tabs, extra spaces, and normalizes spacing
"""
import os
import sys
import django
import re

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question

def normalize_whitespace(text):
    """
    Normalize whitespace in text:
    - Replace tabs with spaces
    - Replace multiple spaces with single space
    - Strip leading/trailing whitespace
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Strip leading and trailing whitespace
    text = text.strip()
    return text

def cleanup_questions():
    """Clean whitespace from all questions in database"""
    
    print("[INFO] Starting whitespace cleanup on Question database...\n")
    
    all_questions = Question.objects.all()
    total_count = all_questions.count()
    updated_count = 0
    unchanged_count = 0
    
    print(f"[INFO] Found {total_count} questions to check\n")
    
    for question in all_questions:
        original_text = question.question_text
        cleaned_text = normalize_whitespace(original_text)
        
        if original_text != cleaned_text:
            # Question text changed, update it
            question.question_text = cleaned_text
            question.save()
            updated_count += 1
            
            safe_original = original_text[:50].encode('ascii', 'ignore').decode('ascii')
            safe_cleaned = cleaned_text[:50].encode('ascii', 'ignore').decode('ascii')
            print(f"  [UPDATE] Question ID {question.id}")
            print(f"    Before:  {safe_original}...")
            print(f"    After:   {safe_cleaned}...")
        else:
            unchanged_count += 1
    
    print(f"\n[SUMMARY]")
    print(f"   Total questions checked: {total_count}")
    print(f"   Updated: {updated_count} questions")
    print(f"   Unchanged: {unchanged_count} questions")
    print(f"\n[OK] Whitespace cleanup complete!")

if __name__ == "__main__":
    print("[INFO] Question Whitespace Cleanup Tool\n")
    print("="*60)
    
    try:
        cleanup_questions()
        print("\n[OK] Done!")
    except Exception as e:
        print(f"\n[ERROR] Failed to cleanup questions: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
