from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from accounts.models import Role
from accounts.permissions import roles
from archiveops.models import PhysicalFile
from .models import DigitalAsset,QualityCheck,RepositorySubmission
from .serializers import DigitalAssetSerializer,QualityCheckSerializer,SubmissionSerializer
from .services import record_qc,record_private_submission,approve_publication,DspaceGateway

class DigitalAssetViewSet(viewsets.ModelViewSet):
    serializer_class=DigitalAssetSerializer
    queryset=DigitalAsset.objects.select_related("physical_file","created_by").all().order_by("-created_at")
    permission_classes=[roles(Role.Code.SCANNER,Role.Code.EDITOR,Role.Code.QC_REPOSITORY)]
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)

class QualityCheckViewSet(viewsets.ModelViewSet):
    serializer_class=QualityCheckSerializer
    queryset=QualityCheck.objects.select_related("physical_file","judge_asset","other_asset","checked_by").all().order_by("-checked_at")
    permission_classes=[roles(Role.Code.QC_REPOSITORY)]
    def create(self,request,*args,**kwargs):
        try:
            pf=PhysicalFile.objects.get(pk=request.data.get("physical_file"))
            judge=DigitalAsset.objects.get(pk=request.data.get("judge_asset"))
            other=DigitalAsset.objects.get(pk=request.data.get("other_asset"))
        except (PhysicalFile.DoesNotExist,DigitalAsset.DoesNotExist,TypeError,ValueError):
            raise ValidationError("Valid physical_file, judge_asset and other_asset IDs are required.")
        result=request.data.get("result")
        if result not in QualityCheck.Result.values: raise ValidationError({"result":"Use PASS or FAIL."})
        qc=record_qc(physical_file=pf,judge_asset=judge,other_asset=other,result=result,
                     notes=request.data.get("notes",""),actor=request.user)
        return Response(self.get_serializer(qc).data,status=status.HTTP_201_CREATED)

class RepositorySubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=SubmissionSerializer
    queryset=RepositorySubmission.objects.select_related("physical_file","physical_file__case","qc","submitted_by").all().order_by("-submitted_at")
    permission_classes=[roles(Role.Code.QC_REPOSITORY,Role.Code.DEPARTMENT_HEAD)]
    @action(detail=False,methods=["post"],url_path="create-private",permission_classes=[roles(Role.Code.QC_REPOSITORY)])
    def create_private(self,request):
        try: qc=QualityCheck.objects.get(pk=request.data.get("qc"))
        except (QualityCheck.DoesNotExist,TypeError,ValueError): raise ValidationError({"qc":"Valid QC ID is required."})
        item=record_private_submission(qc=qc,actor=request.user,gateway=DspaceGateway())
        return Response(self.get_serializer(item).data,status=status.HTTP_201_CREATED)
    @action(detail=True,methods=["post"],url_path="approve-publication",permission_classes=[roles(Role.Code.DEPARTMENT_HEAD)])
    def approve_publication(self,request,pk=None):
        item=approve_publication(submission_id=pk,actor=request.user,gateway=DspaceGateway())
        return Response(self.get_serializer(item).data)
