"""Django Admin configuration for Planner models."""

from django.contrib import admin
from .models import Task, Exam, StudySession


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'owner', 'due_date', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'subject']
    search_fields = ['title', 'subject', 'owner__username']
    ordering = ['due_date', '-priority']
    date_hierarchy = 'due_date'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'owner', 'exam_date', 'created_at']
    list_filter = ['subject']
    search_fields = ['name', 'subject', 'owner__username']
    ordering = ['exam_date']
    date_hierarchy = 'exam_date'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'owner', 'study_date', 'start_time', 'duration_minutes', 'is_completed']
    list_filter = ['is_completed', 'study_date']
    search_fields = ['subject', 'owner__username']
    ordering = ['study_date', 'start_time']
