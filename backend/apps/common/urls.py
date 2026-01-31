from django.urls import path
from . import views

urlpatterns = [
    path('consent/', views.ConsentListView.as_view(), name='consent-list'),
    path('consent/grant/', views.GrantConsentView.as_view(), name='consent-grant'),
]
