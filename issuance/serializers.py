from rest_framework import serializers


class ListIdentifiersSerializer(serializers.Serializer):
    app = serializers.CharField(required=True)
    instance = serializers.CharField(required=True)
    profile = serializers.CharField(required=True)
    vc_type = serializers.CharField(required=True)
    subject_id = serializers.CharField(required=True)


class GetClaimsSerializer(serializers.Serializer):
    app = serializers.CharField(required=True)
    instance = serializers.CharField(required=True)
    profile = serializers.CharField(required=True)
    vc_identifier = serializers.CharField(required=True)
    subject_id = serializers.CharField(required=True)
    vc_identifier = serializers.CharField(required=False, allow_blank=True)


class NotificationSerializer(serializers.Serializer):
    app = serializers.CharField(required=True)
    instance = serializers.CharField(required=True)
    profile = serializers.CharField(required=True)
    subject_id = serializers.CharField(required=True)
    credential_id = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class GetCredentialsByOrganizationIdentitySerializer(serializers.Serializer):
    credential_id = serializers.CharField(required=False, allow_blank=True)
    organization_identity = serializers.CharField(required=True)
    vc_type = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    creation_at = serializers.DateTimeField(required=False)
    update_at = serializers.DateTimeField(required=False)


class ListGetCredentialsByOrganizationIdentitySerializer(serializers.Serializer):
    credentials = GetCredentialsByOrganizationIdentitySerializer(many=True)
    page = serializers.IntegerField()
    num_pages = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total = serializers.IntegerField()
