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
        # raise Exception("Token expired")
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
            "name": "David Lutzardo",
            "preferred_username": "jdavidlb27@gmail.com",
            "power": [
                {"type": "domain", "domain": "DOME", "function": "Onboarding", "action": ["execute"]},
                {"type": "domain", "domain": "ISBE", "function": "Onboarding", "action": ["execute"]},
            ],
            "org_name": "GOOD AIR, S.L.",
            "org_legal_id": "NTRIES-B12345678",
            "org_legal_id_no": "VATFR-B12345678",
            "org_legal_id3": "VATES-11111111K",
            "org_legal_id2": "VATES-A66721499:IDCES-99999999R",
            "organization_identity": "urn:ngsi-ld:organization:VATES-11111111K",
            "given_name": "David",
            "family_name": "Lutzardo",
            "email": "jdavidlb27@gmail.com",
        }
    except Exception as e:
        print(e)
        raise Exception(f"Invalid token: {e}")
