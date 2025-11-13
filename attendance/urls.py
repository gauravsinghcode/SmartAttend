from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name="home"),
    path('dashboard/', views.dashboard, name="app-dashboard"),
    path('signup/student/', views.signup_student, name='signup_student'),
    path('signup/teacher/', views.signup_teacher, name='signup_teacher'),
    path('login/', views.user_login, name='login'),
    path('', views.landing, name='landing'),
    path('create-qr/', views.create_qr, name='create_qr'),
    path('mark/<str:token>/', views.mark_attendance, name='mark_attendance'),
    path('scan/', views.scan_qr_page, name='scan_qr_page'),
    path('ajax/mark/', views.mark_attendance_ajax, name='mark_attendance_ajax'),
    path('logout/', views.logout_user, name='logout'),
    path("teacher/reports/", views.teacher_reports, name="teacher-reports"),
    path('reports/session/<int:session_id>/', views.session_report, name="session-report"),
]
