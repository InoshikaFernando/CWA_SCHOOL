# Deploying StudentFinalAnswer Table to Production

This guide walks through deploying the new `StudentFinalAnswer` table and related changes to production.

## Overview

The `StudentFinalAnswer` table stores aggregated quiz attempt results, making it easier to:
- Track attempt numbers per student-topic-level combination
- Query best results efficiently
- Display results on the dashboard

## Prerequisites

- Access to production server
- Database backup (recommended before any migration)
- Ability to run Django management commands

## Deployment Steps

### Step 1: Backup Production Database

**IMPORTANT**: Always backup before running migrations!

```bash
# On production server
python manage.py dumpdata --indent 2 --output backup_before_studentfinalanswer.json
```

Or use your existing backup script:
```bash
python Testing/backup_production_db.py
```

### Step 2: Pull Latest Code

Pull the latest code that includes:
- `maths/models.py` (with `StudentFinalAnswer` model)
- `maths/migrations/0011_add_student_final_answer.py`
- Updated `maths/views.py` (with save logic)
- `Testing/backfill_student_final_answer.py` script

```bash
# Navigate to project directory
cd /path/to/CWA_SCHOOL

# Pull latest changes (adjust based on your deployment method)
git pull origin main
# OR
# If using other deployment method, ensure all files are updated
```

### Step 3: Verify Files Are Present

Check that the migration file exists:
```bash
ls maths/migrations/0011_add_student_final_answer.py
```

Check that the backfill script exists:
```bash
ls Testing/backfill_student_final_answer.py
```

### Step 4: Run Database Migration

Apply the migration to create the new table:

```bash
python manage.py migrate maths
```

Expected output:
```
Operations to perform:
  Apply all migrations: maths
Running migrations:
  Applying maths.0011_add_student_final_answer... OK
```

### Step 5: Verify Table Creation

Verify the table was created successfully:

```bash
python Testing/display_table_records.py --table_name maths_studentfinalanswer
```

Expected output:
```
[INFO] Total records: 0
No records found in this table.
```

This is expected - the table is empty until we backfill.

### Step 6: Backfill Existing Data (DRY RUN)

First, run a dry-run to see what will be created:

```bash
python Testing/backfill_student_final_answer.py
```

This will show:
- How many sessions will be processed
- How many records will be created
- Any errors or skipped records

**Review the output carefully** before proceeding.

### Step 7: Backfill Existing Data (EXECUTE)

If the dry-run looks good, execute the backfill:

```bash
python Testing/backfill_student_final_answer.py --execute
```

Expected output:
```
[EXECUTE MODE] - Changes will be saved to the database

Found X unique sessions to process

Backfill Summary:
Created: X
Updated: 0
Skipped: 0 (missing topic/level)
Errors: 0

[SUCCESS] Backfill completed!
```

### Step 8: Verify Backfill Results

Check that records were created:

```bash
python Testing/display_table_records.py --table_name maths_studentfinalanswer --limit 10
```

You should see records with:
- Student names
- Session IDs
- Topics and levels
- Attempt numbers
- Points earned

### Step 9: Test New Quiz Completion

**Important**: Test that new quiz completions work correctly:

1. Log in as a test student
2. Complete a quiz (e.g., Year 3 Measurements)
3. Verify a new record appears in `maths_studentfinalanswer`:

```bash
python Testing/display_table_records.py --table_name maths_studentfinalanswer --limit 20
```

4. Check that:
   - Attempt number increments correctly
   - Points are calculated correctly
   - Dashboard displays the result

### Step 10: Monitor for Issues

After deployment, monitor:
- Error logs for any issues
- Dashboard functionality
- Quiz completion flow
- Database performance

## Rollback Plan (If Needed)

If you need to rollback:

### Option 1: Remove the Table (if no data loss is acceptable)

```bash
python manage.py migrate maths 0010_topiclevelstatistics
```

This will remove the `StudentFinalAnswer` table. **Note**: This will delete all records in the table.

### Option 2: Keep Table, Revert Code

1. Revert code changes (remove save logic from views)
2. Keep the table (data preserved)
3. Re-deploy when ready

## Verification Checklist

- [ ] Database backup completed
- [ ] Code pulled/updated
- [ ] Migration applied successfully
- [ ] Table created and verified
- [ ] Backfill dry-run completed
- [ ] Backfill executed successfully
- [ ] Records verified in table
- [ ] New quiz completion tested
- [ ] Dashboard displays results correctly
- [ ] No errors in logs

## Troubleshooting

### Migration Fails

If migration fails:
1. Check error message
2. Verify database connection
3. Check for conflicting migrations
4. Review database logs

### Backfill Errors

If backfill has errors:
1. Check error messages in output
2. Verify all questions have topics
3. Check for missing levels
4. Review skipped records

### No Records After Backfill

If no records appear:
1. Check if `StudentAnswer` records have `session_id`
2. Verify topics and levels exist
3. Check for filtering issues
4. Review backfill script output

### Dashboard Not Showing Results

If dashboard doesn't show results:
1. Verify `StudentFinalAnswer` records exist
2. Check dashboard query logic
3. Verify topic/level matching
4. Check browser console for errors

## Post-Deployment

After successful deployment:

1. **Update Documentation**: Ensure `DATABASE_SCHEMA.md` is updated:
   ```bash
   python Testing/generate_database_documentation.py
   ```

2. **Monitor Performance**: Watch for any performance issues

3. **Gather Feedback**: Monitor user experience

## Support

If you encounter issues:
1. Check error logs
2. Review this guide
3. Check `RESULT_SAVING_FLOW.md` for how results are saved
4. Review `DATABASE_SCHEMA.md` for table structure

## Notes

- The `StudentFinalAnswer` table is **additive** - it doesn't replace `StudentAnswer`
- Both tables work together:
  - `StudentAnswer`: Individual question answers
  - `StudentFinalAnswer`: Aggregated quiz attempts
- New quiz completions automatically save to both tables
- The backfill script can be run multiple times safely (uses `update_or_create`)

