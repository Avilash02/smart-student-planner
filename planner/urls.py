"""Planner URL configuration"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.task_add, name='task_add'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),

    # Exams
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.exam_add, name='exam_add'),
    path('exams/<int:pk>/edit/', views.exam_edit, name='exam_edit'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),

    # Study Plan
    path('study/', views.study_plan, name='study_plan'),
    path('study/add/', views.study_session_add, name='study_session_add'),
    path('study/<int:pk>/edit/', views.study_session_edit, name='study_session_edit'),
    path('study/<int:pk>/delete/', views.study_session_delete, name='study_session_delete'),
    path('study/<int:pk>/toggle/', views.study_session_toggle, name='study_session_toggle'),
]
