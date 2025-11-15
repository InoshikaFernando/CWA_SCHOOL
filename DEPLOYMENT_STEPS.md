# Deployment Steps for PythonAnywhere

## Standard Deployment Checklist (After Committing to Git)

### Step 1: Pull Latest Code on PythonAnywhere
```bash
# SSH into PythonAnywhere or use Bash Console
cd /home/yourusername/path/to/your/project

# Pull the latest changes from git
git pull origin main

# Or if using a different branch
git pull origin <your-branch>
```

### Step 2: Activate Virtual Environment (if using one)
```bash
# If you have a virtual environment
source /home/yourusername/.virtualenvs/yourvenv/bin/activate

# Or if venv is in project directory
source venv/bin/activate
```

### Step 3: Install/Update Dependencies (if requirements.txt changed)
```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations (if models changed)
```bash
# Create new migration files (only if you haven't already)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### Step 5: Collect Static Files (if CSS/JS changed)
```bash
python manage.py collectstatic --noinput
```

### Step 6: Reload Web App
- Go to PythonAnywhere Dashboard → **Web** tab
- Click the green **Reload** button for your web app
- Wait for reload to complete (usually 10-30 seconds)

### Step 7: Clear Browser Cache (Optional but Recommended)
- Hard refresh: `Ctrl+Shift+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Or use incognito/private window to test

---

## Special Cases

### If You Added New Database Models or Fields
Follow Step 4 above, then verify:
```bash
python manage.py shell
```
```python
from maths.models import YourNewModel
# Test that model exists and works
YourNewModel.objects.all()
```

### If You Added New Basic Facts Topics/Levels
```bash
# Run the Basic Facts creation script
python Questions/create_basic_facts.py
```

### If You Changed Static Files (CSS/JS)
Follow Step 5 above (collectstatic), then Step 6 (reload).

---

## Quick Deployment Command (All-in-One)

Run this in PythonAnywhere bash console:
```bash
cd /home/yourusername/path/to/your/project
git pull origin main
source venv/bin/activate  # if using venv
pip install -r requirements.txt  # if requirements changed
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **reload your web app** from the PythonAnywhere Web tab.

---

## Troubleshooting

### Template Changes Not Showing
1. Verify file was pulled: `cat templates/maths/base.html | head -20`
2. Reload web app (Step 6)
3. Clear browser cache (hard refresh)
4. Check for syntax errors in template

### Database Errors After Migration
```bash
# Check migration status
python manage.py showmigrations

# If stuck, try fake migration (use with caution)
python manage.py migrate --fake
```

### Static Files Not Loading
1. Check `STATIC_URL` and `STATIC_ROOT` in `settings.py`
2. Run `collectstatic` again
3. Verify static files path in PythonAnywhere Web tab settings

---

## Basic Facts Deployment (Legacy)

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
python Questions/create_basic_facts.py
```

This script will:
- Create "Basic facts" topic
- Create subtopics: Addition, Subtraction, Multiplication, Division, Place Value Facts
- Create 33 levels (100-132) associated with these subtopics

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

# Should show 33 levels (100-132)
for level in basic_facts_levels:
    topics = level.topics.all()
    print(f"Level {level.level_number}: {[t.name for t in topics]}")

# Check if topics exist
topics = Topic.objects.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division', 'Place Value Facts'])
print(f"\nSubtopics found: {topics.count()}")
for topic in topics:
    print(f"- {topic.name}")

# Check Place Value Facts specifically
place_value_topic = Topic.objects.filter(name='Place Value Facts').first()
if place_value_topic:
    place_value_levels = Level.objects.filter(topics=place_value_topic, level_number__gte=128)
    print(f"\nPlace Value Facts levels: {place_value_levels.count()} (should be 5)")
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
python Questions/create_basic_facts.py
```

Then reload your web app from the Web tab.


