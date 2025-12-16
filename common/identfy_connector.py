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

from issuance.helper import get_url_base_for_connector, get_url_base_for_connector_credential
from project import settings


def get_qr(preauth_code, vc_type: str) -> tuple[bytes, str]:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    resp = requests.get(get_url_base_for_connector() + "/credential-offer?response_mode=qr&preauth_code=" + preauth_code + "&vc_type=" + vc_type, headers=headers, timeout=8)
    # resp = requests.get(
    #    "https://identfy.izer.tech/95b3d953-6ac2-40c8-8707-b5f58dbb2279/credential-offer/qr", headers=headers, timeout=8
    # )
    if resp.status_code not in (200, 201):
        raise Exception(f"Error getting QR from Identfy Connector: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "image/png")
    return resp.content, ctype


def identify_register_preauth_code(profile: str, vc_type: str, subject_id: str, expires_in: int) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    paylod = {
        "profile": profile,
        "vc_types": [vc_type],
        "subject_id": subject_id,
        "expires_in": expires_in,
        # "tx_code?": {input_mode, length, description},
    }
    resp = requests.post(f"{get_url_base_for_connector()}/preauth-code", headers=headers, json=paylod)
    if resp.status_code not in (200, 201):
        raise Exception(f"Error getting QR from Identfy Connector: {resp.status_code} - {resp.text}")
    return resp.json()


def identify_get_credential(credential_id: str) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    resp = requests.get(f"{get_url_base_for_connector_credential()}/{credential_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def indentfy_revoke_credential(credential_id: str) -> dict:
    headers = {
        "accept": "application/json",
        "x-api-key": settings.IDENTFY_CONNECTOR_API_KEY,
    }
    paylod = {
        "status": "0x1"  # revoked
    }
    resp = requests.post(
        f"{get_url_base_for_connector_credential()}/{credential_id}/status", headers=headers, json=paylod
    )
    resp.raise_for_status()
    return resp.json()
