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
        if request.user.role != 'doctor':
            return False
        # Check doctor approval status
        try:
            return request.user.doctor_profile.is_approved
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        """Doktor sadece kendisine atanmis hastalarin verisine erisebilir."""
        if request.user.is_superuser:
            return True
        if request.user.role != 'doctor':
            return False

        # obj bir User (hasta) ise
        if hasattr(obj, 'patient_profile'):
            return obj.patient_profile.assigned_doctor_id == request.user.id

        # obj'nin user veya patient fieldi varsa
        patient_user = getattr(obj, 'patient', None) or getattr(obj, 'user', None)
        if patient_user and hasattr(patient_user, 'patient_profile'):
            return patient_user.patient_profile.assigned_doctor_id == request.user.id

        return True  # Hasta ile iliskili olmayan objeler icin izin ver


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

    def has_object_permission(self, request, view, obj):
        """Bakici sadece atandigi hastalarin verisine erisebilir."""
        if request.user.is_superuser:
            return True
        if request.user.role != 'caregiver':
            return False

        try:
            caregiver_profile = request.user.caregiver_profile
        except Exception:
            return False

        # obj bir User (hasta) ise
        patient_user = obj
        if hasattr(obj, 'patient') and hasattr(obj.patient, 'role'):
            patient_user = obj.patient
        elif hasattr(obj, 'user') and hasattr(obj.user, 'role'):
            patient_user = obj.user

        if hasattr(patient_user, 'role') and patient_user.role == 'patient':
            return caregiver_profile.patients.filter(id=patient_user.id).exists()

        return True


class IsRelative(permissions.BasePermission):
    """Allow access only to approved relatives."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.user.role != 'relative':
            return False

        # Onaylanmis relative mi kontrol et
        try:
            return request.user.relative_profile.is_approved
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        """Akraba sadece atandigi hastanin verisine erisebilir (salt okunur)."""
        if request.user.is_superuser:
            return True

        # Sadece GET isteklerine izin ver (salt okunur)
        if request.method not in permissions.SAFE_METHODS:
            return False

        try:
            relative_profile = request.user.relative_profile
            if not relative_profile.is_approved:
                return False
        except Exception:
            return False

        # obj bir User (hasta) ise
        patient_user = obj
        if hasattr(obj, 'patient') and hasattr(obj.patient, 'role'):
            patient_user = obj.patient
        elif hasattr(obj, 'user') and hasattr(obj.user, 'role'):
            patient_user = obj.user

        if hasattr(patient_user, 'role') and patient_user.role == 'patient':
            return relative_profile.patient_id == patient_user.id

        return True


class IsPatientOrCaregiver(permissions.BasePermission):
    """Allow access to patients (own data) or caregivers (assigned patients)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in ('patient', 'caregiver')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        # Hasta kendi verisine erisiyor
        if request.user.role == 'patient':
            patient_user = getattr(obj, 'patient', None) or getattr(obj, 'user', None) or obj
            if hasattr(patient_user, 'id'):
                return patient_user.id == request.user.id
            return True

        # Bakici atandigi hastanin verisine erisiyor
        if request.user.role == 'caregiver':
            try:
                caregiver_profile = request.user.caregiver_profile
            except Exception:
                return False

            patient_user = getattr(obj, 'patient', None) or getattr(obj, 'user', None) or obj
            if hasattr(patient_user, 'id'):
                return caregiver_profile.patients.filter(id=patient_user.id).exists()

        return True


class IsPatientOrCaregiverOrRelative(permissions.BasePermission):
    """Allow access to patients, caregivers, or approved relatives."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.user.role == 'relative':
            try:
                return request.user.relative_profile.is_approved
            except Exception:
                return False
        return request.user.role in ('patient', 'caregiver')
