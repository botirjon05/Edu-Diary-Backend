from rest_framework import serializers
from .models import Subject, Assignment, Grade, Attendance, Event

class SubjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "code", "name", "color", "created_at"]

class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source = "subject.name")
    class Meta:
        model = Assignment
        fields = ["id", "subject", "subject_name", "title", "description", "due_at", "status", "created_at", "updated_at"]

class GradeSerializer (serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source = "subject.name")
    user_name = serializers.ReadOnlyField(source = "user.username")
    class Meta:

        model = Grade
        fields = ["id", "user", "user_name", "subject", "subject_name", "value", "credits", "graded_at"]

class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source = "user.username")
    subject_name = serializers.ReadOnlyField(source = "subject.name")
    class Meta:
        model = Attendance
        fields = ["id", "user", "user_name", "subject", "subject_name", "date", "status"]

class EventSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source = "owner.username")
    subject_name = serializers.ReadOnlyField(source = "subject.name")
    class Meta:
        model = Event
        fields = ["id", "owner", "owner_name", "subject", "subject_name", "title", "location", "start_at", "ends_at", "created_at"]