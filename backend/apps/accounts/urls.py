from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),

    # Relative invitation flow
    path('relative/invite/', views.InviteRelativeView.as_view(), name='invite-relative'),
    path('relative/invitations/', views.InviteRelativeListView.as_view(), name='relative-invitations'),
    path('relative/invite/verify/<uuid:token>/', views.VerifyInvitationView.as_view(), name='verify-invitation'),
    path('relative/register/', views.RegisterRelativeView.as_view(), name='register-relative'),

    # Doctor approval (admin endpoints)
    path('doctor-applications/', views.DoctorApplicationListView.as_view(), name='doctor-applications'),
    path('doctor-applications/<uuid:pk>/approve/', views.DoctorApplicationApproveView.as_view(), name='doctor-approve'),
    path('doctor-applications/<uuid:pk>/reject/', views.DoctorApplicationRejectView.as_view(), name='doctor-reject'),
]
