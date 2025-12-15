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


from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name"]


class CustomTokenLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user_id"] = user.id
        token["username"] = user.username
        token["email"] = user.email

        return token

    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenLoginSerializer, self).validate(attrs)
        # Custom data you want to include
        data.update({"user_id": self.user.id})
        data.update({"username": self.user.username})
        data.update({"email": self.user.email})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    old_password = serializers.CharField()
    new_password = serializers.CharField()
