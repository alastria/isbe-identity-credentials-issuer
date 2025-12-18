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


from enum import Enum

from issuance.models import CONFIG_KEY_VC_TYPES, Configuration

VCTypes = None


def get_vc_types_enum():
    global VCTypes
    try:
        if VCTypes:
            return VCTypes
        configs = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES).all()
        vc_types = [item.value.strip() for item in configs]
        VCTypes = Enum("VCTypes", {item: item for item in vc_types})
        return VCTypes
    except Configuration.DoesNotExist:
        return Enum("VCTypes", {})


# Example usage:
# print(VCTypes.RepresentativeVC)
# print(VCTypes.EmployeeVC)
# print(list(VCTypes))


# TODO: pendiente de conocer los estados definitivos de las credenciales emitidas por IDP
IssuedCredentialStatus = Enum(
    "IssuedCredentialStatus", {"PENDING": "pending", "ISSUED": "issued", "REVOKED": "revoked"}
)
# Example usage:
# print(IssuedCredentialStatus.PENDING)
