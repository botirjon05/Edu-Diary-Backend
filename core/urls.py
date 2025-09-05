from os.path import basename

from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, AssignmentViewSet, GradeViewSet

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename = "subject")
router.register(r"assignments", AssignmentViewSet, basename = "assignments")
router.register(r"grades", GradeViewSet, basename = "grade")

urlpatterns = router.urls