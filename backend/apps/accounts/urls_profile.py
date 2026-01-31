from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.UserProfileView.as_view(), name='user_profile'),
    path('me/patient-profile/', views.PatientProfileView.as_view(), name='patient_profile'),
    path('me/doctor-profile/', views.DoctorProfileView.as_view(), name='doctor_profile'),
]
