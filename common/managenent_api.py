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

from project.settings import MANAGEMENT_API_URL


def get_management_by_organization(organization_identifier: str) -> dict:
    headers = {
        "accept": "application/json",
    }
    resp = requests.get(f"{MANAGEMENT_API_URL}/managements/organization/{organization_identifier}", headers=headers)
    if resp.status_code == 404:
        return {}
    resp.raise_for_status()

    return resp.json()


def check_roles_in_polices(organization_identifier: str, powers: list[dict]) -> bool:
    management = get_management_by_organization(organization_identifier)
    if not management or "role" not in management or "policies" not in management.get("role", {}):
        return False
    policies = management.get("role", {}).get("policies", [])
    # check all powers are in policies
    result = True
    for power in powers:
        exist = False
        for policy in policies:
            #  {"type": "organization", "action": ["*" ], "domain": "ISBE", "function": "*" }
            if (
                policy.get("type") == power.get("type")
                and policy.get("domain") == power.get("domain")
                and policy.get("function") == power.get("function")
            ):
                action_policy = policy.get("action", [])
                if "*" in action_policy:
                    exist = True
                    break
                action_power = power.get("action", [])

                all_actions_exist = all(act in action_policy for act in action_power)
                all_actions_exist_2 = all(act in action_power for act in action_policy)
                if all_actions_exist and all_actions_exist_2:
                    exist = True
                    break
        if not exist:
            return False

    return result
