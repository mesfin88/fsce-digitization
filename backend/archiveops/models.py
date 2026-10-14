from django.conf import settings
from django.db import models
from django.utils import timezone

class CaseRecord(models.Model):
    case_number = models.CharField(max_length=40, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="registered_cases")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.case_number

class ArchiveLocation(models.Model):
    code = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.code

class PhysicalFile(models.Model):
    class Status(models.TextChoices):
        ON_SHELF="ON_SHELF","On shelf"
        PREPARING="PREPARING","Preparing for dispatch"
        IN_TRANSIT="IN_TRANSIT","In transit"
        WITH_SCANNER="WITH_SCANNER","With scanner"
        WITH_EDITOR="WITH_EDITOR","With editor"
        RETURN_PENDING="RETURN_PENDING","Return pending"
        RETURNED="RETURNED","Returned to shelf"
        EXCEPTION="EXCEPTION","Exception"
    # Database constraint: exactly one physical file per case number.
    case = models.OneToOneField(CaseRecord,on_delete=models.PROTECT,related_name="physical_file")
    location = models.ForeignKey(ArchiveLocation,on_delete=models.PROTECT,related_name="physical_files")
    inventory_page_count = models.PositiveIntegerField()
    status = models.CharField(max_length=24,choices=Status.choices,default=Status.ON_SHELF)
    condition_notes = models.TextField(blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="registered_physical_files")
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.case.case_number

class Batch(models.Model):
    class Status(models.TextChoices):
        DRAFT="DRAFT","Draft"
        DISPATCHED="DISPATCHED","Dispatched"
        RECEIVED="RECEIVED","Received"
        CLOSED="CLOSED","Closed"
    batch_number = models.CharField(max_length=40,unique=True)
    source_location = models.ForeignKey(ArchiveLocation,on_delete=models.PROTECT,related_name="outgoing_batches")
    status = models.CharField(max_length=16,choices=Status.choices,default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_batches")
    dispatched_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name="dispatched_batches")
    dispatched_at = models.DateTimeField(null=True,blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name="received_batches")
    received_at = models.DateTimeField(null=True,blank=True)
    exception_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BatchItem(models.Model):
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE,related_name="items")
    physical_file = models.ForeignKey(PhysicalFile,on_delete=models.PROTECT,related_name="batch_items")
    # Explicit manual assignment by an authorized user.
    assigned_scanner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="scanner_assignments")
    inventory_page_count_snapshot = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["batch","physical_file"],name="uniq_file_per_batch")]

class FileMovement(models.Model):
    physical_file = models.ForeignKey(PhysicalFile,on_delete=models.PROTECT,related_name="movements")
    batch = models.ForeignKey(Batch,null=True,blank=True,on_delete=models.PROTECT,related_name="movements")
    action = models.CharField(max_length=24)
    from_location = models.CharField(max_length=120,blank=True)
    to_location = models.CharField(max_length=120,blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="file_movements")
    occurred_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
