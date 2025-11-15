# Documentation

This folder contains all project documentation files.

## Available Documentation

- **DATABASE_SCHEMA.md** - Complete database schema with all table relationships (auto-generated)
- **DEPLOYMENT_STEPS.md** - Step-by-step guide for deploying to production
- **DEPLOY_STUDENT_FINAL_ANSWER.md** - Guide for deploying the StudentFinalAnswer table to production
- **SESSION_MANAGEMENT_GUIDE.md** - Guide for managing student quiz sessions
- **EMAIL_SETUP_GUIDE.md** - Guide for setting up email functionality
- **TOPIC_STATISTICS_GUIDE.md** - Guide for topic-level statistics and color coding
- **BACKUP_RESTORE_GUIDE.md** - Guide for backing up and restoring the database
- **DJANGO_COMMANDS.md** - Reference for common Django management commands

## Updating Documentation

### Database Schema Documentation

The `DATABASE_SCHEMA.md` file is auto-generated. To update it after model changes:

```bash
python Testing/generate_database_documentation.py
```

This will automatically update the documentation in this folder.

### Other Documentation

Other documentation files are manually maintained. Update them when:
- Adding new features
- Changing workflows
- Updating deployment procedures

## File Locations

All documentation files are now located in the `documentation/` folder at the project root.

## New Features

### StudentFinalAnswer Table

A new table `StudentFinalAnswer` has been added to store aggregated quiz attempt results:
- **Fields**: `id`, `student`, `session_id`, `topic`, `level`, `attempt_number`, `points_earned`, `last_updated_time`
- **Purpose**: Track each quiz attempt with incrementing attempt numbers per student-topic-level combination
- **Benefits**: 
  - Easy to query best results: `StudentFinalAnswer.get_best_result(student, topic, level)`
  - Track attempt numbers automatically
  - More efficient dashboard queries

**Backfill Script**: `Testing/backfill_student_final_answer.py` - Run to populate the table from existing `StudentAnswer` records
