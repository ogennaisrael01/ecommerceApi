from rest_framework.permissions import BasePermission


class IsVendorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "Vendor" or request.user.is_staff
    
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff