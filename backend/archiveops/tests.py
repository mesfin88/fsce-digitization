from django.test import TestCase
from rest_framework.exceptions import ValidationError
from accounts.models import User,Role
from .models import CaseRecord,PhysicalFile,ArchiveLocation,Batch
from .services import add_batch_item,dispatch_batch,receive_batch

class BatchWorkflowTests(TestCase):
    def setUp(self):
        ar,_=Role.objects.get_or_create(code="ARCHIVE",defaults={"name":"Archive Worker"})
        sr,_=Role.objects.get_or_create(code="SCANNER",defaults={"name":"Scanner"})
        self.archive=User.objects.create_user(username="arch2",password="test-password-123"); self.archive.roles.add(ar)
        self.scanner=User.objects.create_user(username="scan2",password="test-password-123"); self.scanner.roles.add(sr)
        self.loc=ArchiveLocation.objects.create(code="SHELF-C")
        case=CaseRecord.objects.create(case_number="CASE-2",registered_by=self.archive)
        self.pf=PhysicalFile.objects.create(case=case,location=self.loc,inventory_page_count=12,registered_by=self.archive)
        self.batch=Batch.objects.create(batch_number="B-002",source_location=self.loc,created_by=self.archive)
        add_batch_item(batch_id=self.batch.pk,physical_file_id=self.pf.pk,scanner=self.scanner,actor=self.archive)
    def test_dispatch_receive(self):
        dispatch_batch(batch_id=self.batch.pk,actor=self.archive)
        self.batch.refresh_from_db(); self.pf.refresh_from_db()
        self.assertEqual(self.batch.status,Batch.Status.DISPATCHED)
        self.assertEqual(self.pf.status,PhysicalFile.Status.IN_TRANSIT)
        receive_batch(batch_id=self.batch.pk,actor=self.archive,exception_notes="Cover damaged")
        self.batch.refresh_from_db(); self.pf.refresh_from_db()
        self.assertEqual(self.batch.status,Batch.Status.RECEIVED)
        self.assertEqual(self.pf.status,PhysicalFile.Status.WITH_SCANNER)
        self.assertEqual(self.batch.exception_notes,"Cover damaged")
    def test_empty_batch_cannot_dispatch(self):
        empty=Batch.objects.create(batch_number="EMPTY",source_location=self.loc,created_by=self.archive)
        with self.assertRaises(ValidationError): dispatch_batch(batch_id=empty.pk,actor=self.archive)
