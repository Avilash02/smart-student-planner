"""smart_student_planner URL configuration"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from planner import views as planner_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', planner_views.register_view, name='register'),
    path('accounts/', include('allauth.urls')),

    # App
    path('', include('planner.urls')),
]
