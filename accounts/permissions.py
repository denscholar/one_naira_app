from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_admin:
            return True
        return False


class is_support_level1(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_support_level1:
            return True
        return False


class is_support_level2(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_support_level2:
            return True
        return False


class isAccountant1(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_accountant1:
            return True
        return False


class isAccountant2(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_accountant2:
            return True
        return False
