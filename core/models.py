from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

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


class Grade(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "grades")
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, related_name = "grades")
    value = models.FloatField()
    credits = models.FloatField(blank = True, null = True)
    graded_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}: {self.value}"

class Attendance(models.Model):
    PRESENT, ABSENT, LATE, EXCUSED = "PRESENT", "ABSENT", "LATE", "EXCUSED"
    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (LATE, "Late"),
        (EXCUSED, "Excused"),
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "attendance")
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, related_name = "attendance")
    date = models.DateField()
    status = models.CharField(max_length = 8, choices = STATUS_CHOICES)

    class Meta:
        unique_together = ("user", "subject", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} {self.subject.name} {self.date} {self.status}"

class Event(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "events")
    subject = models.ForeignKey(Subject, on_delete = models.SET_NULL, null = True, blank = True, related_name = "events")
    title = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200, blank = True, null = True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ["starts_at"]
        indexes = [
            models.Index(fields = ["starts_at"]),
        ]

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "Ends at must be after Starts at."})

    def __str__(self):
        return f"{self.title} @ {self.starts_at or 'TBD'}"