# Deployment Steps for Basic Facts

## Issue: Basic Facts Panel Not Showing on PythonAnywhere

The Basic Facts panel requires specific database records (Topics and Levels) to be created. Follow these steps:

## Step 1: Verify Code is Deployed
```bash
# On PythonAnywhere, make sure you've pulled the latest code
git pull origin main

# Or if using a different branch
git pull origin <your-branch>
```

## Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 3: Create Basic Facts Structure
```bash
# Run the script to create Basic Facts topics and levels
python create_basic_facts.py
```

This script will:
- Create "Basic facts" topic
- Create subtopics: Addition, Subtraction, Multiplication, Division
- Create 28 levels (100-127) associated with these subtopics

## Step 4: Verify Basic Facts Were Created
```bash
# Open Django shell
python manage.py shell
```

Then run:
```python
from maths.models import Level, Topic

# Check if Basic Facts levels exist
basic_facts_levels = Level.objects.filter(level_number__gte=100)
print(f"Basic Facts levels found: {basic_facts_levels.count()}")

# Should show 28 levels (100-127)
for level in basic_facts_levels:
    topics = level.topics.all()
    print(f"Level {level.level_number}: {[t.name for t in topics]}")

# Check if topics exist
topics = Topic.objects.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division'])
print(f"\nSubtopics found: {topics.count()}")
for topic in topics:
    print(f"- {topic.name}")
```

## Step 5: Reload Web App
- Go to PythonAnywhere Web tab
- Click the "Reload" button for your web app

## Troubleshooting

### If Basic Facts panel still doesn't show:

1. **Check if levels are associated with topics:**
   ```python
   # In Django shell
   from maths.models import Level, Topic
   
   addition_topic = Topic.objects.get(name="Addition")
   addition_levels = Level.objects.filter(topics=addition_topic, level_number__gte=100)
   print(f"Addition levels: {addition_levels.count()}")
   ```

2. **Manually associate levels with topics if needed:**
   ```python
   from maths.models import Level, Topic
   
   addition = Topic.objects.get(name="Addition")
   for level_num in range(100, 107):
       level = Level.objects.get(level_number=level_num)
       level.topics.add(addition)
       print(f"Associated level {level_num} with Addition")
   ```

3. **Check the view is receiving data:**
   - Add some debug output to see what `basic_facts_by_subtopic` contains
   - Or check browser console for errors

## Quick Fix Command (All-in-One)

Run this in PythonAnywhere bash console:
```bash
cd /path/to/your/project
python manage.py migrate
python create_basic_facts.py
```

Then reload your web app from the Web tab.


