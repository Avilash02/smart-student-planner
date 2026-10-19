"""Planner models: Task, Exam, StudySession"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=100)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.status == 'pending' and self.due_date < timezone.localdate()

    @property
    def is_due_today(self):
        return self.due_date == timezone.localdate()

    @property
    def is_due_tomorrow(self):
        from datetime import timedelta
        return self.due_date == timezone.localdate() + timedelta(days=1)

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def priority_order(self):
        return {'high': 0, 'medium': 1, 'low': 2}.get(self.priority, 1)


class Exam(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    exam_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exam_date']

    def __str__(self):
        return f"{self.name} ({self.subject})"

    @property
    def days_remaining(self):
        delta = self.exam_date - timezone.localdate()
        return delta.days

    @property
    def is_upcoming(self):
        return self.exam_date >= timezone.localdate()

    @property
    def is_past(self):
        return self.exam_date < timezone.localdate()


class StudySession(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.CharField(max_length=200)
    study_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(help_text='Duration in minutes')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['study_date', 'start_time']

    def __str__(self):
        return f"{self.subject} on {self.study_date}"

    @property
    def duration_display(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        elif hours:
            return f"{hours}h"
        return f"{minutes}m"
