from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PatientProfile, DoctorProfile


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


from apps.accounts.models import DoctorAuthor

@admin.register(DoctorAuthor)
class DoctorAuthorAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'primary_specialty', 'author_level', 'total_articles', 'is_verified', 'is_active']
    list_filter = ['primary_specialty', 'author_level', 'is_verified', 'is_active']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'institution']
