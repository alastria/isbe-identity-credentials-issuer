from django.urls import path

from . import views

urlpatterns = [
    path("representative", views.representative_issuance, name="issuance-representative"),
    path("employee", views.employee_issuance, name="issuance-employee"),
    # identifiers
    path("identifiers", views.list_identifiers, name="issuance-list-identifiers"),
    path("claims", views.get_claims_view, name="issuance-get-claims"),
    path("notifications", views.handle_notifications, name="issuance-handle-notifications"),
]
