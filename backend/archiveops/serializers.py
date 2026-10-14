from rest_framework import serializers
from .models import CaseRecord, PhysicalFile, ArchiveLocation, Batch, BatchItem
class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=CaseRecord
        fields=["id","case_number","description","registered_by","created_at"]
        read_only_fields=["id","registered_by","created_at"]
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=ArchiveLocation
        fields=["id","code","description","active"]
class PhysicalFileSerializer(serializers.ModelSerializer):
    case_number=serializers.CharField(source="case.case_number",read_only=True)
    location_code=serializers.CharField(source="location.code",read_only=True)
    class Meta:
        model=PhysicalFile
        fields=["id","case","case_number","location","location_code","inventory_page_count","status","condition_notes","registered_by","registered_at"]
        read_only_fields=["id","status","registered_by","registered_at"]
class BatchItemSerializer(serializers.ModelSerializer):
    case_number=serializers.CharField(source="physical_file.case.case_number",read_only=True)
    scanner_username=serializers.CharField(source="assigned_scanner.username",read_only=True)
    class Meta:
        model=BatchItem
        fields=["id","physical_file","case_number","assigned_scanner","scanner_username","inventory_page_count_snapshot"]
        read_only_fields=["id","inventory_page_count_snapshot"]
class BatchSerializer(serializers.ModelSerializer):
    items=BatchItemSerializer(many=True,read_only=True)
    class Meta:
        model=Batch
        fields=["id","batch_number","source_location","status","created_by","dispatched_by","dispatched_at","received_by","received_at","exception_notes","created_at","items"]
        read_only_fields=["id","status","created_by","dispatched_by","dispatched_at","received_by","received_at","created_at"]
