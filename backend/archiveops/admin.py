from django.contrib import admin
from .models import CaseRecord,PhysicalFile,ArchiveLocation,Batch,BatchItem,FileMovement
admin.site.register(CaseRecord)
admin.site.register(PhysicalFile)
admin.site.register(ArchiveLocation)
admin.site.register(Batch)
admin.site.register(BatchItem)
@admin.register(FileMovement)
class MovementAdmin(admin.ModelAdmin):
    list_display=("occurred_at","physical_file","action","actor")
    readonly_fields=("physical_file","batch","action","from_location","to_location","actor","occurred_at","notes")
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
