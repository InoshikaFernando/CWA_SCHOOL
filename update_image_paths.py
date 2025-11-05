#!/usr/bin/env python
"""
Update questions that use root-level images to use year6/measurements images instead.

Updates:
- questions/image1.png -> questions/year6/measurements/image1.png
- questions/image2.png -> questions/year6/measurements/image2.png
- questions/image3.png -> questions/year6/measurements/image3.png
- questions/image5.png -> questions/year6/measurements/image5.png
- questions/image7.png -> questions/year6/measurements/image7.png
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from maths.models import Question

# Map of old paths to new paths
image_mappings = {
    'questions/image1.png': 'questions/year6/measurements/image1.png',
    'questions/image2.png': 'questions/year6/measurements/image2.png',
    'questions/image3.png': 'questions/year6/measurements/image3.png',
    'questions/image5.png': 'questions/year6/measurements/image5.png',
    'questions/image7.png': 'questions/year6/measurements/image7.png',
}

print("🔄 Updating image paths from root-level to year6/measurements...\n")

total_updated = 0

for old_path, new_path in image_mappings.items():
    # Find all questions using the old path
    questions_with_images = Question.objects.filter(image__isnull=False)
    questions_to_update = [q for q in questions_with_images if q.image and q.image.name == old_path]
    
    if questions_to_update:
        print(f"📷 {os.path.basename(old_path)}:")
        print(f"   Found {len(questions_to_update)} question(s) using old path: {old_path}")
        
        # Check if new image file exists
        new_file_path = os.path.join('media', new_path)
        if not os.path.exists(new_file_path):
            print(f"   ⚠️  WARNING: New image file not found: {new_file_path}")
            print(f"   ⏭️  Skipping this image...")
            continue
        
        # Update each question
        for question in questions_to_update:
            # Update the image path
            question.image.name = new_path
            question.save(update_fields=['image'])
            print(f"   ✅ Updated Question ID {question.id} (Level {question.level.level_number})")
        
        total_updated += len(questions_to_update)
        print()
    else:
        print(f"📷 {os.path.basename(old_path)}: No questions using this image\n")

print(f"📊 Summary:")
print(f"   ✅ Updated: {total_updated} question(s)")
print(f"   🗑️  You can now delete the old root-level images if desired")

