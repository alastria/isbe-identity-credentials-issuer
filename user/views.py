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


import json

from django.contrib.auth import authenticate, password_validation
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.views import ResetPasswordRequestToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView

from user.serializers import ChangePasswordSerializer, CustomTokenLoginSerializer

"""
IMPORTANTE:
    Deallocar los objetos creados dentro de los endpoints para liberar memoria. Una vez utilizado el objeto igualarlo a
    None.

    Para comprobar que la referencia se ha eliminado correctamente hacer uso del módulo weakref de la siguiente manera:
        obj = MyClass()
        obj_ref = weakref.ref(obj)
        obj = None
        if obj_ref() is None:
            print("La referencia ha sido eliminada correctamente")
        else:
            print("La referencia no ha sido eliminada correctamente")
"""


class LoginViewCustom(TokenObtainPairView):
    serializer_class = CustomTokenLoginSerializer


class CustomResetPasswordRequestToken(ResetPasswordRequestToken):
    last_url = None

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data["url"]:
            CustomResetPasswordRequestToken.last_url = data["url"]
        else:
            CustomResetPasswordRequestToken.last_url = None
        return super().post(request, args, kwargs)


@swagger_auto_schema(
    method="post",
    operation_description="Change password",
    responses={200: openapi.Response("")},
    request_body=ChangePasswordSerializer,
)
@api_view(["POST"])
def password_change(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse(data=serializer._errors, status=400)

    old_password = serializer["old_password"].value
    new_password = serializer["new_password"].value
    username = serializer["username"].value

    user = authenticate(username=username, password=old_password)
    if not user:
        return JsonResponse(
            data={"error": _("Usuario o contraseña no válidos")}, status=400
        )

    try:
        password_validation.validate_password(new_password)
    except Exception as e:
        return JsonResponse(data={"error": " ".join(e.messages)}, status=400)
    user.set_password(new_password)
    user.save()

    return JsonResponse({"status": "OK"}, safe=False)
