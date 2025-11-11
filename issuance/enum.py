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
    "IssuedCredentialStatus", {"PENDING": "pending", "ACTIVE": "active", "REVOKED": "revoked"}
)
# Example usage:
# print(IssuedCredentialStatus.PENDING)
