from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Role, User
from accounts.permissions import roles
from .models import CaseRecord,PhysicalFile,ArchiveLocation,Batch
from .serializers import CaseSerializer,PhysicalFileSerializer,LocationSerializer,BatchSerializer,BatchItemSerializer
from .services import add_batch_item,dispatch_batch,receive_batch
ARCHIVE_ROLES=[Role.Code.ARCHIVE,Role.Code.DEPARTMENT_HEAD,Role.Code.SYSTEM_ADMIN]
class CaseViewSet(viewsets.ModelViewSet):
    serializer_class=CaseSerializer
    queryset=CaseRecord.objects.select_related("registered_by").all().order_by("-created_at")
    permission_classes=[roles(*ARCHIVE_ROLES)]
    def perform_create(self,serializer): serializer.save(registered_by=self.request.user)
class PhysicalFileViewSet(viewsets.ModelViewSet):
    serializer_class=PhysicalFileSerializer
    queryset=PhysicalFile.objects.select_related("case","location","registered_by").all().order_by("-registered_at")
    permission_classes=[roles(*ARCHIVE_ROLES)]
    def perform_create(self,serializer): serializer.save(registered_by=self.request.user)
class ArchiveLocationViewSet(viewsets.ModelViewSet):
    serializer_class=LocationSerializer
    queryset=ArchiveLocation.objects.all().order_by("code")
    permission_classes=[roles(*ARCHIVE_ROLES)]
class BatchViewSet(viewsets.ModelViewSet):
    serializer_class=BatchSerializer
    queryset=Batch.objects.select_related("source_location","created_by").prefetch_related("items__physical_file__case","items__assigned_scanner").all().order_by("-created_at")
    permission_classes=[roles(*ARCHIVE_ROLES)]
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)
    @action(detail=True,methods=["post"],url_path="add_item")
    def add_item(self,request,pk=None):
        if not request.data.get("physical_file") or not request.data.get("scanner"):
            raise ValidationError("physical_file and scanner IDs are required.")
        try: scanner=User.objects.get(pk=request.data["scanner"],is_active=True)
        except (User.DoesNotExist,ValueError,TypeError): raise ValidationError({"scanner":"Active scanner user not found."})
        item=add_batch_item(batch_id=pk,physical_file_id=request.data["physical_file"],scanner=scanner,actor=request.user)
        return Response(BatchItemSerializer(item).data,status=status.HTTP_201_CREATED)
    @action(detail=True,methods=["post"])
    def dispatch(self,request,pk=None):
        return Response(self.get_serializer(dispatch_batch(batch_id=pk,actor=request.user)).data)
    @action(detail=True,methods=["post"])
    def receive(self,request,pk=None):
        return Response(self.get_serializer(receive_batch(batch_id=pk,actor=request.user,exception_notes=request.data.get("exceptions",""))).data)
class ScannerUsersView(APIView):
    permission_classes=[roles(*ARCHIVE_ROLES)]
    def get(self,request):
        qs=User.objects.filter(is_active=True,roles__code=Role.Code.SCANNER).distinct().order_by("username")
        return Response([{"id":u.id,"username":u.username,"roles":u.role_codes()} for u in qs])
