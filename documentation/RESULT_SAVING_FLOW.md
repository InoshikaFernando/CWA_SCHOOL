# How Results Are Saved When Students Complete a Topic

This document explains the complete flow of how student quiz results are saved to the database when completing a topic (e.g., Year 6 Measurements).

## Overview

When a student completes a topic quiz, results are saved in the `maths_studentanswer` table. Each answer is saved individually as the student progresses, and all answers are linked together using a `session_id`.

## Step-by-Step Flow

### 1. Starting the Quiz

When a student starts a quiz (e.g., Year 6 Measurements):

**Location:** `maths/views.py` → `measurements_questions()` function

```python
# On first question (question_number == 1)
if question_number == 1 and not timer_start:
    # Start timer
    request.session[timer_session_key] = time.time()
    
    # Generate unique session ID for this attempt
    import uuid
    request.session['current_attempt_id'] = str(uuid.uuid4())
    
    # Select questions using stratified random sampling
    selected_questions = select_questions_stratified(all_questions_list, question_limit)
    
    # Store question IDs in session
    request.session[questions_session_key] = [q.id for q in selected_questions]
```

**What happens:**
- A unique `session_id` (UUID) is generated and stored in the Django session
- Questions are selected using stratified random sampling
- Question IDs are stored in the session
- Timer starts

### 2. Answering Each Question

As the student answers each question:

**Location:** `maths/views.py` → `measurements_questions()` → `action == 'check_answer'`

```python
if action == 'check_answer':
    question_id = request.POST.get('question_id')
    answer_id = request.POST.get('answer_id')
    
    # Get the attempt_id from session
    attempt_id = request.session.get('current_attempt_id', '')
    
    # Save student answer with session ID
    student_answer, created = StudentAnswer.objects.update_or_create(
        student=request.user,
        question=question,
        defaults={
            'selected_answer': answer,
            'is_correct': answer.is_correct,
            'points_earned': question.points if answer.is_correct else 0,
            'session_id': attempt_id  # Links all answers together
        }
    )
```

**What happens:**
- Each answer is saved immediately to the database
- The `session_id` links all answers from the same quiz attempt
- Uses `update_or_create()` to handle re-answering the same question
- `is_correct` and `points_earned` are calculated and saved

**Database Record Created:**
```python
StudentAnswer(
    student=request.user,           # The student
    question=question,              # The question answered
    selected_answer=answer,         # The answer chosen
    is_correct=True/False,          # Whether answer is correct
    points_earned=0 or question.points,  # Points earned
    session_id=attempt_id,          # Links all answers in this attempt
    answered_at=datetime.now(),     # Timestamp (auto)
    time_taken_seconds=0            # Set to 0 initially
)
```

### 3. Completing the Quiz

When the student clicks "Finish" (after answering all questions):

**Location:** `maths/views.py` → `measurements_questions()` → `completed == '1'`

```python
if completed:
    # Get all answers for this session
    attempt_id = request.session.get('current_attempt_id', '')
    student_answers = StudentAnswer.objects.filter(
        student=request.user,
        question__level=level,
        question__topic=measurements_topic,
        session_id=attempt_id
    )
    
    # Calculate totals
    total_score = sum(answer.points_earned for answer in student_answers)
    total_points = sum(q.points for q in all_questions)
    
    # Calculate time taken
    now_ts = time.time()
    start_ts = request.session.get(timer_session_key) or now_ts
    total_time_seconds = max(1, int(now_ts - start_ts))
    
    # Update time_taken_seconds for ALL answers in this session
    student_answers.update(time_taken_seconds=total_time_seconds)
```

**What happens:**
- All answers with the same `session_id` are retrieved
- Total score and total points are calculated
- Total time taken is calculated
- **All answers in the session are updated** with the same `time_taken_seconds` value

### 4. Statistics Update

After saving results, statistics are updated asynchronously:

```python
# Update topic-level statistics (for color coding)
def update_stats_async():
    try:
        update_topic_statistics(level_num=level.level_number, topic_name=measurements_topic.name)
    except Exception:
        pass

thread = threading.Thread(target=update_stats_async)
thread.daemon = True
thread.start()
```

**What happens:**
- Topic-level statistics (average points, standard deviation) are recalculated
- This runs asynchronously to avoid blocking the redirect
- Used for color-coding on the dashboard

