# Copyright (c) 2025 Comunidad de Madrid & Alastria
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
# [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0 "http://www.apache.org/licenses/license-2.0")
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
