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


from datetime import datetime

import requests

from issuance.helper import get_url_base_for_connector
from project import settings
from project.settings import IDENTFY_CONNECTOR_API_URL


# TODO: ¿cambiar llamaa a /oid/credential-offer?
def get_qr():
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    resp = requests.get(get_url_base_for_connector() + "/credential-offer?response_mode=qr", headers=headers, timeout=8)
    # resp = requests.get(
    #    "https://identfy.izer.tech/95b3d953-6ac2-40c8-8707-b5f58dbb2279/credential-offer/qr", headers=headers, timeout=8
    # )
    if resp.status_code not in (200, 201):
        raise Exception(f"Error getting QR from Identfy Connector: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "image/png")
    return resp.content, ctype


def identify_register_preauth_code(profile: str, vc_type: str, subject_id: str) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    paylod = {
        "profile": profile,
        "vc_types": [vc_type],
        "subject_id": subject_id,
        # "expires_in?": number,
        # "tx_code?": {input_mode, length, description},
    }
    resp = requests.post(f"{get_url_base_for_connector()}/preauth-code", headers=headers, json=paylod)
    if resp.status_code not in (200, 201):
        raise Exception(f"Error getting QR from Identfy Connector: {resp.status_code} - {resp.text}")
    return resp.json()
    # print("TODO. Quitar salto identify_register_preauth_code")
    # return {
    #    "preauth_code": "abcd-1234-efgh-5678",
    #    "expires_in": datetime.now() + timedelta(days=30),
    #    "tx_code?": "algo_tx_code",
    # }


def identify_get_credential(credential_id: str) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    resp = requests.get(f"{IDENTFY_CONNECTOR_API_URL}/issuer/credentials/{credential_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()
    """
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
    """


def indentfy_revoke_credential(credential_id: str) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    # resp = requests.post(f"{_get_url_base()}/protected/credentials/{credential_id}/revoke", headers=headers)
    # resp.raise_for_status()
    # return resp.json()
    print("TODO. Quitar salto indentfy_revoke_credential")
    return {
        "credential_id": credential_id,
        "status": "revoked",
        "revocationDate": datetime.now().isoformat(),
    }
