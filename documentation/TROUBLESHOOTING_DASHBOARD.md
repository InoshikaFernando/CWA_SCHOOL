# Troubleshooting Dashboard Not Showing Results

## Issue: Dashboard Not Showing Results for Student

If you've updated the code to use `StudentFinalAnswer` but results still don't appear:

### Step 1: Verify Code is Deployed

**Check if the updated `maths/views.py` is in production:**

1. SSH into production server
2. Check the `dashboard_detail` function around line 526-594
3. Look for this code:
   ```python
   # PRIMARY: Get all level-topic combinations from StudentFinalAnswer table
   final_answer_combinations = StudentFinalAnswer.objects.filter(
       student=request.user
   ).values(
       'level__level_number',
       'topic__name'
   ).distinct()
   ```

If this code is NOT present, the updated code hasn't been deployed yet.

### Step 2: Verify StudentFinalAnswer Records Exist

Run this in production:
```bash
python Testing/display_table_records.py --table_name maths_studentfinalanswer
```

Check that records exist for the student.

### Step 3: Test Dashboard Logic

Run this in production:
```bash
python Testing/test_dashboard_for_student.py --username avisha.munasinghe
```

This will show exactly what the dashboard query returns.

### Step 4: Check Which Page You're Viewing

**Important:** There are TWO dashboard pages:

1. **Main Dashboard** (`/dashboard/`) - Shows topic cards, doesn't show progress table
2. **Detail Dashboard** (`/dashboard/detail/`) - Shows progress table with results

Make sure you're viewing the **Detail Dashboard** (`/dashboard/detail/`).

### Step 5: Clear Browser Cache

Sometimes the browser caches the old page. Try:
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Or clear browser cache

### Step 6: Check for Errors

Check the Django error logs in production for any exceptions.

### Step 7: Verify Template is Correct

The template should check for `show_progress_table`:
```html
{% if show_progress_table %}
    {% if progress_by_level %}
        <!-- Progress table here -->
    {% endif %}
{% endif %}
```

### Step 8: Reload Web App

If using PythonAnywhere:
1. Go to Web tab
2. Click the green **Reload** button
3. Wait for reload to complete
4. Try accessing dashboard again

## Quick Checklist

- [ ] Code is deployed to production
- [ ] Migration `0011_add_student_final_answer` is applied
- [ ] `StudentFinalAnswer` records exist for the student
- [ ] Viewing `/dashboard/detail/` (not `/dashboard/`)
- [ ] Browser cache cleared
- [ ] Web app reloaded (if PythonAnywhere)
- [ ] No errors in Django logs

## Common Issues

### Issue: "No progress data yet" message

**Cause:** `progress_by_level` is empty

**Solution:**
1. Check if `StudentFinalAnswer` records exist
2. Run `test_dashboard_for_student.py` to see what query returns
3. Verify level and topic names match exactly

### Issue: Results show on test but not in browser

**Cause:** Code not deployed or browser cache

**Solution:**
1. Verify code is in production
2. Clear browser cache
3. Reload web app

### Issue: Some students see results, others don't

**Cause:** `StudentFinalAnswer` records not created for all students

**Solution:**
1. Run backfill script:
   ```bash
   python Testing/backfill_student_final_answer.py --execute
   ```

## Still Not Working?

1. Run diagnostic script:
   ```bash
   python Testing/diagnose_dashboard_results.py --username <student_username>
   ```

2. Run test script:
   ```bash
   python Testing/test_dashboard_for_student.py --username <student_username>
   ```

3. Check Django logs for errors

4. Verify database connection and that migrations are applied

