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
