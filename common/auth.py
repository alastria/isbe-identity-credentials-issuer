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


from typing import Any, Optional, Tuple

from django.http import HttpRequest
from jose.exceptions import ExpiredSignatureError

from common.keycloak import verify_jwt


def get_bearer_token_from_request(request: HttpRequest) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def virifity_token_and_get_payload(request: HttpRequest) -> Tuple[Optional[dict[str, Any]]]:
    token = get_bearer_token_from_request(request)
    if not token:
        raise Exception("Missing Bearer token")
    try:
        return verify_jwt(token)
    except ExpiredSignatureError:
        raise Exception("Token expired")
        """
        print("TODO. Quitar salto Token expired")
        return {
            "exp": 1761908111,
            "iat": 1761907811,
            "auth_time": 1761907810,
            "jti": "onrtac:fbac3db6-2c47-e075-b739-565dc87c9821",
            "iss": "https://keycloak-deploy-dev-080a5cde9036.herokuapp.com/realms/brokerdev",
            "aud": ["broker", "account"],
            "sub": "2e052739-3246-4606-b048-e8ad8362f511",
            "typ": "Bearer",
            "azp": "spa",
            "sid": "228054da-64e9-4b97-cf34-38a521e5d8bd",
            "acr": "1",
            "allowed-origins": ["http://localhost:8080"],
            "realm_access": {"roles": ["default-roles-brokerdev", "offline_access", "uma_authorization"]},
            "resource_access": {
                "broker": {"roles": ["read-token"]},
                "account": {"roles": ["manage-account", "manage-account-links", "view-profile"]},
            },
            "scope": "openid email cliente-credenciales profile",
            "prueba1": {"prueba1": 1},
            "prueba2": '{"prueba2":1}',
            "email_verified": "true",
            "given_name": "David",
            "family_name": "Lutzardo",
            "user": "David Lutzardo",
            "user_identifier": "12345678L",
            "email": "jdavidlb27@gmail.com",
            "power": [
                {"type": "domain", "domain": "DOME", "function": "Onboarding", "action": ["execute"]},
                {"type": "organization", "domain": "*", "function": "Onboarding", "action": ["execute"]},
            ],
            "organization": "GOOD AIR, S.L.",
            # "organization_identifier": "NTRIES-B12345678",
            "organization_identifier": "ORG-2024-001",
        }
    """
    except Exception as e:
        print(e)
        raise Exception(f"Invalid token: {e}")
