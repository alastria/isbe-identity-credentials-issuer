import requests

from project.settings import TMF_API_URL

if not TMF_API_URL:
    raise Exception("TMF_API_URL setting is missing")


def tmf_get_organization(org_legal_id: str) -> dict:
    if not org_legal_id:
        raise Exception("org_legal_id is required")
    # /urn:ngsi-ld:organization:NTRIES-B12345678
    if "urn:ngsi-ld:organization:" not in org_legal_id:
        org_legal_id = f"urn:ngsi-ld:organization:{org_legal_id}"

    headers = {
        "accept": "application/json",
    }
    resp = requests.get(f"{TMF_API_URL}/organization/{org_legal_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def tmf_get_individual(individual_legal_id: str) -> dict:
    if not individual_legal_id:
        raise Exception("individual_legal_id is required")
    # urn:ngsi-ld:individual:VATES-A66721499:IDCES-99999999R
    if "urn:ngsi-ld:individual:" not in individual_legal_id:
        individual_legal_id = f"urn:ngsi-ld:individual:{individual_legal_id}"

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
    resp = requests.get(f"{TMF_API_URL}/individual/{individual_legal_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()
