from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date, parse_datetime
from datetime import datetime, time as dtime

from .admin import AssignmentAdmin
from .models import Subject, Assignment, Grade, Attendance, Event
from .serializers import SubjectSerializer, AssignmentSerializer, GradeSerializer, AttendanceSerializer, EventSerializer

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
        by_subject = [
            {"subject": s, "avg": round(sum(vals)/len(vals), 2), "count": len(vals)}
            for s, vals in by_subj.items()
        ]
        return Response ({"count": count, "avg": avg, "by_subject": by_subject})


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Attendance.objects.select_related("user", "subject")
        p = self.request.query_params

        if p.get("user"): qs = qs.filter(user_id = p["user"])
        if p.get("subject"): qs = qs.filter(subject_id = p["subject"])
        if p.get("status"): qs = qs.filter(status = p["status"].upper())
        if p.get("start"): qs = qs.filter(date__gte = parse_date(p["start"]))
        if p.get("end"): qs = qs.filter(date__lte = parse_date(p["end"]))
        return qs.order_by ("-date")

    @action(detail = False, methods = ["GET"])
    def summary(self, request):
        qs = self.get_queryset()
        total = qs.count()
        counts = {s: 0 for s in ["PRESENT", "ABSENT", "LATE", "EXCUSED"]}
        for a in qs:
            counts[a.status] += 1
        present_pct = round((counts["PRESENT"] / total) * 100, 2) if total else 0.0

        by_subject = {}
        for a in qs:
            d = by_subject.setdefault(a.subject.name, {"present": 0, "total": 0})
            d["total"] += 1
            if a.status == "PRESENT":
                d["present"] += 1
        per_subject = [
            {
                "subject": s,
                "present": v["present"],
                "total": v["total"],
                "percent": round((v["present"] / v["total"])*100, 2) if v["total"] else 0.0,
            }
            for s, v in by_subject.items()
        ]

        return Response({
            "total": total,
            "counts": counts,
            "present_percent": present_pct,
            "by_subject": per_subject
        })

def _aware (dt: datetime) -> datetime:
    tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, tz)
    return dt.astimezone(tz)

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Minimal, robust events API."""
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer
    queryset = Event.objects.select_related("owner", "subject").order_by("starts_at")

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

        # simple safe filters (ignore bad ids instead of crashing)
        owner = p.get("owner")
        subject = p.get("subject")
        if owner and owner.isdigit():
            qs = qs.filter(owner_id=int(owner))
        if subject and subject.isdigit():
            qs = qs.filter(subject_id=int(subject))

        if p.get("upcoming") == "true":
            qs = qs.filter(starts_at__gte=timezone.now())

        return qs

    @action(detail=False, methods=["GET"])
    def next(self, request):
        obj = self.get_queryset().filter(starts_at__gte=timezone.now()).first()
        return Response(EventSerializer(obj).data if obj else None)

    @action(detail=False, methods=["GET"])
    def general(self, request):
        """Events without a subject (for 'General Lectures')."""
        qs = self.get_queryset().filter(subject__isnull=True)
        return Response(EventSerializer(qs, many=True).data)

