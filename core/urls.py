from os.path import basename
from django.urls import path


from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, AssignmentViewSet, GradeViewSet, AttendanceViewSet, EventViewSet, register

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename = "subject")
router.register(r"assignments", AssignmentViewSet, basename = "assignments")
router.register(r"grades", GradeViewSet, basename = "grade")
router.register(r"attendance", AttendanceViewSet, basename = "attendance")
router.register(r"events", EventViewSet, basename = "event")

urlpatterns = router.urls + [
    path("auth/register/", register, name = "register"),
]