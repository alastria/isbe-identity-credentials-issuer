import logging
import traceback
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from common.auth import virifity_token_and_get_payload
from common.identfy_connector import get_qr, identify_get_credential, identify_register_preauth_code
from common.tmf_api import tmf_get_individual, tmf_get_organization
from issuance.emails import send_email_user_enrollment
from issuance.enum import IssuedCredentialStatus
from issuance.helper import check_and_get_errors_access_token, get_profile, validate_request
from issuance.models import CONFIG_KEY_VC_TYPES, Configuration, IssuedCredential
from issuance.serializers import (
    GetClaimsSerializer,
    GetCredentialsByOrganizationIdentitySerializer,
    ListGetCredentialsByOrganizationIdentitySerializer,
    ListIdentifiersSerializer,
    NotificationSerializer,
)

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
            return send_error(status.HTTP_400_BAD_REQUEST, "Missing required data", ", ".join(missing))

        # TODO: validate fields
        user_data = {
            "sub": token_data.get("sub"),
            "org_legal_id": token_data.get("org_legal_id"),
            "org_name": token_data.get("org_name"),
            "roles": (token_data.get("realm_access") or {}).get("roles", []),
        }
        log.debug(user_data)

        content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="representative").first()
        if not vc_type:
            raise Exception("VC type for representative is not configured")
        profile = get_profile()
        if not profile:
            raise Exception("PROFILE not configured")
        subject_id = f"{token_data.get('email')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_register = identify_register_preauth_code(profile.value, vc_type.value, subject_id)
        print(preauth_register)
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_register["preauth_code"],
            preauth_code_expires_in=preauth_register["expires_in"],
            token_data=token_data,
            organization_identity=token_data.get("organization_identity"),
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
            return send_error(status.HTTP_400_BAD_REQUEST, "Missing required data", ", ".join(missing))
        # TODO: validate fields
        user_data = {
            "sub": token_data.get("sub"),
            "org_legal_id": token_data.get("org_legal_id"),
            "org_name": token_data.get("org_name"),
            "roles": (token_data.get("realm_access") or {}).get("roles", []),
        }
        log.debug(user_data)

        # TODO validade DNI?

        qr_content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="employee").first()
        if not vc_type:
            raise Exception("VC type for employee is not configured")
        if not get_profile():
            raise Exception("PROFILE not configured")
        subject_id = f"{token_data.get('email')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_register = identify_register_preauth_code(get_profile().value, vc_type.value, subject_id)
        print(preauth_register)
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_register["preauth_code"],
            preauth_code_expires_in=preauth_register["expires_in"],
            token_data=token_data,
            organization_identity=token_data.get("organization_identity"),
            status=IssuedCredentialStatus.PENDING.value,
        )

        send_email_user_enrollment(token_data.get("email"), qr_content)
        return JsonResponse({"message": "sends email with QR to user"}, safe=False)
    except Exception:
        traceback.print_exc()
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


@swagger_auto_schema(
    method="post",
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
    request_body=ListIdentifiersSerializer,
)
@api_view(["POST"])
def list_identifiers(request):
    serializer = ListIdentifiersSerializer(data=request.data)
    if not serializer.is_valid():
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data"), str(serializer.errors)
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
    return JsonResponse([{"vc_type": issued_credential.vc_type, "identifiers": []}], safe=False)


@swagger_auto_schema(
    method="post",
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
    request_body=GetClaimsSerializer,
)
@api_view(["POST"])
def get_claims_view(request):
    serializer = GetClaimsSerializer(data=request.data)
    if not serializer.is_valid():
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid data", str(serializer.errors))
    data = serializer.validated_data
    error = validate_request(data["app"], data["profile"], data["instance"])
    if error:
        return send_error(status.HTTP_404_NOT_FOUND, "Not found", error)
    issued_credential = IssuedCredential.objects.filter(
        vc_type=data["vc_identifier"], subject_id=data["subject_id"]
    ).first()
    if not issued_credential:
        return send_error(
            status.HTTP_404_NOT_FOUND,
            "Not found",
            "No issued credential found for the given profile, vc_identifier and subject_id",
        )
    try:
        org_legal_id = issued_credential.token_data.get("org_legal_id")
        if issued_credential.vc_type.lower().startswith("representative"):
            data = tmf_get_organization(org_legal_id)
        else:
            data = tmf_get_individual(org_legal_id)
        issued_credential.tmf_claims = data
        issued_credential.save()
        return JsonResponse({"subject_claims": data, "additional_claims": {}, "context_claims": {}}, safe=False)
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
    operation_description="Get issued credentials. Requires authentication (token) and permissions to access the specified organization_identity or admin role for all.",
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
    return _get_credentials_by_organization_identity(request)


@swagger_auto_schema(
    method="get",
    operation_description="Get issued credentials by organization_identity. Requires authentication (token) and permissions to access the specified organization_identity or admin role for all.",
    security=[{"Bearer": []}],
    request_parameters=[
        openapi.Parameter(
            name="organization_identity",
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
def get_credentials_by_organization_identity(request, organization_identity):
    organization_identity = request.resolver_match.kwargs.get("organization_identity")
    if not organization_identity:
        return send_error(status.HTTP_400_BAD_REQUEST, "Missing organization_identity parameter")
    return _get_credentials_by_organization_identity(request, organization_identity)


def _get_credentials_by_organization_identity(request, organization_identity=None):
    try:
        token_data = virifity_token_and_get_payload(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return send_error(status.HTTP_401_UNAUTHORIZED, "Unauthorized", "invalid token")

    # check organization_identity and permissions
    if organization_identity:
        token_org_identity = token_data.get("organization_identity")
        if token_org_identity != organization_identity:
            # TODO: check if has admin role to get other organization_identity credentials
            return send_error(status.HTTP_403_FORBIDDEN, "Forbidden", "Insufficient permissions")
    if not organization_identity:
        organization_identity = token_data.get("organization_identity")
        if not organization_identity:
            # TODO: check if has admin role to get all credentials
            return send_error(status.HTTP_400_BAD_REQUEST, "Missing organization_identity parameter")

    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 20)
    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return send_error(status.HTTP_400_BAD_REQUEST, "Invalid pagination parameters")

    try:
        logging.debug("organization_identity=%s", organization_identity)
        paginator = Paginator(
            IssuedCredential.objects.filter(organization_identity=organization_identity).all().order_by("-creation_at")
            if organization_identity
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
                    "organization_identity": cred.organization_identity,
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
        log.error(f"Error fetching credentials by organization_identity: {e}")
        return send_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error", str(e))


def send_error(status, message, description=""):
    return JsonResponse({"error": message, "error_description": description}, status=status, safe=False)
