"""All views for the Smart Student Planner."""

from datetime import timedelta, date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ExamForm, RegistrationForm, StudySessionForm, TaskForm
from .models import Exam, StudySession, Task

PRIORITY_ORDER = Case(
    When(priority='high', then=Value(0)),
    When(priority='medium', then=Value(1)),
    When(priority='low', then=Value(2)),
    default=Value(1),
    output_field=IntegerField(),
)


# ─────────────────────────── Authentication ──────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# ─────────────────────────── Dashboard ───────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    tasks = Task.objects.filter(owner=request.user)
    pending_tasks = tasks.filter(status='pending').annotate(priority_rank=PRIORITY_ORDER)
    completed_tasks = tasks.filter(status='completed')

    total = tasks.count()
    completed_count = completed_tasks.count()
    pending_count = pending_tasks.count()
    completion_pct = round((completed_count / total * 100) if total else 0)

    overdue = pending_tasks.filter(due_date__lt=today).order_by('due_date', 'priority_rank')
    due_today = pending_tasks.filter(due_date=today).order_by('priority_rank')
    # Filter strictly for upcoming dates after today to prevent duplicate listing
    due_soon = pending_tasks.filter(due_date__gt=today).order_by('due_date', 'priority_rank')[:5]

    upcoming_exams_qs = Exam.objects.filter(owner=request.user, exam_date__gte=today)
    upcoming_exams_count = upcoming_exams_qs.count()
    upcoming_exams = upcoming_exams_qs.order_by('exam_date')[:5]

    # Smart suggestion: highest-priority pending task with nearest due date
    suggested_task = (
        pending_tasks.filter(due_date__gte=today)
        .order_by('due_date', 'priority_rank')
        .first()
        or pending_tasks.order_by('priority_rank', 'due_date').first()
    )

    hour = timezone.localtime().hour
    if hour < 12:
        greeting = 'Good Morning'
    elif hour < 17:
        greeting = 'Good Afternoon'
    else:
        greeting = 'Good Evening'

    context = {
        'today': today,
        'greeting': greeting,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'total_count': total,
        'completion_pct': completion_pct,
        'overdue': overdue,
        'due_today': due_today,
        'due_soon': due_soon,
        'upcoming_exams': upcoming_exams,
        'upcoming_exams_count': upcoming_exams_count,
        'suggested_task': suggested_task,
        'has_tasks': total > 0,
        'has_exams': upcoming_exams_count > 0,
    }
    return render(request, 'planner/dashboard.html', context)


# ─────────────────────────── Tasks ───────────────────────────────────────────

@login_required
def task_list(request):
    today = timezone.localdate()
    status_filter = request.GET.get('status', 'all')
    tasks = Task.objects.filter(owner=request.user).annotate(priority_rank=PRIORITY_ORDER)

    if status_filter == 'pending':
        tasks = tasks.filter(status='pending')
    elif status_filter == 'completed':
        tasks = tasks.filter(status='completed')

    tasks = tasks.order_by('due_date', 'priority_rank')

    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'today': today,
        'tomorrow': today + timedelta(days=1),
    }
    return render(request, 'planner/task_list.html', context)


@login_required
def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" added successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
        # Pre-fill today's date
        form.fields['due_date'].initial = timezone.localdate()
    return render(request, 'planner/task_form.html', {'form': form, 'action': 'Add'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'planner/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('task_list')
    return render(request, 'planner/task_confirm_delete.html', {'object': task, 'type': 'Task'})


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        if task.status == 'pending':
            task.status = 'completed'
            messages.success(request, f'"{task.title}" marked as completed!')
        else:
            task.status = 'pending'
            messages.info(request, f'"{task.title}" reopened.')
        task.save()
    next_url = request.POST.get('next') or request.GET.get('next') or 'task_list'
    return redirect(next_url)


# ─────────────────────────── Exams ───────────────────────────────────────────

@login_required
def exam_list(request):
    today = timezone.localdate()
    upcoming = Exam.objects.filter(owner=request.user, exam_date__gte=today).order_by('exam_date')
    past = Exam.objects.filter(owner=request.user, exam_date__lt=today).order_by('-exam_date')
    return render(request, 'planner/exam_list.html', {
        'upcoming': upcoming,
        'past': past,
        'today': today,
    })


@login_required
def exam_add(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.owner = request.user
            exam.save()
            messages.success(request, f'Exam "{exam.name}" added!')
            return redirect('exam_list')
    else:
        form = ExamForm()
        form.fields['exam_date'].initial = timezone.localdate()
    return render(request, 'planner/exam_form.html', {'form': form, 'action': 'Add'})


@login_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam "{exam.name}" updated!')
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'planner/exam_form.html', {'form': form, 'action': 'Edit', 'exam': exam})


@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = exam.name
        exam.delete()
        messages.success(request, f'Exam "{name}" deleted.')
        return redirect('exam_list')
    return render(request, 'planner/task_confirm_delete.html', {'object': exam, 'type': 'Exam'})


# ─────────────────────────── Study Plan ──────────────────────────────────────

@login_required
def study_plan(request):
    today = timezone.localdate()
    view_date_str = request.GET.get('date', '')
    try:
        view_date = date.fromisoformat(view_date_str)
    except ValueError:
        view_date = today

    sessions = StudySession.objects.filter(owner=request.user, study_date=view_date).order_by('start_time')
    total_minutes = sum(s.duration_minutes for s in sessions)

    # Navigation: prev/next day
    prev_date = view_date - timedelta(days=1)
    next_date = view_date + timedelta(days=1)

    context = {
        'sessions': sessions,
        'view_date': view_date,
        'today': today,
        'prev_date': prev_date,
        'next_date': next_date,
        'total_minutes': total_minutes,
        'total_display': _minutes_to_display(total_minutes),
    }
    return render(request, 'planner/study_plan.html', context)


def _minutes_to_display(minutes):
    if not minutes:
        return '0 min'
    h, m = divmod(minutes, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    return ' '.join(parts)


@login_required
def study_session_add(request):
    today = timezone.localdate()
    view_date_str = request.GET.get('date', str(today))
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.owner = request.user
            session.save()
            messages.success(request, f'Study session added for {session.subject}!')
            return redirect(f"{reverse('study_plan')}?date={session.study_date}")
    else:
        form = StudySessionForm()
        form.fields['study_date'].initial = view_date_str
    return render(request, 'planner/study_session_form.html', {'form': form, 'action': 'Add'})


@login_required
def study_session_edit(request, pk):
    session = get_object_or_404(StudySession, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = StudySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Study session updated!')
            return redirect(f"{reverse('study_plan')}?date={session.study_date}")
    else:
        form = StudySessionForm(instance=session)
    return render(request, 'planner/study_session_form.html', {'form': form, 'action': 'Edit', 'session': session})


@login_required
def study_session_delete(request, pk):
    session = get_object_or_404(StudySession, pk=pk, owner=request.user)
    if request.method == 'POST':
        d = session.study_date
        session.delete()
        messages.success(request, 'Study session deleted.')
        return redirect(f"{reverse('study_plan')}?date={d}")
    return render(request, 'planner/task_confirm_delete.html', {'object': session, 'type': 'Study Session'})


@login_required
def study_session_toggle(request, pk):
    session = get_object_or_404(StudySession, pk=pk, owner=request.user)
    if request.method == 'POST':
        session.is_completed = not session.is_completed
        session.save()
        status = 'completed' if session.is_completed else 'reopened'
        messages.success(request, f'Study session {status}!')
    return redirect(f"{reverse('study_plan')}?date={session.study_date}")
