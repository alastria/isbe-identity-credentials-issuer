from datetime import datetime, timedelta

import requests

from issuance.helper import get_url_base_for_connector
from project.settings import IDENTFY_CONNECTOR_API_URL


# TODO: ¿cambiar llamaa a /oid/credential-offer?
def get_qr():
    headers = {
        "accept": "application/json",
    }
    # TODO: request añadir parametros cuando este el conector final
    # resp = requests.get(IDENTFY_CONNECTOR_API_URL + "/credential-offer/qr", headers=headers, timeout=8)
    resp = requests.get(get_url_base_for_connector() + "/credential-offer/qr", headers=headers, timeout=8)
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "image/png")
    return resp.content, ctype


def identify_register_preauth_code(profile: str, vc_type: str, subject_id: str) -> dict:
    headers = {
        "accept": "application/json",
    }
    paylod = {
        "profile": profile,
        "vc_types": [vc_type],
        "subject_id": subject_id,
        # "expires_in?": number,
        # "tx_code?": {input_mode, length, description},
    }
    # resp = requests.post(f"{_get_url_base()}/protected/oid/preauth-code", headers=headers, json=paylod)
    print("TODO. Quitar salto identify_register_preauth_code")
    # resp.raise_for_status()
    # return resp.json()
    return {
        "preauth_code": "abcd-1234-efgh-5678",
        "expires_in": datetime.now() + timedelta(days=30),
        "tx_code?": "algo_tx_code",
    }


def identify_get_credential(credential_id: str) -> dict:
    headers = {
        "accept": "application/json",
    }
    # resp = requests.get(f"{_get_url_base()}/protected/credentials/{credential_id}", headers=headers)
    # resp.raise_for_status()
    # return resp.json()
    print("TODO. Quitar salto identify_get_credential")
    return {
        "credential_id": credential_id,
        "credential_data": {
            "id": credential_id,
            "type": ["VerifiableCredential", "ExampleCredential"],
            "issuer": "did:example:issuer123",
            "issuanceDate": "2024-01-01T00:00:00Z",
            "credentialSubject": {
                "id": "did:example:subject456",
                "exampleField": "exampleValue",
            },
            "proof": {
                "type": "Ed25519Signature2018",
                "created": "2024-01-01T00:00:00Z",
                "proofPurpose": "assertionMethod",
                "verificationMethod": "did:example:issuer123#key-1",
                "jws": "eyJ...signature...",
            },
        },
    }
