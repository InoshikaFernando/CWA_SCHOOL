#!/usr/bin/env python
"""
Delete invalid image files from the media/questions/ directory
Invalid images are those that:
1. Are directly under questions/ instead of questions/year*/<topic>/
2. Don't follow the pattern questions/year*/<topic>/filename.ext
3. Optionally: Are not referenced by any questions (orphaned files)

WARNING: This will permanently delete image files from the filesystem
"""
import os
import sys
import django
import re
from pathlib import Path

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.conf import settings
from maths.models import Question

def is_valid_image_path(relative_path):
    """
    Check if image path is valid
    Valid: questions/year6/measurements/image1.png (year*/topic/filename)
    Invalid: questions/image1.png (directly under questions/)
    Invalid: questions/year6/image1.png (missing topic subdirectory)
    """
    if not relative_path:
        return False
    
    # Normalize path separators
    relative_path = relative_path.replace('\\', '/')
    
    # Valid pattern: questions/year*/topic/filename.ext
    # Must have at least: questions/year*/topic/filename
    valid_pattern = r'^questions/year\d+/[^/]+/[^/]+$'
    
    return bool(re.match(valid_pattern, relative_path))

def get_all_image_files(media_root):
    """
    Get all image files in media/questions/ directory
    Returns list of (full_path, relative_path) tuples
    """
    questions_dir = os.path.join(media_root, 'questions')
    
    if not os.path.exists(questions_dir):
        return []
    
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
    image_files = []
    
    for root, dirs, files in os.walk(questions_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                full_path = os.path.join(root, file)
                # Get relative path from media_root
                relative_path = os.path.relpath(full_path, media_root)
                # Normalize separators
                relative_path = relative_path.replace('\\', '/')
                image_files.append((full_path, relative_path))
    
    return image_files

def get_referenced_image_paths():
    """
    Get all image paths that are referenced by questions in the database
    Returns a set of normalized relative paths
    """
    referenced = set()
    
    questions_with_images = Question.objects.exclude(
        image__isnull=True
    ).exclude(
        image=''
    ).values_list('image', flat=True)
    
    for image_path in questions_with_images:
        if image_path:
            # Normalize path
            normalized = image_path.replace('\\', '/')
            referenced.add(normalized)
    
    return referenced

def delete_invalid_image_files(dry_run=True, delete_orphaned=False):
    """
    Delete invalid image files
    
    Args:
        dry_run: If True, only show what would be deleted without making changes
        delete_orphaned: If True, also delete valid images that aren't referenced by any questions
    """
    
    print("=" * 80)
    if dry_run:
        print("DRY RUN MODE - No image files will be deleted")
    else:
        print("EXECUTION MODE - Image files WILL BE DELETED")
    print("=" * 80)
    print()
    
    media_root = str(settings.MEDIA_ROOT)
    print(f"[INFO] Scanning media directory: {media_root}")
    print(f"[INFO] Looking for invalid image files in: {os.path.join(media_root, 'questions')}\n")
    
    # Get all image files
    all_image_files = get_all_image_files(media_root)
    
    if not all_image_files:
        print("[OK] No image files found in media/questions/")
        return
    
    print(f"[INFO] Found {len(all_image_files)} image file(s) total\n")
    
    # Get referenced image paths if checking for orphaned files
    referenced_paths = set()
    if delete_orphaned:
        print("[INFO] Checking which images are referenced by questions...")
        referenced_paths = get_referenced_image_paths()
        print(f"[INFO] Found {len(referenced_paths)} image(s) referenced by questions\n")
    
    # Categorize images
    invalid_images = []
    orphaned_images = []
    valid_images = []
    
    for full_path, relative_path in all_image_files:
        if not is_valid_image_path(relative_path):
            invalid_images.append((full_path, relative_path))
        elif delete_orphaned and relative_path not in referenced_paths:
            orphaned_images.append((full_path, relative_path))
        else:
            valid_images.append((full_path, relative_path))
    
    # Report findings
    print("=" * 80)
    print("IMAGE FILE ANALYSIS")
    print("=" * 80)
    print(f"Total image files: {len(all_image_files)}")
    print(f"  Valid images: {len(valid_images)}")
    print(f"  Invalid images: {len(invalid_images)}")
    if delete_orphaned:
        print(f"  Orphaned images (valid but not referenced): {len(orphaned_images)}")
    print()
    
    files_to_delete = invalid_images.copy()
    if delete_orphaned:
        files_to_delete.extend(orphaned_images)
    
    if not files_to_delete:
        print("[OK] No invalid or orphaned image files to delete!")
        return
    
    print("=" * 80)
    print("FILES TO BE DELETED")
    print("=" * 80)
    
    if invalid_images:
        print(f"\n[INVALID] {len(invalid_images)} file(s) with invalid paths:")
        for full_path, relative_path in invalid_images:
            file_size = os.path.getsize(full_path) if os.path.exists(full_path) else 0
            size_kb = file_size / 1024
            print(f"  - {relative_path} ({size_kb:.2f} KB)")
    
    if orphaned_images:
        print(f"\n[ORPHANED] {len(orphaned_images)} file(s) not referenced by any questions:")
        for full_path, relative_path in orphaned_images:
            file_size = os.path.getsize(full_path) if os.path.exists(full_path) else 0
            size_kb = file_size / 1024
            print(f"  - {relative_path} ({size_kb:.2f} KB)")
    
    # Calculate total size
    total_size = 0
    for full_path, _ in files_to_delete:
        if os.path.exists(full_path):
            total_size += os.path.getsize(full_path)
    total_size_mb = total_size / (1024 * 1024)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files to delete: {len(files_to_delete)}")
    print(f"Total size to free: {total_size_mb:.2f} MB")
    
    if dry_run:
        print("\n" + "=" * 80)
        print("[DRY RUN] This was a dry run. No files were deleted.")
        print("         Run with --execute to actually delete these files.")
        if not delete_orphaned:
            print("         Use --delete-orphaned to also delete orphaned images.")
        print("=" * 80)
        return
    
    # Actually delete
    print("\n[INFO] Starting deletion...\n")
    
    deleted_count = 0
    deleted_size = 0
    errors = []
    
    for full_path, relative_path in files_to_delete:
        try:
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                os.remove(full_path)
                deleted_count += 1
                deleted_size += file_size
                
                if deleted_count % 10 == 0:
                    print(f"  [PROGRESS] Deleted {deleted_count} files...")
            else:
                print(f"  [WARNING] File not found (may have been deleted): {relative_path}")
        except Exception as e:
            error_msg = f"Error deleting {relative_path}: {str(e)}"
            errors.append(error_msg)
            print(f"  [ERROR] {error_msg}")
    
    # Try to remove empty directories
    print("\n[INFO] Cleaning up empty directories...")
    questions_dir = os.path.join(media_root, 'questions')
    if os.path.exists(questions_dir):
        for root, dirs, files in os.walk(questions_dir, topdown=False):
            try:
                if not os.listdir(root):  # Directory is empty
                    os.rmdir(root)
                    print(f"  [CLEANUP] Removed empty directory: {os.path.relpath(root, media_root)}")
            except OSError:
                pass  # Directory not empty or other error
    
    print("\n" + "=" * 80)
    print("DELETION SUMMARY")
    print("=" * 80)
    print(f"Total files deleted: {deleted_count}")
    print(f"Total size freed: {deleted_size / (1024 * 1024):.2f} MB")
    
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    
    print("\n[OK] Deletion complete!")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Delete invalid image files from media/questions/ directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This will permanently delete image files from the filesystem!

The script will:
- Find image files with invalid paths (not in questions/year*/<topic>/ format)
- Optionally find orphaned images (valid paths but not referenced by any questions)
- Delete these files and clean up empty directories

Examples:
  # Dry run (show what would be deleted)
  python delete_invalid_image_files.py
  
  # Actually delete invalid images
  python delete_invalid_image_files.py --execute
  
  # Also delete orphaned images (not referenced by questions)
  python delete_invalid_image_files.py --execute --delete-orphaned
        """
    )
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the files (default is dry run)')
    parser.add_argument('--delete-orphaned', action='store_true',
                       help='Also delete orphaned images (valid paths but not referenced by questions)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if not dry_run:
        print("\n" + "!" * 80)
        print("WARNING: You are about to DELETE image files from the filesystem!")
        print("!" * 80)
        print()
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("Cancelled. No files were deleted.")
            sys.exit(0)
        print()
    
    delete_invalid_image_files(dry_run=dry_run, delete_orphaned=args.delete_orphaned)

