from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models import Role
from .models import Batch, BatchItem, PhysicalFile, FileMovement

@transaction.atomic
def add_batch_item(*,batch_id,physical_file_id,scanner,actor):
    batch=Batch.objects.select_for_update().get(pk=batch_id)
    if batch.status != Batch.Status.DRAFT: raise ValidationError("Only draft batches can be edited.")
    if not scanner.is_active or (not scanner.is_superuser and not scanner.roles.filter(code=Role.Code.SCANNER).exists()):
        raise ValidationError("Select an active user with the SCANNER role.")
    pf=PhysicalFile.objects.select_for_update().select_related("case","location").get(pk=physical_file_id)
    if pf.status not in (PhysicalFile.Status.ON_SHELF,PhysicalFile.Status.PREPARING):
        raise ValidationError("Physical file is not available for a new batch.")
    if pf.location_id != batch.source_location_id: raise ValidationError("File must be at the batch source location.")
    if BatchItem.objects.filter(physical_file=pf,batch__status__in=[Batch.Status.DRAFT,Batch.Status.DISPATCHED]).exists():
        raise ValidationError("Physical file is already assigned to an open batch.")
    item=BatchItem.objects.create(batch=batch,physical_file=pf,assigned_scanner=scanner,
                                  inventory_page_count_snapshot=pf.inventory_page_count)
    pf.status=PhysicalFile.Status.PREPARING
    pf.save(update_fields=["status","updated_at"])
    FileMovement.objects.create(physical_file=pf,batch=batch,action="BATCH_ASSIGNED",
        from_location=pf.location.code,to_location=f"Batch {batch.batch_number}",actor=actor,
        notes=f"Manually assigned to scanner {scanner.username}")
    return item

@transaction.atomic
def dispatch_batch(*,batch_id,actor):
    batch=Batch.objects.select_for_update().get(pk=batch_id)
    if batch.status != Batch.Status.DRAFT: raise ValidationError("Only draft batches can be dispatched.")
    items=list(batch.items.select_related("physical_file","physical_file__case","physical_file__location"))
    if not items: raise ValidationError("Cannot dispatch an empty batch.")
    now=timezone.now()
    for item in items:
        pf=PhysicalFile.objects.select_for_update().get(pk=item.physical_file_id)
        if pf.status != PhysicalFile.Status.PREPARING: raise ValidationError(f"{pf.case.case_number} is not ready.")
        pf.status=PhysicalFile.Status.IN_TRANSIT
        pf.save(update_fields=["status","updated_at"])
        FileMovement.objects.create(physical_file=pf,batch=batch,action="DISPATCHED",
            from_location=pf.location.code,to_location=f"Scanner {item.assigned_scanner.username}",actor=actor,occurred_at=now)
    batch.status=Batch.Status.DISPATCHED
    batch.dispatched_by=actor
    batch.dispatched_at=now
    batch.save(update_fields=["status","dispatched_by","dispatched_at"])
    return batch

@transaction.atomic
def receive_batch(*,batch_id,actor,exception_notes=""):
    batch=Batch.objects.select_for_update().get(pk=batch_id)
    if batch.status != Batch.Status.DISPATCHED: raise ValidationError("Only dispatched batches can be received.")
    now=timezone.now()
    for item in batch.items.select_related("physical_file","physical_file__case"):
        pf=PhysicalFile.objects.select_for_update().get(pk=item.physical_file_id)
        pf.status=PhysicalFile.Status.WITH_SCANNER
        pf.save(update_fields=["status","updated_at"])
        FileMovement.objects.create(physical_file=pf,batch=batch,action="RECEIVED",
            from_location=f"Transit / {batch.batch_number}",to_location=f"Scanner {item.assigned_scanner.username}",
            actor=actor,occurred_at=now,notes=exception_notes)
    batch.status=Batch.Status.RECEIVED
    batch.received_by=actor
    batch.received_at=now
    batch.exception_notes=exception_notes
    batch.save(update_fields=["status","received_by","received_at","exception_notes"])
    return batch
