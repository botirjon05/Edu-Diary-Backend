from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone

from .admin import AssignmentAdmin
from .models import Subject, Assignment
from .serializers import SubjectSerializer, AssignmentSerializer

class SubjectViewSet (viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]

class AssignmentViewSet (viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Assignment.objects.select_related("subject").order_by("due_at")
        params = self.request.query_params
        subject = params.get("subject")
        status = params.get("status")
        upcoming = params.get("upcoming")
        overdue = params.get("overdue")

        if subject:
            qs = qs.filter(subject_id = subject)
        if status:
            qs = qs.filter(status = status.upper())
        now = timezone.now()
        if upcoming == "true":
            qs = qs.filter(status="PENDING", due_at__gte=now)
        if overdue == "true":
            qs = qs.filter(status="PENDING", due_at__lt=now)
        return qs



