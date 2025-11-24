import logging

from issuance.models import (
    CONFIG_KEY_API_VERSION,
    CONFIG_KEY_APP,
    CONFIG_KEY_INSTANCE,
    CONFIG_KEY_PROFILE,
    Configuration,
)
from project.settings import IDENTFY_CONNECTOR_API_URL

log = logging.getLogger(__name__)

if not IDENTFY_CONNECTOR_API_URL:
    raise Exception("IDENTFY_CONNECTOR_API_URL setting is missing")


def get_profile():
    return Configuration.objects.filter(key=CONFIG_KEY_PROFILE).first()


def validate_request(app: str, profile: str, instance: str) -> str | None:
    list = Configuration.objects.filter(key__in=[CONFIG_KEY_PROFILE, CONFIG_KEY_APP, CONFIG_KEY_INSTANCE]).all()

    config_profile = list.filter(key=CONFIG_KEY_PROFILE).first()
    if not config_profile or config_profile.value != profile:
        return "Profile not found"
    config_app = list.filter(key=CONFIG_KEY_APP).first()
    if not config_app or config_app.value != app:
        return "App not found"
    config_instance = list.filter(key=CONFIG_KEY_INSTANCE).first()
    print("instance:", instance)
    if not config_instance or config_instance.value != instance:
        return "Instance not found"
    return None


def get_url_base_for_connector():
    # /oid/v{version}/{profile}/{endpoint}/...
    list = Configuration.objects.filter(
        key__in=[CONFIG_KEY_API_VERSION, CONFIG_KEY_PROFILE, CONFIG_KEY_APP, CONFIG_KEY_INSTANCE]
    ).all()
    app = list.filter(key=CONFIG_KEY_APP).first()
    if not app:
        raise Exception("APP not configured")
    api_version = list.filter(key=CONFIG_KEY_API_VERSION).first()
    if not api_version:
        raise Exception("API_VERSION not configured")
    profile = list.filter(key=CONFIG_KEY_PROFILE).first()
    if not profile:
        raise Exception("PROFILE not configured")
    instance = list.filter(key=CONFIG_KEY_INSTANCE).first()
    if not instance:
        raise Exception("INSTANCE not configured")
    if api_version.value == "-":
        return f"{IDENTFY_CONNECTOR_API_URL}/{app.value}/{profile.value}/{instance.value}"
    return f"{IDENTFY_CONNECTOR_API_URL}/{app.value}/{api_version.value}/{profile.value}/{instance.value}"


def check_and_get_errors_access_token(claims: dict) -> bool:
    missing = []
    # TODO: revisar todos los claims necesarios, añadir los que falten
    # Algunos pueden cambiar de nombre o no ser obligatorios
    if "org_legal_id" not in claims:
        missing.append("org_legal_id")
    if "org_name" not in claims:
        missing.append("org_name")
    if "email" not in claims:
        missing.append("email")
    if "organization_identity" not in claims:
        missing.append("organization_identity")
    roles_present = (
        "realm_access" in claims and isinstance(claims["realm_access"], dict) and "roles" in claims["realm_access"]
    )
    if not roles_present:
        missing.append("realm_access.roles")
    return missing
