"""
Tests for Smart Student Planner.

Covers: registration, login, logout, access control, tasks (CRUD + toggle),
exams (CRUD), study sessions (CRUD + toggle), dashboard stats, and
record ownership isolation.
"""

from datetime import date, timedelta, time

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Exam, StudySession, Task


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_user(username='student', password='pass1234!'):
    return User.objects.create_user(username=username, password=password)


def make_task(owner, days=3, priority='medium', status='pending'):
    return Task.objects.create(
        owner=owner,
        title='Test Task',
        subject='Maths',
        due_date=date.today() + timedelta(days=days),
        priority=priority,
        status=status,
    )


def make_exam(owner, days=5):
    return Exam.objects.create(
        owner=owner,
        name='Midterm',
        subject='Science',
        exam_date=date.today() + timedelta(days=days),
    )


def make_session(owner, days=0):
    return StudySession.objects.create(
        owner=owner,
        subject='Physics',
        study_date=date.today() + timedelta(days=days),
        start_time=time(10, 0),
        duration_minutes=60,
    )


# ─── Authentication ───────────────────────────────────────────────────────────

class RegistrationTests(TestCase):
    def test_register_page_loads(self):
        r = self.client.get(reverse('register'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Create Your Account')

    def test_register_creates_user(self):
        r = self.client.post(reverse('register'), {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'username': 'alice',
            'email': 'alice@test.com',
            'password1': 'Str0ng!Pass',
            'password2': 'Str0ng!Pass',
        })
        self.assertRedirects(r, reverse('login'))
        self.assertTrue(User.objects.filter(username='alice').exists())

    def test_register_duplicate_username(self):
        make_user('alice')
        r = self.client.post(reverse('register'), {
            'first_name': 'Alice',
            'username': 'alice',
            'email': 'new@test.com',
            'password1': 'Str0ng!Pass',
            'password2': 'Str0ng!Pass',
        })
        self.assertEqual(r.status_code, 200)  # stays on form


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_login_valid(self):
        r = self.client.post(reverse('login'), {'username': 'student', 'password': 'pass1234!'})
        self.assertRedirects(r, reverse('dashboard'))

    def test_login_invalid(self):
        r = self.client.post(reverse('login'), {'username': 'student', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)

    def test_logout(self):
        self.client.login(username='student', password='pass1234!')
        r = self.client.post(reverse('logout'))
        self.assertEqual(r.status_code, 302)


# ─── Access Control ───────────────────────────────────────────────────────────

class AccessControlTests(TestCase):
    def test_dashboard_requires_login(self):
        r = self.client.get(reverse('dashboard'))
        self.assertRedirects(r, '/login/?next=/')

    def test_task_list_requires_login(self):
        r = self.client.get(reverse('task_list'))
        self.assertIn('/login/', r['Location'])

    def test_exam_list_requires_login(self):
        r = self.client.get(reverse('exam_list'))
        self.assertIn('/login/', r['Location'])

    def test_study_plan_requires_login(self):
        r = self.client.get(reverse('study_plan'))
        self.assertIn('/login/', r['Location'])


# ─── Tasks ───────────────────────────────────────────────────────────────────

class TaskTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username='student', password='pass1234!')

    def test_task_list_loads(self):
        r = self.client.get(reverse('task_list'))
        self.assertEqual(r.status_code, 200)

    def test_add_task(self):
        r = self.client.post(reverse('task_add'), {
            'title': 'Homework',
            'subject': 'Maths',
            'due_date': (date.today() + timedelta(days=2)).isoformat(),
            'priority': 'high',
            'description': '',
        })
        self.assertRedirects(r, reverse('task_list'))
        self.assertTrue(Task.objects.filter(title='Homework', owner=self.user).exists())

    def test_edit_task(self):
        task = make_task(self.user)
        r = self.client.post(reverse('task_edit', args=[task.pk]), {
            'title': 'Updated',
            'subject': 'Science',
            'due_date': (date.today() + timedelta(days=4)).isoformat(),
            'priority': 'low',
            'description': '',
        })
        self.assertRedirects(r, reverse('task_list'))
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated')

    def test_delete_task(self):
        task = make_task(self.user)
        r = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertRedirects(r, reverse('task_list'))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_complete_task(self):
        task = make_task(self.user)
        self.client.post(reverse('task_toggle', args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')

    def test_reopen_task(self):
        task = make_task(self.user, status='completed')
        self.client.post(reverse('task_toggle', args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, 'pending')

    def test_filter_pending(self):
        make_task(self.user, status='pending')
        make_task(self.user, status='completed')
        r = self.client.get(reverse('task_list') + '?status=pending')
        self.assertEqual(len(r.context['tasks']), 1)

    def test_overdue_property(self):
        task = Task.objects.create(
            owner=self.user, title='Old', subject='X',
            due_date=date.today() - timedelta(days=2), priority='medium'
        )
        self.assertTrue(task.is_overdue)


# ─── Ownership Isolation ─────────────────────────────────────────────────────

class OwnershipTests(TestCase):
    def setUp(self):
        self.user1 = make_user('user1', 'pass1234!')
        self.user2 = make_user('user2', 'pass1234!')
        self.task = make_task(self.user1)
        self.client.login(username='user2', password='pass1234!')

    def test_cannot_edit_others_task(self):
        r = self.client.get(reverse('task_edit', args=[self.task.pk]))
        self.assertEqual(r.status_code, 404)

    def test_cannot_delete_others_task(self):
        r = self.client.post(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_cannot_toggle_others_task(self):
        self.client.post(reverse('task_toggle', args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'pending')  # unchanged


# ─── Exams ───────────────────────────────────────────────────────────────────

class ExamTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username='student', password='pass1234!')

    def test_exam_list_loads(self):
        r = self.client.get(reverse('exam_list'))
        self.assertEqual(r.status_code, 200)

    def test_add_exam(self):
        r = self.client.post(reverse('exam_add'), {
            'name': 'Final',
            'subject': 'History',
            'exam_date': (date.today() + timedelta(days=10)).isoformat(),
            'notes': '',
        })
        self.assertRedirects(r, reverse('exam_list'))
        self.assertTrue(Exam.objects.filter(name='Final', owner=self.user).exists())

    def test_days_remaining(self):
        exam = make_exam(self.user, days=7)
        self.assertEqual(exam.days_remaining, 7)

    def test_delete_exam(self):
        exam = make_exam(self.user)
        r = self.client.post(reverse('exam_delete', args=[exam.pk]))
        self.assertRedirects(r, reverse('exam_list'))
        self.assertFalse(Exam.objects.filter(pk=exam.pk).exists())


# ─── Study Sessions ───────────────────────────────────────────────────────────

class StudySessionTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username='student', password='pass1234!')

    def test_study_plan_loads(self):
        r = self.client.get(reverse('study_plan'))
        self.assertEqual(r.status_code, 200)

    def test_add_session(self):
        today = date.today().isoformat()
        r = self.client.post(reverse('study_session_add'), {
            'subject': 'Biology',
            'study_date': today,
            'start_time': '09:00',
            'duration_minutes': 90,
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(StudySession.objects.filter(subject='Biology', owner=self.user).exists())

    def test_toggle_session(self):
        session = make_session(self.user)
        self.assertFalse(session.is_completed)
        self.client.post(reverse('study_session_toggle', args=[session.pk]))
        session.refresh_from_db()
        self.assertTrue(session.is_completed)

    def test_delete_session(self):
        session = make_session(self.user)
        self.client.post(reverse('study_session_delete', args=[session.pk]))
        self.assertFalse(StudySession.objects.filter(pk=session.pk).exists())


# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username='student', password='pass1234!')

    def test_dashboard_loads(self):
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_dashboard_counts(self):
        make_task(self.user, status='pending')
        make_task(self.user, status='completed')
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.context['pending_count'], 1)
        self.assertEqual(r.context['completed_count'], 1)
        self.assertEqual(r.context['completion_pct'], 50)

    def test_dashboard_greeting_and_progress_rendering(self):
        self.user.first_name = 'Alice'
        self.user.save()
        make_task(self.user, status='pending')
        make_task(self.user, status='completed')
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, '{{')
        self.assertContains(r, 'Alice! 👋')
        self.assertContains(r, 'style="width: 50%;"')
        self.assertContains(r, 'data-pct="50%"')

    def test_dashboard_empty_state(self):
        r = self.client.get(reverse('dashboard'))
        self.assertFalse(r.context['has_tasks'])

    def test_overdue_on_dashboard(self):
        Task.objects.create(
            owner=self.user, title='Old', subject='X',
            due_date=date.today() - timedelta(days=3),
            priority='high'
        )
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(len(r.context['overdue']), 1)

    def test_data_persists_after_save(self):
        """Data saved in one request appears in next."""
        self.client.post(reverse('task_add'), {
            'title': 'Persist test',
            'subject': 'Python',
            'due_date': (date.today() + timedelta(days=1)).isoformat(),
            'priority': 'medium',
            'description': '',
        })
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.context['pending_count'], 1)

    def test_due_today_and_due_soon_do_not_overlap(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        t_today = Task.objects.create(owner=self.user, title='Task Today', subject='OS', due_date=today, priority='high')
        t_soon = Task.objects.create(owner=self.user, title='Task Tomorrow', subject='Python', due_date=tomorrow, priority='medium')
        r = self.client.get(reverse('dashboard'))
        self.assertIn(t_today, list(r.context['due_today']))
        self.assertNotIn(t_today, list(r.context['due_soon']))
        self.assertIn(t_soon, list(r.context['due_soon']))

    def test_priority_ordering_high_before_medium(self):
        today = date.today() + timedelta(days=2)
        t_med = Task.objects.create(owner=self.user, title='Med Task', subject='OS', due_date=today, priority='medium')
        t_high = Task.objects.create(owner=self.user, title='High Task', subject='Python', due_date=today, priority='high')
        r = self.client.get(reverse('task_list'))
        tasks = list(r.context['tasks'])
        self.assertLess(tasks.index(t_high), tasks.index(t_med))

    def test_study_session_toggle_get_request_is_safe(self):
        session = make_session(self.user)
        r = self.client.get(reverse('study_session_toggle', args=[session.pk]))
        self.assertEqual(r.status_code, 302)
