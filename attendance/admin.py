from django.contrib import admin
from .models import CustomUser, ClassSession, Attendance

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'department', 'roll_number', 'subject')


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'expires_at', 'is_valid_display')
    readonly_fields = ('created_at', 'expires_at', 'used_by')

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.short_description = "Active?"

    filter_horizontal = ('used_by',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_at')
    list_filter = ('status', 'marked_at', 'session')
    search_fields = ('student__username', 'session__token')
