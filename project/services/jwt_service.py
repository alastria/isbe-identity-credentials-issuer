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
import os
from datetime import datetime

import jwt
from django.conf import settings

from django.conf import settings

logger = logging.getLogger("django")

PATH_FILES = settings.MEDIA_ROOT
if not os.path.exists(PATH_FILES):
    # Create a new directory because it does not exist
    os.makedirs(PATH_FILES)
    logger.info(f"The temporal directory is created: {PATH_FILES}")


class JWTService:
    @staticmethod
    def decodeJWT(token) -> str:
        return jwt.decode(token, settings.JWT_PASSWORD, algorithms=["HS256"])

    @staticmethod
    def encodeJWT(payload) -> str:
        return jwt.encode(payload, settings.JWT_PASSWORD, algorithm="HS256")

    def isJwtExpired(token) -> bool:
        try:
            pl = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": True},
                algorithms=["HS256"],
            )
            timestamp = int(datetime.now().timestamp())
            if timestamp >= pl["exp"]:
                print("Expired jwt")
                return True
            return False
        except jwt.ExpiredSignatureError:
            print("Expired jwt")
            return True
