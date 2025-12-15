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


from typing import Any, Optional, Tuple

from django.http import HttpRequest
from jose.exceptions import ExpiredSignatureError

from common.keycloak import verify_jwt


def get_bearer_token_from_request(request: HttpRequest) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def virifity_token_and_get_payload(request: HttpRequest) -> Tuple[Optional[dict[str, Any]]]:
    token = get_bearer_token_from_request(request)
    if not token:
        raise Exception("Missing Bearer token")
    try:
        return verify_jwt(token)
    except ExpiredSignatureError:
        raise Exception("Token expired")
    except Exception as e:
        print(e)
        raise Exception(f"Invalid token: {e}")
