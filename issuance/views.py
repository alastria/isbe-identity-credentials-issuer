import logging
import traceback
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from common.auth import get_claims
from common.identfy_conector import get_qr, identify_get_credential, identify_register_preauth_code
from common.tmf_api import tmf_get_individual, tmf_get_organization
from issuance.enum import IssuedCredentialStatus
from issuance.models import CONFIG_KEY_PROFILE, CONFIG_KEY_VC_TYPES, Configuration, IssuedCredential
from issuance.serializers import (
    GetClaimsSerializer,
    ListIdentifiersSerializer,
    NotificationSerializer,
)

log = logging.getLogger(__name__)


PROFILE = None


def get_profile():
    global PROFILE
    if PROFILE:
        return PROFILE
    PROFILE = Configuration.objects.filter(key=CONFIG_KEY_PROFILE).first()
    return PROFILE


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
        401: "Unauthorized",
        403: "Missing required claims",
    },
)
@api_view(["POST"])
def representative_issuance(request):
    try:
        claims = get_claims(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return JsonResponse({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        missing = []
        if "org_legal_id" not in claims:
            missing.append("org_legal_id")
        if "org_name" not in claims:
            missing.append("org_name")
        if "email" not in claims:
            missing.append("email")
        roles_present = (
            "realm_access" in claims and isinstance(claims["realm_access"], dict) and "roles" in claims["realm_access"]
        )
        if not roles_present:
            missing.append("realm_access.roles")

        if missing:
            return JsonResponse(
                {"detail": "Missing required claims", "missing": missing}, status=status.HTTP_400_BAD_REQUEST
            )
        # TODO: validate fields
        user_data = {
            "sub": claims.get("sub"),
            "org_legal_id": claims.get("org_legal_id"),
            "org_name": claims.get("org_name"),
            "roles": (claims.get("realm_access") or {}).get("roles", []),
        }
        log.debug(user_data)

        content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="representative").first()
        if not vc_type:
            raise Exception("VC type for representative is not configured")
        if not get_profile():
            raise Exception("PROFILE not configured")
        subject_id = f"{claims.get('email')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_register = identify_register_preauth_code(get_profile().value, vc_type.value, subject_id)
        print(preauth_register)
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_register["preauth_code"],
            preauth_code_expires_in=preauth_register["expires_in"],
            token_claims=claims,
            status=IssuedCredentialStatus.PENDING.value,
        )
        return HttpResponse(content, content_type=ctype)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"detail": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_description="Issue a VC for an employee (returns QR PNG)",
    security=[{"Bearer": []}],
    produces=["image/png"],
    responses={
        200: openapi.Response(
            description="QR image (PNG)",
            schema=openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
        ),
        401: "Unauthorized",
        502: "Upstream error",
        504: "Upstream timeout",
    },
)
@api_view(["POST"])
def employee_issuance(request):
    try:
        claims = get_claims(request)
    except Exception as e:
        log.error(f"Auth error: {e}")
        return JsonResponse({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        missing = []
        # TODO: revisar claims necesarios para employee, luego puede que se pueda refactorizar con representative_issuance
        if "org_legal_id" not in claims:
            missing.append("org_legal_id")
        if "org_name" not in claims:
            missing.append("org_name")
        if "email" not in claims:
            missing.append("email")

        if missing:
            return JsonResponse(
                {"detail": "Missing required claims", "missing": missing}, status=status.HTTP_400_BAD_REQUEST
            )
        # TODO: validate fields
        user_data = {
            "sub": claims.get("sub"),
            "org_legal_id": claims.get("org_legal_id"),
            "org_name": claims.get("org_name"),
            "roles": (claims.get("realm_access") or {}).get("roles", []),
        }
        log.debug(user_data)

        content, ctype = get_qr()
        vc_type = Configuration.objects.filter(key=CONFIG_KEY_VC_TYPES, tag="employee").first()
        if not vc_type:
            raise Exception("VC type for employee is not configured")
        if not get_profile():
            raise Exception("PROFILE not configured")
        subject_id = f"{claims.get('email')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        preauth_register = identify_register_preauth_code(get_profile().value, vc_type.value, subject_id)
        print(preauth_register)
        IssuedCredential.objects.create(
            vc_type=vc_type.value,
            subject_id=subject_id,
            preauth_code=preauth_register["preauth_code"],
            preauth_code_expires_in=preauth_register["expires_in"],
            token_claims=claims,
            status=IssuedCredentialStatus.PENDING.value,
        )
        return HttpResponse(content, content_type=ctype)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"detail": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_description="List available identifier types for issuance",
    responses={
        200: openapi.Response(
            description="List of identifier types",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "identifier_types": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING),
                    )
                },
            ),
        ),
        401: "Unauthorized",
    },
    request_body=ListIdentifiersSerializer,
)
@api_view(["POST"])
def list_identifiers(request):
    serializer = ListIdentifiersSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse(data=serializer.errors, status=400)
    data = serializer.validated_data
    if get_profile() and get_profile().value != data["profile"]:
        return JsonResponse(
            {"detail": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    issued_credential = IssuedCredential.objects.filter(vc_type=data["vc_type"], subject_id=data["subject_id"]).first()
    if not issued_credential:
        return JsonResponse(
            {"detail": "No issued credential found for the given profile, vc_type and subject_id"},
            status=status.HTTP_404_NOT_FOUND,
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
        return JsonResponse(data=serializer.errors, status=400)
    data = serializer.validated_data
    if get_profile() and get_profile().value != data["profile"]:
        return JsonResponse(
            {"detail": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    issued_credential = IssuedCredential.objects.filter(vc_type=data["vc_type"], subject_id=data["subject_id"]).first()
    if not issued_credential:
        return JsonResponse(
            {"detail": "No issued credential found for the given profile, vc_type and subject_id"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        org_legal_id = issued_credential.token_claims.get("org_legal_id")
        if issued_credential.vc_type.lower().startswith("representative"):
            data = tmf_get_organization(org_legal_id)
        else:
            data = tmf_get_individual(org_legal_id)
        issued_credential.tmf_claims = data
        issued_credential.save()
        return JsonResponse(data, safe=False)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error fetching organization data from TMF API: {e}")
        return JsonResponse(
            {"detail": f"{e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method="post",
    operation_description="Handle notifications from Identfy Connector",
    responses={
        200: "OK",
        400: "Bad Request",
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
            return JsonResponse(data=serializer.errors, status=400)
        data = serializer.validated_data
        if get_profile() and get_profile().value != data["profile"]:
            return JsonResponse(
                {"detail": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        issued_credential = IssuedCredential.objects.filter(subject_id=data["subject_id"]).first()
        if not issued_credential:
            return JsonResponse(
                {"detail": "No issued credential found for the given profile, vc_type and subject_id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Process the notification
        log.info(f"Processing notification for credential ID: {data['credential_id']}, type: {data['type']}")
        if issued_credential.credential_id and issued_credential.credential_id != data["credential_id"]:
            log.warning(
                f"Credential ID mismatch: existing {issued_credential.credential_id}, notification {data['credential_id']}"
            )
            return JsonResponse(
                {"detail": "Credential ID mismatch"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not issued_credential.credential_id and data["credential_id"]:
            # Update the credential ID if not set before
            issued_credential.credential_data = identify_get_credential(data["credential_id"])

        issued_credential.credential_id = data["credential_id"]
        issued_credential.status = data["type"]
        issued_credential.update_at = datetime.now()
        issued_credential.save()

        return JsonResponse({"detail": "Notification processed successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Error processing notification: {e}")
        return JsonResponse(
            {"detail": f"Internal error: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
