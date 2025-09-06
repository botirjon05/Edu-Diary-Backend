from wsgiref.validate import validator

from rest_framework import serializers
from .models import Subject, Assignment, Grade, Attendance, Event
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

User = get_user_model()

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
    owner_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ["id", "owner", "owner_name", "subject", "subject_name", "title", "location", "starts_at", "ends_at", "created_at"]
    @extend_schema_field(OpenApiTypes.STR)
    def get_owner_name(self,obj):
        return obj.owner.username if getattr(obj, "owner", None) else None

    @extend_schema_field(OpenApiTypes.STR)
    def get_subject_name(self, obj):
        return obj.subject.name if getattr(obj, "subject", None) else None

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length = 150,
        validators = [UniqueValidator(queryset = User.objects.all(), message = "Username already taken")],
    )
    email = serializers.EmailField(required = False, allow_blank =True)

    password = serializers.CharField(write_only = True, required = True, validators = [validate_password])
    password2 = serializers.CharField(write_only = True, required = True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password", "password2")


    def validate(self, attrs):
         if attrs["password"] != attrs["password2"]:
               raise serializers.ValidationError({"password2": "Password fields didn't match."})
         return attrs

    def validate_email(self, value: str):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        user = User.objects.create_user(
            username = validated_data["username"],
            email = validated_data.get("email") or "",
            password = password,
            first_name = validated_data.get("first_name", ""),
            last_name = validated_data.get("last_name", ""),
        )
        return user