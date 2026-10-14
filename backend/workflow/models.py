from django.conf import settings
from django.db import models
from archiveops.models import PhysicalFile

class DigitalAsset(models.Model):
    class Kind(models.TextChoices):
        JUDGE="JUDGE","Judge PDF"
        OTHER="OTHER","Other PDF"
    physical_file=models.ForeignKey(PhysicalFile,on_delete=models.PROTECT,related_name="digital_assets")
    kind=models.CharField(max_length=10,choices=Kind.choices)
    version=models.PositiveIntegerField(default=1)
    storage_path=models.CharField(max_length=1024)
    page_count=models.PositiveIntegerField()
    sha256=models.CharField(max_length=64)
    edited=models.BooleanField(default=False)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="digital_assets")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["physical_file","kind","version"],name="uniq_asset_kind_version")]

class QualityCheck(models.Model):
    class Result(models.TextChoices):
        PASS="PASS","Pass"
        FAIL="FAIL","Fail"
    physical_file=models.ForeignKey(PhysicalFile,on_delete=models.PROTECT,related_name="quality_checks")
    judge_asset=models.ForeignKey(DigitalAsset,on_delete=models.PROTECT,related_name="judge_qc_checks")
    other_asset=models.ForeignKey(DigitalAsset,on_delete=models.PROTECT,related_name="other_qc_checks")
    result=models.CharField(max_length=8,choices=Result.choices)
    notes=models.TextField(blank=True)
    checked_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="quality_checks")
    checked_at=models.DateTimeField(auto_now_add=True)

class RepositorySubmission(models.Model):
    class Status(models.TextChoices):
        PRIVATE="PRIVATE","Private / unpublished"
        PUBLISHED="PUBLISHED","Published"
        FAILED="FAILED","Submission failed"
    physical_file=models.ForeignKey(PhysicalFile,on_delete=models.PROTECT,related_name="repository_submissions")
    qc=models.ForeignKey(QualityCheck,on_delete=models.PROTECT,related_name="submissions")
    dspace_uuid=models.CharField(max_length=80,blank=True,db_index=True)
    dspace_handle=models.CharField(max_length=120,blank=True)
    status=models.CharField(max_length=12,choices=Status.choices,default=Status.PRIVATE)
    is_private=models.BooleanField(default=True)
    submitted_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="repository_submissions")
    submitted_at=models.DateTimeField(auto_now_add=True)
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name="approved_publications")
    approved_at=models.DateTimeField(null=True,blank=True)
    published_at=models.DateTimeField(null=True,blank=True)
    last_error=models.TextField(blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["physical_file","qc"],name="uniq_submission_per_qc")]

class AuditEvent(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="audit_events")
    action=models.CharField(max_length=80)
    object_type=models.CharField(max_length=80)
    object_id=models.CharField(max_length=80)
    details=models.JSONField(default=dict,blank=True)
    occurred_at=models.DateTimeField(auto_now_add=True)
