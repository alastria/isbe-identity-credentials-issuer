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


import logging

from issuance.models import (
    CONFIG_KEY_API_VERSION,
    CONFIG_KEY_APP,
    CONFIG_KEY_INSTANCE,
    CONFIG_KEY_PROFILE,
    Configuration,
)
from project import settings
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


def get_url_base_for_connector_credential():
    api_version = Configuration.objects.filter(key=CONFIG_KEY_API_VERSION).first()
    if not api_version:
        raise Exception("API_VERSION not configured")
    return f"{IDENTFY_CONNECTOR_API_URL}/issuer/{api_version.value}/credentials"


def check_and_get_errors_access_token(claims: dict) -> bool:
    missing = []
    requeries = ["power", "user_identifier", "organization_identifier", "organization", "email"]
    for req in requeries:
        if req not in claims:
            missing.append(req)
    if len(missing) > 0:
        return missing

    # "power": [
    #            {"type": "domain", "domain": "DOME", "function": "Onboarding", "action": ["execute"]},
    #            {"type": "domain", "domain": "ISBE", "function": "Credentials", "action": ["execute"]},
    #        ],
    # Check power in claims
    print(f"claims power: {claims['power']}")
    print(f"settings POWER_REQUIRED: {settings.POWER_REQUIRED}")
    if "power" in claims and isinstance(claims["power"], list):
        powers = claims["power"]
        has_power = False
        for power in powers:
            if not isinstance(power, dict):
                continue
            for power_required in settings.POWER_REQUIRED:
                if not all(
                    key in power and (power_required[key] == ["*"] or power[key] in power_required[key])
                    for key in ["type", "domain", "function"]
                ):
                    continue
                if "action" not in power or not isinstance(power["action"], list):
                    continue

                print(f" ==> power required actions: {power_required['action']}, power actions: {power['action']}")
                if any(act in power["action"] for act in power_required["action"]):
                    has_power = True
                    break

            if has_power:
                break
        if not has_power:
            missing.append("thre is no required power for this operation")
    else:
        missing.append("power is missing or invalid")

    return missing


def get_item_value(data, list_items, name):
    if list_items in data and isinstance(data[list_items], list):
        list_items = data[list_items]
        for item in list_items:
            if item.get("name") == name:
                return item.get("value")
    return None
