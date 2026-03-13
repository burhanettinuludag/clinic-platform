from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == 'patient'


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == 'doctor'


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == 'admin'


class IsCaregiver(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == 'caregiver'


class IsRelative(permissions.BasePermission):
    """Allow access only to approved relatives."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == 'relative'


class IsPatientOrCaregiver(permissions.BasePermission):
    """Allow access to patients (own data) or caregivers (assigned patients)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in ('patient', 'caregiver')


class IsPatientOrCaregiverOrRelative(permissions.BasePermission):
    """Allow access to patients, caregivers, or approved relatives."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in ('patient', 'caregiver', 'relative')
