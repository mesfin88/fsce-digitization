from rest_framework import serializers
from .models import DigitalAsset,QualityCheck,RepositorySubmission
class DigitalAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model=DigitalAsset
        fields=["id","physical_file","kind","version","storage_path","page_count","sha256","edited","created_by","created_at"]
        read_only_fields=["id","created_by","created_at"]
class QualityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model=QualityCheck
        fields=["id","physical_file","judge_asset","other_asset","result","notes","checked_by","checked_at"]
        read_only_fields=["id","checked_by","checked_at"]
class SubmissionSerializer(serializers.ModelSerializer):
    case_number=serializers.CharField(source="physical_file.case.case_number",read_only=True)
    class Meta:
        model=RepositorySubmission
        fields=["id","physical_file","case_number","qc","dspace_uuid","dspace_handle","status","is_private","submitted_by","submitted_at","approved_by","approved_at","published_at","last_error"]
        read_only_fields=["id","dspace_uuid","dspace_handle","status","is_private","submitted_by","submitted_at","approved_by","approved_at","published_at","last_error"]
