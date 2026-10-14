from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from accounts.views import CurrentUserView
from archiveops.views import CaseViewSet, PhysicalFileViewSet, ArchiveLocationViewSet, BatchViewSet, ScannerUsersView
from workflow.views import DigitalAssetViewSet, QualityCheckViewSet, RepositorySubmissionViewSet

router = DefaultRouter()
router.register("cases", CaseViewSet, basename="case")
router.register("physical-files", PhysicalFileViewSet, basename="physical-file")
router.register("archive-locations", ArchiveLocationViewSet, basename="archive-location")
router.register("batches", BatchViewSet, basename="batch")
router.register("digital-assets", DigitalAssetViewSet, basename="digital-asset")
router.register("qc", QualityCheckViewSet, basename="qc")
router.register("submissions", RepositorySubmissionViewSet, basename="submission")
urlpatterns = [
 path("admin/", admin.site.urls),
 path("api/me/", CurrentUserView.as_view()),
 path("api/scanner-users/", ScannerUsersView.as_view()),
 path("api/", include(router.urls)),
 path("api-auth/", include("rest_framework.urls")),
]
