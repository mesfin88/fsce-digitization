from django.test import TestCase
from rest_framework.exceptions import PermissionDenied,ValidationError
from accounts.models import User,Role
from archiveops.models import CaseRecord,PhysicalFile,ArchiveLocation
from .models import DigitalAsset,QualityCheck,RepositorySubmission
from .services import approve_publication

class FakeGateway:
    def publish_item(self,*,submission): return {"is_private":False}
class PublicationTests(TestCase):
    def setUp(self):
        hr,_=Role.objects.get_or_create(code="DEPARTMENT_HEAD",defaults={"name":"Head"})
        sr,_=Role.objects.get_or_create(code="SYSTEM_ADMIN",defaults={"name":"System Admin"})
        qr,_=Role.objects.get_or_create(code="QC_REPOSITORY",defaults={"name":"QC"})
        self.head=User.objects.create_user(username="head",password="test-password-123"); self.head.roles.add(hr)
        self.admin=User.objects.create_user(username="sysadmin",password="test-password-123"); self.admin.roles.add(sr)
        self.qcuser=User.objects.create_user(username="qc",password="test-password-123"); self.qcuser.roles.add(qr)
        loc=ArchiveLocation.objects.create(code="QC-SHELF")
        case=CaseRecord.objects.create(case_number="CASE-QC",registered_by=self.qcuser)
        self.pf=PhysicalFile.objects.create(case=case,location=loc,inventory_page_count=2,registered_by=self.qcuser)
        j=DigitalAsset.objects.create(physical_file=self.pf,kind="JUDGE",version=1,storage_path="/private/judge.pdf",page_count=1,sha256="a"*64,created_by=self.qcuser)
        o=DigitalAsset.objects.create(physical_file=self.pf,kind="OTHER",version=1,storage_path="/private/other.pdf",page_count=1,sha256="b"*64,created_by=self.qcuser)
        self.qc=QualityCheck.objects.create(physical_file=self.pf,judge_asset=j,other_asset=o,result="PASS",checked_by=self.qcuser)
    def make_submission(self):
        return RepositorySubmission.objects.create(physical_file=self.pf,qc=self.qc,dspace_uuid="uuid",status="PRIVATE",is_private=True,submitted_by=self.qcuser)
    def test_sysadmin_cannot_approve(self):
        item=self.make_submission()
        with self.assertRaises(PermissionDenied): approve_publication(submission_id=item.pk,actor=self.admin,gateway=FakeGateway())
    def test_head_approval_requires_remote_confirmation(self):
        item=self.make_submission()
        result=approve_publication(submission_id=item.pk,actor=self.head,gateway=FakeGateway())
        self.assertEqual(result.status,RepositorySubmission.Status.PUBLISHED)
        self.assertFalse(result.is_private)
    def test_remote_failure_keeps_private(self):
        class BadGateway:
            def publish_item(self,*,submission): return {"is_private":True}
        item=self.make_submission()
        with self.assertRaises(ValidationError): approve_publication(submission_id=item.pk,actor=self.head,gateway=BadGateway())
        item.refresh_from_db()
        self.assertEqual(item.status,RepositorySubmission.Status.PRIVATE)
        self.assertTrue(item.is_private)
