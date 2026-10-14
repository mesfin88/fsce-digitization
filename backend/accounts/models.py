from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    class Code(models.TextChoices):
        ARCHIVE="ARCHIVE","Archive Worker"
        SCANNER="SCANNER","Scanner"
        EDITOR="EDITOR","Editor"
        QC_REPOSITORY="QC_REPOSITORY","QC and Repository Officer"
        DEPARTMENT_HEAD="DEPARTMENT_HEAD","Digitization Department Head"
        SYSTEM_ADMIN="SYSTEM_ADMIN","System Administrator"
    code = models.CharField(max_length=32, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class User(AbstractUser):
    roles = models.ManyToManyField(Role, blank=True, related_name="users")
    def has_role(self, code):
        return self.is_superuser or self.roles.filter(code=code).exists()
    def role_codes(self):
        return list(self.roles.values_list("code", flat=True))
