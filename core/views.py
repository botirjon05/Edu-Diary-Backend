import pickle
from http.client import responses

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date, parse_datetime
from datetime import datetime, time as dtime
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters
from django.db import IntegrityError
from rest_framework import serializers

from .admin import AssignmentAdmin
from .models import Subject, Assignment, Grade, Attendance, Event, Enrollment
from .serializers import SubjectSerializer, AssignmentSerializer, GradeSerializer, AttendanceSerializer, EventSerializer, RegisterSerializer, EnrollmentSerializer

class SubjectViewSet (viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

class AssignmentViewSet (viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "subject__name"]
    ordering_fields = ["due_at", "created_at"]

    def get_queryset(self):
        qs = Assignment.objects.select_related("subject").order_by("due_at")
        p = self.request.query_params

        if p.get("subject"): qs = qs.filter(subject_id = p["subject"])
        if p.get("status"): qs = qs.filter(status = p["status"].upper())
        now = timezone.now()
        if p.get("upcoming") == "true": qs = qs.filter(status = "PENDING", due_at__gte = now)
        if p.get("overdue") == "true": qs = qs.filter(status = "PENDING", due_at__lt =now)
        return qs



class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.none()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["subject__name"]
    ordering_fields = ["graded_at", "value"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

        qs = Grade.objects.select_related ("user", "subject").order_by("-graded_at")
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(user=user)
        p = self.request.query_params

        if p.get("subject"):
            qs = qs.filter(subject_id = p["subject"])
        if p.get("min"):
            qs = qs.filter(value__gte = float(p["min"]))
        if p.get("max"):
            qs = qs.filter(value__lte = float(p["max"]))
        return qs


    @action(detail = False, methods = ["GET"])
    def summary(self, request):

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
    queryset = Attendance.objects.none()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset

        qs = Attendance.objects.select_related("user", "subject")
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(user=user)
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
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    queryset = Event.objects.select_related("owner", "subject").order_by("starts_at")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(owner=user)
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



@extend_schema(
    request = RegisterSerializer,
    responses = {201: OpenApiResponse(response = dict, description = "Created and returns JWT tokens")},
    description = "Create a new user account and return access/refresh JWT tokens. "
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data = request.data)
    try:

        serializer.is_valid(raise_exception = True)
        user = serializer.save()
    except Exception as e:
        return Response({"error": str(e)}, status =400)
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
            status = 201,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
    })

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Enroll/Unenroll the current user; list my enrollments.
    """

    queryset = Enrollment.objects.none()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        qs = Enrollment.objects.select_related ("subject", "user")
        if not self.request.user.is_staff:
            qs = qs.filter(user = self.request.user)
        return qs

    def perform_create(self, serializer):
        try:
            serializer.save(user = self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"subject": "You are already enrolled in this subject. "})


    def perform_destroy(self, instance):
        if self.request.user.is_staff or instance.user_id == self.request.user.id:
            return super().perform_destroy(instance)
        return Response({"detail" : "Not allowed"}, status = 403)

