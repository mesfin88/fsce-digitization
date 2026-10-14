from django.core.management.base import BaseCommand
from accounts.models import Role
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        roles={"ARCHIVE":"Archive Worker","SCANNER":"Scanner","EDITOR":"Editor",
        "QC_REPOSITORY":"QC and Repository Officer","DEPARTMENT_HEAD":"Digitization Department Head",
        "SYSTEM_ADMIN":"System Administrator"}
        for code,name in roles.items(): Role.objects.update_or_create(code=code,defaults={"name":name})
        self.stdout.write(self.style.SUCCESS("Standard roles created/verified."))
