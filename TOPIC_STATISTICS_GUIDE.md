# Topic-Level Statistics and Color Coding Guide

## Overview

The system now calculates average points and standard deviation (sigma) for each topic-level combination and color-codes student results on the dashboard based on their performance relative to the average.

**Important:** Basic Facts topics (levels with `level_number >= 100`) are **excluded** from statistics calculation and color coding. Only Year levels (2-9) are included in the statistics system.

## How It Works

### 1. Statistics Calculation

For each topic-level combination (e.g., "Year 3 - Fractions"), **excluding Basic Facts levels**, the system:
- Finds all students who have completed that topic-level
- Calculates each student's **best points** for that combination
- Computes the **average** of all students' best points
- Calculates the **standard deviation (sigma)** of the points

### 2. Color Coding

Student results are color-coded based on how many standard deviations above or below the average they are:

| Color | Range | Meaning |
|-------|-------|---------|
| **Dark Green** | > avg + 2σ | Excellent - Top performers |
| **Green** | avg + σ to avg + 2σ | Above average |
| **Light Green** | avg - σ to avg + σ | Average range (within 1 standard deviation) |
| **Yellow** | avg - 2σ to avg - σ | Below average |
| **Orange** | avg - 3σ to avg - 2σ | Well below average |
| **Red** | < avg - 3σ | Needs significant improvement |

### 3. Automatic Updates

Statistics are automatically recalculated when:
- A student completes an exercise (all questions answered)
- A student beats their previous record

The statistics update happens in the background and doesn't slow down the user experience.

## Database Model

### TopicLevelStatistics

Stores statistics for each topic-level combination:

- `level`: ForeignKey to Level
- `topic`: ForeignKey to Topic
- `average_points`: Average points across all students
- `sigma`: Standard deviation
- `student_count`: Number of students who have completed this topic-level
- `last_updated`: Timestamp of last calculation

**Unique constraint**: One record per (level, topic) combination

## Usage

### Initial Calculation

To calculate statistics for all topic-level combinations:

```bash
python calculate_topic_statistics.py
```

To calculate for a specific level or topic:

```bash
python calculate_topic_statistics.py --level 3
python calculate_topic_statistics.py --topic "Fractions"
python calculate_topic_statistics.py --level 3 --topic "Fractions"
```

### Viewing Statistics

Statistics are automatically used in the dashboard view. Each student's result row is color-coded based on their performance.

### Manual Update

Statistics are automatically updated when students complete exercises. However, you can manually recalculate:

```bash
python calculate_topic_statistics.py
```

## Migration

After adding the model, run:

```bash
python manage.py migrate
```

This creates the `TopicLevelStatistics` table in your database.

## Notes

1. **Minimum Students**: Statistics require at least 2 students to be meaningful. If there's only 1 student, the color defaults to light-green.

2. **Best Points**: Only each student's **best attempt** is used in the calculation, not all attempts.

3. **Full Attempts Only**: Only completed attempts (all questions answered) are counted.

4. **Performance**: Statistics updates are done asynchronously and won't block the user interface.

5. **Default Color**: If statistics don't exist for a topic-level, the default color is light-green.

## Example

If 3 students complete Year 3 Fractions with best points of:
- Student A: 85.5
- Student B: 72.3
- Student C: 91.2

Then:
- Average = (85.5 + 72.3 + 91.2) / 3 = 83.0
- Sigma = ~9.5 (standard deviation)

Color coding:
- Student A (85.5): Light green (within 1σ of average)
- Student B (72.3): Yellow (between -2σ and -σ)
- Student C (91.2): Green (between +σ and +2σ)

## Troubleshooting

### Statistics not showing colors
- Make sure at least 2 students have completed the topic-level
- Run `python calculate_topic_statistics.py` to initialize statistics
- Check that the migration has been applied: `python manage.py migrate`

### Colors not updating
- Statistics update automatically when students complete exercises
- If needed, manually recalculate: `python calculate_topic_statistics.py`

### Wrong colors
- Verify the statistics are correct: Check the `TopicLevelStatistics` table in the database
- Recalculate if needed: `python calculate_topic_statistics.py`

