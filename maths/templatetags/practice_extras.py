from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup dictionary values by key"""
    return dictionary.get(key, [])

@register.filter
def basic_facts_level(level_number):
    """Convert Basic Facts level number (100+) to display level (1+)"""
    if level_number >= 100:
        # Each subtopic has 7 levels
        # Addition: 100-106, Subtraction: 107-113, Multiplication: 114-120, Division: 121-127
        # Calculate which block of 7 we're in, then the offset within that block
        block_start = ((level_number - 100) // 7) * 7 + 100
        offset = level_number - block_start
        return offset + 1
    return level_number

@register.filter
def format_time(seconds):
    """Format seconds into mm:ss or ss format"""
    if not seconds or seconds == 0:
        return "N/A"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"