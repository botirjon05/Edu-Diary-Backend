from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    code = models.CharField(max_length = 10, unique = True)  # MS for Math
    name = models.CharField(max_length = 100)                # Mathematics
    color = models.CharField(max_length = 7, blank = True, null = True)  # #22c55e
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Assignment(models.Model):
    PENDING, DONE = "PENDING", "DONE"
    STATUS_CHOICES = [(PENDING, "Pending"), (DONE, "Done")]
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, related_name = "assignments")
    title = models.CharField(max_length = 200)
    description = models.TextField(blank = True)
    due_at = models.DateTimeField()
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default = PENDING)
    created_by = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank = True, related_name = "created_assignments")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"