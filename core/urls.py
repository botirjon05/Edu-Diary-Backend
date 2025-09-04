from os.path import basename

from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, AssignmentViewSet

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename = "subject")
router.register(r"asignments", AssignmentViewSet, basename = "assignments")

urlpatterns = router.urls