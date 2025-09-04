from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Subject
from .serializers import SubjectSerializer

class SubjectViewSet (viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]



