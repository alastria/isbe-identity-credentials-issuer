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
