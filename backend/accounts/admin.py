from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Digitization roles", {"fields":("roles",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Digitization roles", {"fields":("roles",)}),)
admin.site.register(Role)
