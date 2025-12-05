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
import traceback
from datetime import datetime, timedelta

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from common.auth import virifity_token_and_get_payload
from common.identfy_connector import (
    get_qr,
    identify_get_credential,
    identify_register_preauth_code,
    indentfy_revoke_credential,
)
from common.managenent_api import check_roles_in_polices
from common.tmf_api import tmf_get_organization
from issuance.emails import send_email_user_enrollment
from issuance.enum import IssuedCredentialStatus
from issuance.helper import check_and_get_errors_access_token, get_item_value, get_profile, validate_request
from issuance.models import CONFIG_KEY_VC_TYPES, Configuration, IssuedCredential
from issuance.serializers import (
    GetClaimsSerializer,
    GetCredentialsByOrganizationIdentitySerializer,
    IssueEmployeeCredentialSerializer,
    IssueRepresentativeCredentialSerializer,
    ListGetCredentialsByOrganizationIdentitySerializer,
    ListIdentifiersSerializer,
    NotificationSerializer,
)
from project.settings import FUNCTION_REQUIRED

log = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_description="Issue a VC for a representative (returns QR PNG)",
    security=[{"Bearer": []}],
    produces=["image/png"],
    responses={
        200: openapi.Response(
            description="QR image (PNG)",
            schema=openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
        ),
        400: "Bad Request",
        401: "Unauthorized",
    },
    request_body=IssueRepresentativeCredentialSerializer,
)
@api_view(["POST"])
def representative_issuance(request):
    try:
        token_data = virifity_token_and_get_payload(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return send_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "invalid token")

    try:
        missing = check_and_get_errors_access_token(token_data)
        if missing:
            return send_error(
                status.HTTP_400_BAD_REQUEST, "Missing required data or invalid powers", ", ".join(missing)
            )

        serializer = IssueRepresentativeCredentialSerializer(data=request.data)
        if not serializer.is_valid():
            return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))

        # En el body de la petición se recibirá un listado de poderes a asignar en la credencial. El emisor debe comprobar que ISBE
        #  autoriza asignar los poderes recibidos a la organización. Para ello es necesario consultar el servicio de gestión de roles
        #  y preguntar los roles y poderes autorizados a la organización. Todos los poderes recibidos en el POST deben formar parte
        #  del conjunto autorizado, en caso contrario se deniega la operación.
        if not check_roles_in_polices(
            token_data.get("organization_identifier"), serializer.validated_data.get("power", [])
        ):
            return send_error(
                status.HTTP_400_BAD_REQUEST,
                "Invalid powers",
                "The requested powers are not authorized for the organization",
            )

        content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="representative").first()
        if not vc_type:
            raise Exception("VC type for representative is not configured")
        profile = get_profile()
        if not profile:
            raise Exception("PROFILE not configured")
        subject_id = f"{token_data.get('organization_identifier')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_result = identify_register_preauth_code(profile.value, vc_type.value, subject_id)
        # {"preauth_code":"52c520b0-b0b6-40c7-8c62-d17b1cce920f","expires_in":300}
        log.info(f"Preauth code registered: {preauth_result}")
        date_expires = datetime.now()
        date_expires = date_expires.replace(microsecond=0)
        date_expires = date_expires + timedelta(seconds=preauth_result["expires_in"])
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_result["preauth_code"],
            preauth_code_expires_in=date_expires,
            token_data=token_data,
            body_data=serializer.validated_data,
            organization_identifier=token_data.get("organization_identifier"),
            status=IssuedCredentialStatus.PENDING.value,
        )
        return HttpResponse(content, content_type=ctype)
    except Exception:
        traceback.print_exc()
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@swagger_auto_schema(
    method="post",
    operation_description="Issue a VC for an employee (sends email with QR)",
    security=[{"Bearer": []}],
    produces=["image/png"],
    responses={
        200: openapi.Response(
            description="QR image (PNG)",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={"message": openapi.Schema(type=openapi.TYPE_STRING)}
            ),
        ),
        400: "Bad Request",
        401: "Unauthorized",
    },
    request_body=IssueEmployeeCredentialSerializer,
)
@api_view(["POST"])
def employee_issuance(request):
    try:
        token_data = virifity_token_and_get_payload(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return send_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "invalid token")

    try:
        missing = check_and_get_errors_access_token(token_data)
        if missing:
            return send_error(
                status.HTTP_400_BAD_REQUEST, "Missing required data or invalid powers", ", ".join(missing)
            )

        serializer = IssueEmployeeCredentialSerializer(data=request.data)
        if not serializer.is_valid():
            return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))
        # TODO validade DNI?

        # En el body de la petición se recibirá un listado de poderes a asignar en la credencial. El emisor debe comprobar que ISBE
        #  autoriza asignar los poderes recibidos a la organización. Para ello es necesario consultar el servicio de gestión de roles
        #  y preguntar los roles y poderes autorizados a la organización. Todos los poderes recibidos en el POST deben formar parte
        #  del conjunto autorizado, en caso contrario se deniega la operación.
        if not check_roles_in_polices(
            token_data.get("organization_identifier"), serializer.validated_data.get("power", [])
        ):
            return send_error(
                status.HTTP_400_BAD_REQUEST,
                "Invalid powers",
                "The requested powers are not authorized for the organization",
            )

        qr_content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="employee").first()
        if not vc_type:
            raise Exception("VC type for employee is not configured")
        if not get_profile():
            raise Exception("PROFILE not configured")
        subject_id = f"{serializer['email'].value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_result = identify_register_preauth_code(get_profile().value, vc_type.value, subject_id)
        # {"preauth_code":"52c520b0-b0b6-40c7-8c62-d17b1cce920f","expires_in":300}
        log.info(f"Preauth code registered: {preauth_result}")
        date_expires = datetime.now()
        date_expires = date_expires.replace(microsecond=0)
        date_expires = date_expires + timedelta(seconds=preauth_result["expires_in"])
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_result["preauth_code"],
            preauth_code_expires_in=date_expires,
            token_data=token_data,
            body_data=serializer.validated_data,
            organization_identifier=token_data.get("organization_identifier"),
            status=IssuedCredentialStatus.PENDING.value,
        )

        send_email_user_enrollment(serializer["email"].value, qr_content)
        return JsonResponse({"message": "sends email with QR to user"}, safe=False)
    except Exception:
        traceback.print_exc()
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@swagger_auto_schema(
    method="get",
    operation_description="List available identifier types for issuance",
    responses={
        200: openapi.Response(
            description="List of identifier types",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "vc_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "identifiers": openapi.Schema(
                            type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
                        ),
                    },
                ),
            ),
        ),
        401: "Unauthorized",
        404: "Not Found",
    },
    manual_parameters=[
        openapi.Parameter(
            name="app",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Application name",
            required=True,
        ),
        openapi.Parameter(
            name="profile",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Profile name",
            required=True,
        ),
        openapi.Parameter(
            name="instance",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Instance name",
            required=True,
        ),
        openapi.Parameter(
            name="vc_type",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="VC type",
            required=True,
        ),
        openapi.Parameter(
            name="subject_id",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Subject ID",
            required=True,
        ),
    ],
)
@api_view(["GET"])
def list_identifiers(request):
    serializer = ListIdentifiersSerializer(data=request.GET)
    if not serializer.is_valid():
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))
    data = serializer.validated_data
    error = validate_request(data["app"], data["profile"], data["instance"])
    if error:
        return send_error(status.HTTP_404_NOT_FOUND, "Not found", error)
    issued_credential = IssuedCredential.objects.filter(vc_type=data["vc_type"], subject_id=data["subject_id"]).first()
    if not issued_credential:
        return send_error(
            status.HTTP_404_NOT_FOUND,
            "Not found",
            "No issued credential found for the given profile, vc_type and subject_id",
        )
    # [{”vc_type”:”LearVC”, “identfiers”: []]

    return JsonResponse(
        [{"vc_type": issued_credential.vc_type, "identifiers": [_vc_type_to_identier(issued_credential.vc_type)]}],
        safe=False,
    )


