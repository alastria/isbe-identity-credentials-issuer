
from django.urls import path

from . import views

urlpatterns = [
    path("representative", views.representative_issuance, name="issuance-representative"),
    path("employee", views.employee_issuance, name="issuance-employee"),
    # identifiers
    path("identifiers", views.list_identifiers, name="issuance-list-identifiers"),
    path("claims", views.get_claims_view, name="issuance-get-claims"),
    path("notifications", views.handle_notifications, name="issuance-handle-notifications"),
    path("credential", views.get_credentials, name="get-credentials"),
    path(
        "credential/<str:organization_identity>",
        views.get_credentials_by_organization_identity,
        name="get-credentials-by-organization_identity",
    ),
    path("credential/revoke/<str:credential_id>", views.revoke_credential, name="revoke-credential"),
]
