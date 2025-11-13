from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

def generate_class_code():
    return uuid.uuid4().hex[:8]

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth")
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    region = models.CharField(max_length=100, blank=True, help_text="Region/State/Province")

    def __str__(self):
        return self.username

class Topic(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name

class Level(models.Model):
    topics = models.ManyToManyField(Topic, related_name="levels", blank=True)
    level_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("level_number",)

    def __str__(self):
        return f"Year {self.level_number}"

    @property
    def topic_names(self):
        return ", ".join([topic.name for topic in self.topics.all()])

class ClassRoom(models.Model):
    name = models.CharField(max_length=150)
    teacher = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="classes")
    code = models.CharField(max_length=8, unique=True, default=generate_class_code)
    levels = models.ManyToManyField(Level, blank=True, related_name="classrooms")

    def __str__(self):
        return f"{self.name} ({self.code})"

class Enrollment(models.Model):
    student = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="enrollments")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="enrollments")
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "classroom")

    def __str__(self):
        return f"{self.student} → {self.classroom}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('fill_blank', 'Fill in the Blank'),
        ('calculation', 'Calculation'),
    ]
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="questions")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions", help_text="Topic this question belongs to (e.g., BODMAS/PEMDAS, Measurements, Fractions)")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    difficulty = models.PositiveIntegerField(default=1, help_text="1=Easy, 2=Medium, 3=Hard")
    points = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    image = models.ImageField(upload_to='questions/', blank=True, null=True, help_text="Upload an image for this question")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level', 'difficulty', 'created_at']
    
    def __str__(self):
        return f"{self.level} - {self.question_text[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Order for multiple choice options")
    
    class Meta:
        ordering = ['question', 'order', 'id']
    
    def __str__(self):
        return f"{self.question} - {self.answer_text[:30]}..."

class StudentAnswer(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="student_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="student_answers")
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True, help_text="For short answer questions")
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, default="", help_text="Session identifier for tracking attempts")
    time_taken_seconds = models.PositiveIntegerField(default=0, help_text="Time taken for this attempt in seconds")
    
    class Meta:
        unique_together = ("student", "question")
        ordering = ['-answered_at']
    
    def __str__(self):
        return f"{self.student} - {self.question} - {'Correct' if self.is_correct else 'Incorrect'}"

class BasicFactsResult(models.Model):
    """Store Basic Facts quiz attempts in database for persistent tracking"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="basic_facts_results")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="basic_facts_results")
    session_id = models.CharField(max_length=100, help_text="Session identifier for tracking attempts")
    score = models.PositiveIntegerField(help_text="Number of correct answers")
    total_points = models.PositiveIntegerField(help_text="Total possible points")
    time_taken_seconds = models.PositiveIntegerField(help_text="Time taken for this attempt in seconds")
    points = models.DecimalField(max_digits=10, decimal_places=2, help_text="Calculated points based on score, time, and percentage")
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['student', 'level']),
            models.Index(fields=['student', 'level', 'session_id']),
        ]
    
    def __str__(self):
        return f"{self.student} - Level {self.level.level_number} - {self.points} points ({self.completed_at})"

class TimeLog(models.Model):
    """Track daily and weekly time spent by students on the app"""
    student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="time_log")
    daily_total_seconds = models.PositiveIntegerField(default=0, help_text="Total seconds spent today")
    weekly_total_seconds = models.PositiveIntegerField(default=0, help_text="Total seconds spent this week")
    last_reset_date = models.DateField(auto_now=True, help_text="Last date when daily time was reset")
    last_reset_week = models.IntegerField(default=0, help_text="ISO week number of last weekly reset")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last time activity was recorded")
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.student.username} - Daily: {self.daily_total_seconds}s, Weekly: {self.weekly_total_seconds}s"
    
    def reset_daily_if_needed(self):
        """Reset daily time if it's past midnight"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.last_reset_date < today:
            self.daily_total_seconds = 0
            self.last_reset_date = today
            self.save(update_fields=['daily_total_seconds', 'last_reset_date'])
    
    def reset_weekly_if_needed(self):
        """Reset weekly time if it's past Sunday midnight (Monday 00:00)"""
        from django.utils import timezone
        now = timezone.now()
        current_week = now.isocalendar()[1]  # ISO week number
        current_year = now.year
        
        # Check if we need to reset (new week)
        # Week resets on Monday (weekday 0) at midnight
        if self.last_reset_week != current_week:
            # Week has changed, reset weekly total
            self.weekly_total_seconds = 0
            self.last_reset_week = current_week
            self.save(update_fields=['weekly_total_seconds', 'last_reset_week'])

class TopicLevelStatistics(models.Model):
    """Store average and standard deviation (sigma) for each topic-level combination"""
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="topic_statistics")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="level_statistics")
    average_points = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Average points across all students")
    sigma = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Standard deviation (sigma)")
    student_count = models.PositiveIntegerField(default=0, help_text="Number of students who have completed this topic-level")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last time statistics were calculated")
    
    class Meta:
        unique_together = ("level", "topic")
        ordering = ['level__level_number', 'topic__name']
        indexes = [
            models.Index(fields=['level', 'topic']),
        ]
    
    def __str__(self):
        return f"{self.level} - {self.topic}: avg={self.average_points}, σ={self.sigma} (n={self.student_count})"
    
    def get_color_class(self, student_points):
        """
        Determine color class based on student's points relative to average and sigma
        Returns: 'dark-green', 'green', 'light-green', 'yellow', 'orange', 'red'
        """
        if self.sigma == 0 or self.student_count < 2:
            # Not enough data for meaningful comparison
            return 'light-green'
        
        avg = float(self.average_points)
        sigma = float(self.sigma)
        points = float(student_points)
        
        # Calculate how many sigmas above/below average
        diff = points - avg
        
        if diff > 2 * sigma:
            return 'dark-green'  # > avg + 2σ
        elif diff > sigma:
            return 'green'  # avg + σ to avg + 2σ
        elif diff > -sigma:
            return 'light-green'  # avg - σ to avg + σ
        elif diff > -2 * sigma:
            return 'yellow'  # avg - 2σ to avg - σ
        elif diff > -3 * sigma:
            return 'orange'  # avg - 3σ to avg - 2σ
        else:
            return 'red'  # < avg - 3σ
