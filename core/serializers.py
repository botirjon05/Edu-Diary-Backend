from rest_framework import serializers
from .models import Subject, Assignment

class SubjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "code", "name", "color", "created_at"]

class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source = "subject.name")
    class Meta:
        model = Assignment
        fields = ["id", "subject", "subject_name", "title", "description", "due_at", "status", "created_at", "updated_at"]