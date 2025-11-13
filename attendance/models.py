from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
def generate_unique_token():
    return str(uuid.uuid4())    

class ClassSession(models.Model):
    token = models.CharField(max_length=64, unique=True, default=generate_unique_token, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_by = models.ManyToManyField('CustomUser', blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,    
        blank=True
    )

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"Session {self.token[:6]} ({self.created_at.strftime('%H:%M')})"


class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Present')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')


    def __str__(self):
        return f"{self.student.username} - {self.session.token[:6]} - {self.status}"