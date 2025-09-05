from django.contrib import admin
from .models import Subject, Assignment, Grade

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

