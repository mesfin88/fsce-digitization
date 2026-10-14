from rest_framework.permissions import BasePermission
class HasAnyRole(BasePermission):
    allowed_roles = ()
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.roles.filter(code__in=self.allowed_roles).exists()))
def roles(*codes):
    return type("RolePermission_"+"_".join(codes),(HasAnyRole,),{"allowed_roles":codes})
