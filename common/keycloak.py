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


import requests
from jose import jwt
from jose.exceptions import JWTError

from project.settings import KEYCLOAK_JWKS_URI

if not KEYCLOAK_JWKS_URI:
    raise Exception("KEYCLOAK_JWKS_URI setting is missing")


def _get_jwks() -> dict:
    resp = requests.get(KEYCLOAK_JWKS_URI)
    resp.raise_for_status()
    return resp.json()


def _select_jwk_for_token(token: str) -> dict:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise JWTError("Token header has no 'kid'")

    jwks = _get_jwks()
    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return jwk

    raise JWTError("Matching JWK not found for kid")


def verify_jwt(token: str) -> dict:
    """
    Validate a Keycloak JWT using realm JWKS and return claims.
    """
    jwk = _select_jwk_for_token(token)

    return jwt.decode(
        token,
        jwk,
        options={"verify_aud": False},
    )