### 5. Session Cleanup

After completion, session variables are cleared:

```python
# Clear timer and question list for next attempt
if timer_session_key in request.session:
    del request.session[timer_session_key]
if questions_session_key in request.session:
    del request.session[questions_session_key]
if 'current_attempt_id' in request.session:
    del request.session['current_attempt_id']
```

**What happens:**
- Session variables are cleared
- **Database records remain** - they are permanent
- Student can start a new quiz attempt

## Database Structure

### StudentAnswer Table

Each completed quiz creates multiple `StudentAnswer` records:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Primary key | 1, 2, 3... |
| `student` | ForeignKey to CustomUser | avisha.munasinghe |
| `question` | ForeignKey to Question | "Convert 5m to cm" |
| `selected_answer` | ForeignKey to Answer | "500 cm" |
| `text_answer` | Text (for short answers) | "" |
| `is_correct` | Boolean | True |
| `points_earned` | Integer | 2 |
| `answered_at` | DateTime | 2025-11-09 10:40:21 |
| `session_id` | CharField | "7e052f9e-7094-4ab5-8eea-41fd53537633" |
| `time_taken_seconds` | Integer | 7977 |

### Key Points

1. **One Record Per Question**: Each question answered creates one `StudentAnswer` record
2. **Session ID Links Answers**: All answers from the same quiz attempt share the same `session_id`
3. **Time is Shared**: All answers in a session have the same `time_taken_seconds` (total quiz time)
4. **Permanent Storage**: Records are never automatically deleted
5. **Unique Constraint**: `(student, question)` is unique - re-answering updates the existing record

## Example: Year 6 Measurements Quiz

**Scenario:** Student completes Year 6 Measurements (20 questions)

**Database Records Created:**
- 20 `StudentAnswer` records
- All have the same `session_id` (e.g., `"7e052f9e-7094-4ab5-8eea-41fd53537633"`)
- All have the same `time_taken_seconds` (e.g., `7977`)
- Each record has its own `is_correct` and `points_earned`

**Query to Get All Answers for a Session:**
```python
StudentAnswer.objects.filter(
    student=request.user,
    session_id="7e052f9e-7094-4ab5-8eea-41fd53537633"
)
```

**Query to Get All Completed Sessions:**
```python
# Get unique session IDs for Year 6 Measurements
StudentAnswer.objects.filter(
    student=request.user,
    question__level__level_number=6,
    question__topic__name="Measurements"
).exclude(session_id='').values('session_id').distinct()
```

## Dashboard Display

The dashboard uses these records to display results:

**Location:** `maths/views.py` → `dashboard_detail()`

```python
# Group by level, topic, and session_id
unique_level_topic_sessions = student_answers_with_topics.values(
    'question__level__level_number', 
    'question__topic__name',
    'session_id'
).distinct()

# For each session, check if it meets the threshold (90%+ completion)
for session_id in session_ids:
    session_answers = student_answers_with_topics.filter(
        session_id=session_id,
        question__level__level_number=level_num,
        question__topic__name=topic_name
    )
    answer_count = session_answers.count()
    
    if answer_count >= partial_threshold:  # 90% of required
        # Calculate points and display on dashboard
        # Points = (percentage * 100 * 60) / time_seconds
```

## Important Notes

1. **Answers Saved Immediately**: Each answer is saved as soon as the student submits it, not just at the end
2. **Session ID is Critical**: The `session_id` is what groups answers together into a single quiz attempt
3. **Time is Updated on Completion**: `time_taken_seconds` is set to 0 initially, then updated to the total time when the quiz is completed
4. **Re-answering Updates**: If a student answers the same question twice, the record is updated (not duplicated) due to `unique_together = ("student", "question")`
5. **Incomplete Sessions**: If a student doesn't finish, the answers are still saved but `time_taken_seconds` may remain 0

## Troubleshooting

**Q: Why don't results appear on the dashboard?**
- Check if `session_id` is not empty
- Check if `answer_count >= partial_threshold` (90% of required questions)
- Check if `time_taken_seconds > 0`

**Q: How to see all answers for a specific session?**
```python
python Testing/display_table_records.py --table_name maths_studentanswer
# Then filter by session_id in the output
```

**Q: How to merge incomplete sessions?**
```python
python Testing/fix_incomplete_sessions.py --level 6 --topic "Measurements" --execute
```

