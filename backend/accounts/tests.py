from django.test import TestCase
from django.db import IntegrityError,transaction
from rest_framework.test import APIClient
from accounts.models import User,Role
from archiveops.models import CaseRecord,PhysicalFile,ArchiveLocation,Batch
from archiveops.services import add_batch_item

class IdentityAndRolesTests(TestCase):
    def setUp(self):
        self.ar,_=Role.objects.get_or_create(code="ARCHIVE",defaults={"name":"Archive Worker"})
        self.sr,_=Role.objects.get_or_create(code="SCANNER",defaults={"name":"Scanner"})
        self.archive=User.objects.create_user(username="arch",password="test-password-123")
        self.archive.roles.add(self.ar)
        self.scanner=User.objects.create_user(username="scan",password="test-password-123")
        self.scanner.roles.add(self.sr)
        self.loc=ArchiveLocation.objects.create(code="SHELF-A")
        self.case=CaseRecord.objects.create(case_number="00/0001/205642",registered_by=self.archive)
        self.pf=PhysicalFile.objects.create(case=self.case,location=self.loc,inventory_page_count=83,registered_by=self.archive)
    def test_one_physical_file_per_case(self):
        other=ArchiveLocation.objects.create(code="SHELF-B")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PhysicalFile.objects.create(case=self.case,location=other,inventory_page_count=1,registered_by=self.archive)
    def test_manual_scanner_assignment_is_saved(self):
        batch=Batch.objects.create(batch_number="B-001",source_location=self.loc,created_by=self.archive)
        item=add_batch_item(batch_id=batch.pk,physical_file_id=self.pf.pk,scanner=self.scanner,actor=self.archive)
        self.assertEqual(item.assigned_scanner_id,self.scanner.pk)
        self.assertEqual(item.inventory_page_count_snapshot,83)
    def test_scanner_cannot_register_case(self):
        client=APIClient()
        client.force_authenticate(self.scanner)
        response=client.post("/api/cases/",{"case_number":"X-1"},format="json")
        self.assertEqual(response.status_code,403)
