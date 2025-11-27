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


from rest_framework import serializers


class IssueEmployeeCredentialSerializer(serializers.Serializer):
    power = serializers.ListField(child=serializers.DictField(), required=True)


class IssueRepresentativeCredentialSerializer(serializers.Serializer):
    power = serializers.ListField(child=serializers.DictField(), required=True)
    employeId = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    firstName = serializers.CharField(required=True)
    lastname = serializers.CharField(required=True)


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
    organization_identifier = serializers.CharField(required=True)
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
