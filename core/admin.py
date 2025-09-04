from django.contrib import admin
from .models import Subject, Assignment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "color", "created_at")
    search_fields = ("code", "name")

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "due_at", "status", "created_at")
    list_filter = ("subject", "status")
    search_fields = ("title", "description")