def _vc_type_to_identier(vc_type: str) -> str:
    return f"isbe-{vc_type.lower()}"


def _isbe_identier_to_vc_type(identifier: str) -> str:
    if identifier.startswith("isbe-"):
        return identifier[5:]
    return identifier


@swagger_auto_schema(
    method="get",
    operation_description="Get claims data for a given VC",
    responses={
        200: openapi.Response(
            description="Claims data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "subject_claims": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Claims data associated with the subject",
                    ),
                    "additional_claims": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Additional claims data fetched from TMF API",
                    ),
                    "context_claims": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Contextual claims data",
                    ),
                },
            ),
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Not Found",
    },
    manual_parameters=[
        openapi.Parameter(
            name="app",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Application name",
            required=True,
        ),
        openapi.Parameter(
            name="profile",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Profile name",
            required=True,
        ),
        openapi.Parameter(
            name="instance",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Instance name",
            required=True,
        ),
        openapi.Parameter(
            name="vc_type",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="VC type",
            required=True,
        ),
        openapi.Parameter(
            name="subject_id",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Subject ID",
            required=True,
        ),
    ],
)
@api_view(["GET"])
def get_claims_view(request):
    serializer = GetClaimsSerializer(data=request.GET)
    if not serializer.is_valid():
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))
    data = serializer.validated_data
    error = validate_request(data["app"], data["profile"], data["instance"])
    if error:
        return send_error(status.HTTP_404_NOT_FOUND, "Not found", error)
    issued_credential = IssuedCredential.objects.filter(
        vc_type__iexact=_isbe_identier_to_vc_type(data["vc_identifier"]), subject_id=data["subject_id"]
    ).first()
    if not issued_credential:
        return send_error(
            status.HTTP_404_NOT_FOUND,
            "Not found",
            "No issued credential found for the given profile, vc_identifier and subject_id",
        )

    try:
        """ Example response:"
        {
            "mandate": {
                "mandator": {
                    "organization": "GOOD AIR, S.L.",
                    "organizationIdentifier": "VATFR-B12345678",
                    "country": "FR",
                    "commonName": " GOOD AIR, S.L.",
                    "serialNumber": "880692310285",
                    "email": "jean.mar@goodair.fr",
                },
                "mandatee": {
                    "employeId": "A-12345678",
                    "email": "jane.smith@goodair.com",
                    "firstName": "Jane",
                    "lastName": "Smith",
                },
                "power": [{"type": "organization", "domain": "ISBE", "function": "Onboarding", "action": ["execute"]}],
            }
        }
        """
        data = tmf_get_organization(issued_credential.organization_identifier)
        print("TMF organization data:", data)
        claims = {
            "mandate": {
                "mandator": {
                    "organization": data.get("name"),
                    "organizationIdentifier": issued_credential.organization_identifier,
                },
                "mandatee": {},
                "power": issued_credential.body_data.get("power", []),
            }
        }

        country = get_item_value(data, "partyCharacteristic", "country")
        if country:
            claims["mandate"]["mandator"]["country"] = country
        if "tradingName" in data:
            claims["mandate"]["mandator"]["commonName"] = data["tradingName"]
        serialNumber = get_item_value(data, "partyCharacteristic", "serialNumber")
        if serialNumber:  # TODO: revisar, no encuentro donde se obtiene ese dato
            claims["mandate"]["mandator"]["serialNumber"] = serialNumber
        email = get_item_value(data, "partyCharacteristic", "email")
        if email:  # TODO: revisar, no encuentro donde se obtiene ese dato
            claims["mandate"]["mandator"]["email"] = email
        # TODO: se obtienen datos de data["organizationIdentification"][0]["attachment"]["content"] es un base64 con una credencial

        if issued_credential.vc_type.lower().startswith("employee"):
            claims["mandate"]["mandatee"] = {
                "employeId": issued_credential.body_data.get("employeId"),
                "email": issued_credential.body_data.get("email"),
                "firstName": issued_credential.body_data.get("firstName"),
                "lastName": issued_credential.body_data.get("lastName"),
            }

        else:
            # TODO: De momento listado vacio. Error 404 Client Not Found for url: https://tmf.evidenceledger.eu/tmf-api/party/v4/individual/urn:ngsi-ld:individual:NTRIES-B12345678"
            # data = tmf_get_individual(issued_credential.organization_identifier)
            claims["mandate"]["mandatee"] = {
                "employeId": issued_credential.token_data.get("user_identifier"),
                "email": issued_credential.token_data.get("email"),
                "firstName": issued_credential.token_data.get("user"),
                "lastName": "",
            }
        issued_credential.tmf_claims = data
        issued_credential.save()
        return JsonResponse({"subject_claims": claims, "additional_claims": {}, "context_claims": {}}, safe=False)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error fetching organization data from TMF API: {e}")
        return send_error(status.HTTP_502_BAD_GATEWAY, "Upstream error", str(e))


