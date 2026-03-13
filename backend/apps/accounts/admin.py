from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PatientProfile, DoctorProfile, CaregiverProfile, RelativeProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'preferred_language')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified')}),
        ('Dates', {'fields': ('last_login', 'date_joined', 'last_active', 'kvkk_consent_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_doctor', 'date_of_birth', 'gender')
    list_filter = ('gender',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'is_accepting_patients')
    list_filter = ('is_accepting_patients',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'relationship_type', 'get_patients_count')
    list_filter = ('relationship_type',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('patients',)

    def get_patients_count(self, obj):
        return obj.patients.count()
    get_patients_count.short_description = 'Patients'


@admin.register(RelativeProfile)
class RelativeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'patient', 'relationship_type', 'is_approved', 'approved_at')
    list_filter = ('relationship_type', 'is_approved')
    search_fields = ('user__email', 'user__first_name', 'patient__first_name', 'patient__last_name')
    raw_id_fields = ('user', 'patient', 'approved_by')


from apps.accounts.models import DoctorAuthor, RelativeInvitation

@admin.register(DoctorAuthor)
class DoctorAuthorAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'primary_specialty', 'author_level', 'total_articles', 'is_verified', 'is_active']
    list_filter = ['primary_specialty', 'author_level', 'is_verified', 'is_active']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'institution']


@admin.register(RelativeInvitation)
class RelativeInvitationAdmin(admin.ModelAdmin):
    list_display = ['invited_email', 'patient', 'invited_by', 'relationship_type', 'is_used', 'expires_at', 'created_at']
    list_filter = ['is_used', 'relationship_type']
    search_fields = ['invited_email', 'invited_name', 'patient__first_name', 'patient__last_name']
    raw_id_fields = ('invited_by', 'patient')
    readonly_fields = ('token',)
