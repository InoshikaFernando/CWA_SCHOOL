# Basic Facts Questions - How They Work

## What `create_basic_facts.py` Does

The `Questions/create_basic_facts.py` script **ONLY creates the structure** - it does NOT create any questions!

### What it creates:
1. **Topics:**
   - "Basic facts" (main topic)
   - "Addition"
   - "Subtraction"
   - "Multiplication"
   - "Division"
   - "Place Value Facts"

2. **Levels:**
   - Levels 100-109: Addition
   - Levels 110-119: Subtraction
   - Levels 120-129: Multiplication
   - Levels 130-139: Division
   - Levels 140-149: Place Value Facts

3. **Associations:**
   - Links levels to their respective topics
   - Links levels to "Basic facts" topic

### What it does NOT do:
- ❌ Does NOT create any questions
- ❌ Does NOT generate question content

## How Questions Are Actually Created

Questions are created by a **separate script**: `generate_basic_facts_questions.py` (in the root directory)

### What `generate_basic_facts_questions.py` does:
1. Generates 10 questions for each Basic Facts level (100-127)
2. Creates Question objects in the database
3. Creates Answer objects for each question

### ⚠️ IMPORTANT ISSUE:

**The `generate_basic_facts_questions.py` script does NOT assign topics to questions!**

Looking at the code (line 312-318):
```python
question = Question.objects.create(
    level=level_obj,
    question_text=question_text,
    question_type='short_answer',
    difficulty=1,
    points=1
    # ❌ NO topic field is set!
)
```

This means:
- Questions are created with only the `level` field
- The `topic` field is `NULL`
- This is why questions don't appear when filtering by topic!

## Level Range Mismatch

There's also a **mismatch in level ranges**:

- `create_basic_facts.py` says:
  - Division: 130-139
  - Multiplication: 120-129

- `generate_basic_facts_questions.py` says:
  - Division: 121-127
  - Multiplication: 114-120

This mismatch means:
- Division levels 130-139 exist but no questions are generated for them
- Questions are generated for levels 121-127, but those levels might not exist

## How to Fix

### Option 1: Update `generate_basic_facts_questions.py` to assign topics

Add topic assignment when creating questions:
```python
# Get the appropriate topic based on level number
if 100 <= level_num <= 109:
    topic = Topic.objects.get(name="Addition")
elif 107 <= level_num <= 113:
    topic = Topic.objects.get(name="Subtraction")
elif 114 <= level_num <= 120:
    topic = Topic.objects.get(name="Multiplication")
elif 121 <= level_num <= 127:
    topic = Topic.objects.get(name="Division")

question = Question.objects.create(
    level=level_obj,
    topic=topic,  # ✅ Add this!
    question_text=question_text,
    question_type='short_answer',
    difficulty=1,
    points=1
)
```

### Option 2: Backfill topics for existing questions

Create a script to assign topics to existing Basic Facts questions based on their level numbers.

## Current Status

- ✅ Topics and levels are created by `create_basic_facts.py`
- ❌ Questions are created by `generate_basic_facts_questions.py` but **without topics**
- ❌ Questions won't appear when filtering by topic because `topic` field is NULL

## To See Questions

Since questions don't have topics assigned, you need to query by level:
```python
# This will work
Question.objects.filter(level__level_number__gte=100, level__level_number__lte=127)

# This won't work (returns 0)
Question.objects.filter(topic__name="Division")
```