@swagger_auto_schema(
    method="post",
    operation_description="Handle notifications from Identfy Connector",
    responses={
        200: openapi.Response(
            description="Notification processed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Not Found",
    },
    request_body=NotificationSerializer,
)
@api_view(["POST"])
def handle_notifications(request):
    try:
        data = request.data
        log.debug(f"Notification received: {data}")
        serializer = NotificationSerializer(data=data)
        if not serializer.is_valid():
            return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))

        data = serializer.validated_data
        error = validate_request(data["app"], data["profile"], data["instance"])
        if error:
            return send_error(status.HTTP_404_NOT_FOUND, "Not found", error)
        issued_credential = IssuedCredential.objects.filter(subject_id=data["subject_id"]).first()
        if not issued_credential:
            return send_error(status.HTTP_404_NOT_FOUND, "Issued credential not found for the given subject_id")

        # Process the notification
        log.info(f"Processing notification for credential ID: {data['credential_id']}, type: {data['type']}")
        if issued_credential.credential_id and issued_credential.credential_id != data["credential_id"]:
            log.warning(
                f"Credential ID mismatch: existing {issued_credential.credential_id}, notification {data['credential_id']}"
            )
            return send_error(status.HTTP_400_BAD_REQUEST, "Credential ID mismatch")

        if not issued_credential.credential_id and data["credential_id"]:
            # Update the credential ID if not set before
            issued_credential.credential_data = identify_get_credential(data["credential_id"])

        issued_credential.credential_id = data["credential_id"]
        issued_credential.status = data["type"]
        issued_credential.update_at = datetime.now()
        issued_credential.save()

        return JsonResponse({"message": "Notification processed successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error processing notification: {e}")
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error", str(e))


@swagger_auto_schema(
    method="get",
    operation_description="Get issued credentials. Requires authentication (token) and permissions to access the specified organization_identifier or admin role for all.",
    security=[{"Bearer": []}],
    responses={
        200: openapi.Response("List of issued credentials", ListGetCredentialsByOrganizationIdentitySerializer),
        400: "Bad Request",
        500: "Internal Server Error",
    },
    manual_parameters=[
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Page number (optional)",
            required=False,
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Number of items per page (optional)",
            required=False,
        ),
    ],
)
@api_view(["GET"])
def get_credentials(request):
    return _get_credentials_by_organization_identifier(request)


