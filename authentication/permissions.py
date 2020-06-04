from rest_framework.permissions import BasePermission

from authentication.models import DataEntryAdmin, Citizen


# defines various permission levels available

class IsDataEntryAdmin(BasePermission):
    """
    Permission defined for checking the authenticated user is data entry admin or not
    """
    message = "You don't have enough privileges to access this API."

    def has_permission(self, request, view):
        if not request.user:
            return False

        if DataEntryAdmin.objects.filter(user=request.user).exists():
            return True
        return False


class IsCitizen(BasePermission):
    """
    Permission defined for checking the authenticated user is citizen or not
    """
    message = "You don't have enough privileges to access this API."

    def has_permission(self, request, view):
        if not request.user:
            return False

        if Citizen.objects.filter(user=request.user).exists():
            return True
        return False


class IsSuperUser(BasePermission):
    """
    Permission defined for checking the authenticated user is super user or not
    """
    message = "You don't have enough privileges to access this API."

    def has_permission(self, request, view):
        if not request.user:
            return False

        if request.user.is_staff and request.user.is_superuser:
            return True
        return False
