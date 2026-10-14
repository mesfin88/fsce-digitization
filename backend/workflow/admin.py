from django.contrib import admin
from .models import DigitalAsset,QualityCheck,RepositorySubmission,AuditEvent
admin.site.register(DigitalAsset)
admin.site.register(QualityCheck)
admin.site.register(RepositorySubmission)
@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display=("occurred_at","actor","action","object_type","object_id")
    readonly_fields=("actor","action","object_type","object_id","details","occurred_at")
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
