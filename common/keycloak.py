import requests
from jose import jwt
from jose.exceptions import JWTError

from project.settings import KEYCLOAK_JWKS_URL

if not KEYCLOAK_JWKS_URL:
    raise Exception("KEYCLOAK_JWKS_URL setting is missing")


def _get_jwks() -> dict:
    resp = requests.get(KEYCLOAK_JWKS_URL)
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
