import qrcode
from io import BytesIO
import base64
from django.utils import timezone
from datetime import timedelta
from .models import ClassSession, Attendance
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import StudentSignUpForm, TeacherSignUpForm
from django.http import JsonResponse
from django.urls import reverse
import json
from django.conf import settings


def home(request):

    return render(request, "attendance/landing.html")


@login_required
def dashboard(request):

    if request.user.role == "teacher":

        sessions = ClassSession.objects.filter(teacher=request.user).order_by("-created_at")
        for s in sessions:
            s.count = Attendance.objects.filter(session=s).count()

        return render(request, "attendance/dashboard.html", {
            "is_teacher": True,
            "sessions": sessions,
        })

    else: 
        records = Attendance.objects.filter(
            student=request.user
        ).select_related("session").order_by("-marked_at")[:10]

        return render(request, "attendance/dashboard.html", {
            "is_teacher": False,
            "records": records,
        })



def attendance(request):
    
    return render(request, "attendance/attendance.html")


@login_required
def scan_qr_page(request):
    if request.user.role != 'student':
        return redirect('app-dashboard')
    return render(request, 'attendance/scan_qr.html', {})


@login_required
def mark_attendance_ajax(request):
    if request.method != "POST":
        return JsonResponse({'ok': False, 'msg': 'POST required'}, status=405)

    if request.user.role != 'student':
        return JsonResponse({'ok': False, 'msg': 'Only students can mark attendance'}, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        body = {}

    token = body.get("token") or body.get("data") or request.POST.get("token")
    if not token:
        return JsonResponse({'ok': False, 'msg': 'No token provided'}, status=400)

    if '/' in token:
        token = token.rstrip('/').split('/')[-1]

    try:
        session = ClassSession.objects.get(token=token)
    except ClassSession.DoesNotExist:
        return JsonResponse({'ok': False, 'msg': 'Invalid or unknown QR token'}, status=400)

    if not session.is_valid():
        return JsonResponse({'ok': False, 'msg': 'This session has expired'}, status=400)

    already = Attendance.objects.filter(student=request.user, session=session).exists()
    if already:
        return JsonResponse({'ok': False, 'msg': 'You have already marked attendance for this session'}, status=200)

    Attendance.objects.create(student=request.user, session=session, status='Present')

    return JsonResponse({'ok': True, 'msg': 'Attendance marked successfully'})


def landing(request):

    features = {
        "Automatic Presence Detection": '“Seamlessly marks attendance the moment you’re within a 10-meter radius — no manual check-ins or roll calls needed.”',
        "Verified & Tamper-Proof": '“Built on precise geolocation verification, every record is authentic and tied to the student’s secure identity credentials.”',
        "Instant Attendance Insights": '“View attendance summaries, daily statistics, and visual reports in real-time — empowering teachers with instant analytics.”',
        "our Data, Your Control": '“Location data is processed securely and never stored permanently — ensuring complete transparency and privacy for every user.”',
    }

    steps = {
        1 : ["Detect", "SmartAttend automatically senses students within a 10-meter range — no manual check-ins needed."],
        2 : ["Verify", "Instantly confirms identity with secure, device-based authentication."],
        3 : ["Record", "Attendance is logged and updated in real-time, ready for reports."],
    }

    return render(request, "attendance/landing.html", {"features": features, "steps": steps})


def signup_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Student account created successfully.")
            return redirect('login')
    else:
        form = StudentSignUpForm()
    
    return render(request, "attendance/student_signup.html", {"form": form})


def signup_teacher(request):

    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Teacher account created successfully.")
            return redirect("login")
    else:
        form = TeacherSignUpForm()

    return render(request, "attendance/teacher_signup.html", {"form":form})


@login_required
def create_qr(request):
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can generate QR.")
        return redirect("app-dashboard")

    expiry_time = timezone.now() + timedelta(minutes=5)

    new_session = ClassSession.objects.create(
        teacher=request.user,
        expires_at=expiry_time
    )

    BASE_URL = "https://smartattend-1q4w.onrender.com"

    qr_url = f"{BASE_URL}{reverse('mark_attendance', args=[new_session.token])}"

    qr_img = qrcode.make(qr_url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "attendance/qr_display.html", {
        "session": new_session,
        "qr_url": qr_url,
        "expiry": expiry_time,
        "qr_code": qr_base64,
    })


@login_required
def teacher_reports(request):
    if request.user.role != "teacher":
        return redirect("dashboard")

    sessions = ClassSession.objects.filter(teacher=request.user).order_by("-created_at")

    data = []
    for s in sessions:
        count = Attendance.objects.filter(session=s).count()
        data.append({
            "title": s.title or f"Session {s.id}",
            "count": count,
            "created": s.created_at,
        })

    total_attendance = sum(d["count"] for d in data)

    return render(request, "attendance/teacher_reports.html", {
        "session_data": data,
        "total_sessions": sessions.count(),
        "total_attendance": total_attendance,
    })



@login_required
def mark_attendance(request, token):
    try:
        session = ClassSession.objects.get(token=token)
    except ClassSession.DoesNotExist:
        messages.error(request, "Invalid or expired QR code.")
        return redirect("app-dashboard")

    if not session.is_valid():
        messages.error(request, "This session has expired.")
        return redirect("app-dashboard")

    already_marked = Attendance.objects.filter(student=request.user, session=session).exists()
    if already_marked:
        messages.warning(request, "You’ve already marked attendance for this session.")
        return redirect("app-dashboard")

    Attendance.objects.create(student=request.user, session=session)
    messages.success(request, "Attendance marked successfully!")
    return redirect("app-dashboard")


def user_login(request):

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"]

        user = authenticate(request, username=username, password=password)

        if user is not None and user.role == role:
            login(request, user)
            messages.success(request, f"Welcome {user.username}")
            return redirect("app-dashboard") 
        
        else:
            messages.error(request, "Invalid credentials or role mismatch.")

    return render(request, 'attendance/login.html')


def settings(request):

    return render(request, "attendance/settings.html")


def reports(request):

    return render(request, "attendance/reports.html")


def logout_user(request):
    logout(request)
    return redirect('login')