@swagger_auto_schema(
    method="get",
    operation_description="Get issued credentials by organization_identifier. Requires authentication (token) and permissions to access the specified organization_identifier or admin role for all.",
    security=[{"Bearer": []}],
    request_parameters=[
        openapi.Parameter(
            name="organization_identifier",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description="Organization identity to filter issued credentials",
        ),
    ],
    manual_parameters=[
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Page number (optional)",
            required=False,
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Number of items per page (optional)",
            required=False,
        ),
    ],
    responses={
        200: openapi.Response("List of issued credentials", ListGetCredentialsByOrganizationIdentitySerializer),
        400: "Bad Request",
        500: "Internal Server Error",
    },
)
@api_view(["GET"])
def get_credentials_by_organization_identifier(request, organization_identifier):
    organization_identifier = request.resolver_match.kwargs.get("organization_identifier")
    if not organization_identifier:
        return send_error(status.HTTP_400_BAD_REQUEST, "Missing organization_identifier parameter")
    return _get_credentials_by_organization_identifier(request, organization_identifier)


@swagger_auto_schema(
    method="post",
    operation_description="Revoke an issued credential by its ID. Requires authentication (token) and permissions to access the specified organization_identifier or admin role for all.",
    security=[{"Bearer": []}],
    responses={
        200: openapi.Response(
            description="Credential revoked successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    },
    request_body=None,
)
@api_view(["POST"])
def revoke_credential(request, credential_id):
    try:
        token_data = virifity_token_and_get_payload(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return send_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "invalid token")

    try:
        issued_credential = IssuedCredential.objects.filter(credential_id=credential_id).first()
        if not issued_credential:
            return send_error(status.HTTP_404_NOT_FOUND, "Credential not found")

        # check permissions
        if _check_permissions_in_revoke(token_data, issued_credential.organization_identifier) is False:
            return send_error(status.HTTP_403_FORBIDDEN, "Forbidden", "insufficient permissions")

        result = indentfy_revoke_credential(credential_id)
        if result.get("status") != "0x1":
            return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to revoke credential")
        issued_credential.status = IssuedCredentialStatus.REVOKED.value
        issued_credential.update_at = datetime.now()
        issued_credential.save()
        return JsonResponse({"message": "Credential revoked successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error revoking credential: {e}")
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error", str(e))


def _check_is_admin_role(token_data):
    # check admin role
    powers = token_data["power"]
    for power in powers:
        if "domain" == power["type"]:
            return True
    return False


def _check_actions_in_power(token_data, expected_actions):
    powers = token_data["power"]
    for power in powers:
        if power["function"] != FUNCTION_REQUIRED:
            continue
        if "action" not in power or not isinstance(power["action"], list):
            continue
        if "*" in power["action"]:
            return True
        for action_required in expected_actions:
            if action_required in power["action"]:
                return True
    return False


def _check_permissions_in_revoke(token_data, organization_identifier):
    print(f" ==> power: {token_data['power']}")
    # check organization_identifier and permissions
    token_org_identity = token_data.get("organization_identifier")
    # Check can access organization_identifier
    if token_org_identity != organization_identifier and not _check_is_admin_role(token_data):
        print(" ==> organization_identifier mismatch and not admin")
        return False
    # check permissions for operation
    return _check_actions_in_power(token_data, ["delete"])


def _check_permissions_in_get_credentials(token_data, organization_identifier):
    print(f" ==> power: {token_data['power']}")
    # check organization_identifier and permissions
    token_org_identity = token_data.get("organization_identifier")
    # Check can access organization_identifier
    if not token_org_identity == organization_identifier and not _check_is_admin_role(token_data):
        print(" ==> organization_identifier mismatch and not admin")
        return False
    # check permissions for operation
    return _check_actions_in_power(token_data, ["read", "write"])


def _get_credentials_by_organization_identifier(request, organization_identifier=None):
    try:
        token_data = virifity_token_and_get_payload(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return send_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "invalid token")

    if not organization_identifier and not _check_is_admin_role(token_data):
        organization_identifier = token_data.get("organization_identifier")
        if not organization_identifier:
            return send_error(
                status.HTTP_400_BAD_REQUEST, "Missing organization_identifier in parameter and access token"
            )

    print("organization_identifier:", organization_identifier)
    # check permissions
    if _check_permissions_in_get_credentials(token_data, organization_identifier) is False:
        return send_error(status.HTTP_403_FORBIDDEN, "Forbidden", "insufficient permissions")

    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 20)
    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid pagination parameters")

    try:
        logging.debug("organization_identifier=%s", organization_identifier)
        paginator = Paginator(
            IssuedCredential.objects.filter(organization_identifier=organization_identifier)
            .all()
            .order_by("-creation_at")
            if organization_identifier
            else IssuedCredential.objects.all().order_by("-creation_at"),
            page_size,
        )
        try:
            issued_credentials = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            issued_credentials = paginator.page(1)

        if page > paginator.num_pages:
            issued_credentials = []

        credentials_list: list[GetCredentialsByOrganizationIdentitySerializer] = []
        for cred in issued_credentials:
            credentials_list.append(
                {
                    "credential_id": cred.credential_id,
                    "organization_identifier": cred.organization_identifier,
                    "vc_type": cred.vc_type,
                    "status": cred.status,
                    "creation_at": cred.creation_at,
                    "update_at": cred.update_at,
                }
            )

        result: ListGetCredentialsByOrganizationIdentitySerializer = {
            "credentials": credentials_list,
            "page": page,
            "num_pages": paginator.num_pages,
            "page_size": page_size,
            "total": paginator.count,
        }
        return JsonResponse(result, safe=False)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error fetching credentials by organization_identifier: {e}")
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error", str(e))


def send_error(status, message, description=""):
    return JsonResponse({"error": message, "error_description": description}, status=status, safe=False)
