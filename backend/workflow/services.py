from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError
from accounts.models import Role
from .models import DigitalAsset,QualityCheck,RepositorySubmission,AuditEvent

class DspaceGateway:
    # Implement for the exact DSpace deployment. Never fake success.
    def create_private_item(self,*,physical_file,qc):
        raise NotImplementedError("Configure private DSpace workspace integration first.")
    def publish_item(self,*,submission):
        raise NotImplementedError("Configure and verify the DSpace publication transition first.")

@transaction.atomic
def record_qc(*,physical_file,judge_asset,other_asset,result,notes,actor):
    if not actor.has_role(Role.Code.QC_REPOSITORY): raise PermissionDenied("QC and Repository Officer role required.")
    if judge_asset.physical_file_id!=physical_file.id or other_asset.physical_file_id!=physical_file.id:
        raise ValidationError("Both assets must belong to the selected physical file.")
    if judge_asset.kind!="JUDGE" or other_asset.kind!="OTHER": raise ValidationError("Select Judge and Other PDF assets.")
    if not judge_asset.sha256 or not other_asset.sha256: raise ValidationError("Both assets need verified SHA-256 hashes.")
    qc=QualityCheck.objects.create(physical_file=physical_file,judge_asset=judge_asset,other_asset=other_asset,
                                   result=result,notes=notes,checked_by=actor)
    AuditEvent.objects.create(actor=actor,action="QC_RECORDED",object_type="QualityCheck",object_id=str(qc.pk),
                              details={"result":result,"physical_file_id":physical_file.pk})
    return qc

@transaction.atomic
def record_private_submission(*,qc,actor,gateway):
    if not actor.has_role(Role.Code.QC_REPOSITORY): raise PermissionDenied("QC and Repository Officer role required.")
    if qc.result!=QualityCheck.Result.PASS: raise ValidationError("Only passed QC can be submitted.")
    existing=RepositorySubmission.objects.filter(qc=qc).first()
    if existing: return existing
    remote=gateway.create_private_item(physical_file=qc.physical_file,qc=qc)
    if not remote or not remote.get("uuid") or remote.get("is_private") is not True:
        raise ValidationError("DSpace did not confirm a private item; no successful submission was recorded.")
    item=RepositorySubmission.objects.create(physical_file=qc.physical_file,qc=qc,dspace_uuid=remote["uuid"],
        dspace_handle=remote.get("handle",""),status=RepositorySubmission.Status.PRIVATE,is_private=True,submitted_by=actor)
    AuditEvent.objects.create(actor=actor,action="DSPACE_PRIVATE_SUBMISSION",object_type="RepositorySubmission",
        object_id=str(item.pk),details={"dspace_uuid":item.dspace_uuid})
    return item

@transaction.atomic
def approve_publication(*,submission_id,actor,gateway):
    # System admin alone is deliberately insufficient.
    if not actor.has_role(Role.Code.DEPARTMENT_HEAD): raise PermissionDenied("Department Head role required.")
    item=RepositorySubmission.objects.select_for_update().select_related("qc").get(pk=submission_id)
    if item.qc.result!=QualityCheck.Result.PASS: raise ValidationError("Passed QC is required.")
    if item.status!=RepositorySubmission.Status.PRIVATE or not item.is_private:
        raise ValidationError("Only a verified private item can be approved.")
    remote=gateway.publish_item(submission=item)
    if not remote or remote.get("is_private") is not False:
        raise ValidationError("DSpace did not confirm publication; local state remains private.")
    now=timezone.now()
    item.status=RepositorySubmission.Status.PUBLISHED
    item.is_private=False
    item.approved_by=actor
    item.approved_at=now
    item.published_at=now
    item.save(update_fields=["status","is_private","approved_by","approved_at","published_at"])
    AuditEvent.objects.create(actor=actor,action="PUBLICATION_APPROVED_AND_PUBLISHED",object_type="RepositorySubmission",
        object_id=str(item.pk),details={"dspace_uuid":item.dspace_uuid})
    return item
