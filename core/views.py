from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from .admin import AssignmentAdmin
from .models import Subject, Assignment, Grade
from .serializers import SubjectSerializer, AssignmentSerializer, GradeSerializer

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


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Grade.objects.select_related ("user", "subject").order_by("-graded_at")
        params = self.request.query_params
        subject = params.get("subject")
        user_id = params.get ("user")
        minv = params.get ("min")
        maxv = params.get ("max")

        if subject:
            qs = qs.filter(subject_id = subject)
        if user_id:
            qs = qs.filter (user_id = user_id)
        if minv is not None:
            qs = qs.filter(value__gte = float(minv))
        if maxv is not None:
            qs = qs.filter(value__lte = float(maxv))
        return qs

    @action(detail = False, methods = ["GET"])
    def summary(self, request):
        """Simple averages for charts/widgets."""
        qs = self.get_queryset()
        count = qs.count()
        if count == 0:
            return Response({"count": 0, "avg": None, "by_subject": []})
        avg = round(sum(g.value for g in qs) / count, 2)

        by_subj = {}
        for g in qs:
            by_subj.setdefault(g.subject.name, []).append(g.value)
        by_subj = [
            {"subject": s, "avg": round(sum(vals)/len(vals), 2), "count": len(vals)}
            for s, vals in by_subj.items()
        ]
        return Response ({"count": count, "avg": avg, "by_subject": by_subject})



