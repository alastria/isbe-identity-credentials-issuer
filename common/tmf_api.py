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

from project.settings import TMF_API_URL

if not TMF_API_URL:
    raise Exception("TMF_API_URL setting is missing")


def tmf_get_organization(org_id: str) -> dict:
    if not org_id:
        raise Exception("org_legal_id is required")
    # /urn:ngsi-ld:organization:NTRIES-B12345678
    if "urn:ngsi-ld:organization:" not in org_id:
        org_id = f"urn:ngsi-ld:organization:{org_id}"

    headers = {
        "accept": "application/json",
    }
    resp = requests.get(f"{TMF_API_URL}/organization/{org_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def tmf_get_individual(individual_id: str) -> dict:
    if not individual_id:
        raise Exception("individual_legal_id is required")
    # urn:ngsi-ld:individual:VATES-A66721499:IDCES-99999999R
    if "urn:ngsi-ld:individual:" not in individual_id:
        individual_id = f"urn:ngsi-ld:individual:{individual_id}"

    headers = {
        "accept": "application/json",
    }
    # TODO: retorna error, revisar si se puede llamar
    # {
    #  "@type": "Error",
    #  "code": "403",
    #  "reason": "Forbidden",
    #  "message": "403 Forbidden: app/tmfserver/service/service.go:593 GetGenericObject: app/tmfserver/service/service.go:593 GetGenericObject: app/tmfserver/service/takedecision.go:35 takeDecision: user not authenticated"
    # }
    resp = requests.get(f"{TMF_API_URL}/individual/{individual_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()
