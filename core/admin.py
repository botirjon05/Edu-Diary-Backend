from django.contrib import admin
from .models import Subject, Assignment, Grade, Attendance, Event

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "color", "created_at")
    search_fields = ("code", "name")

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "due_at", "status", "created_at")
    list_filter = ("subject", "status")
    search_fields = ("title", "description")

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "value", "credits", "graded_at")
    list_filter = ("subject",)
    search_fields = ("user__username", "subject__name")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "date", "status")
    list_filter = ("subject", "status", "date")
    search_fields = ("user__username", "subject__name")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "subject", "starts_at", "ends_at", "location")
    list_filter = ("subject", "owner")
    search_fields = ("title", "location")
    date_hierarchy = "starts_at"

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


