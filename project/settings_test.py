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


import dj_database_url
import os

from project.settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": "5432",
    }
}

database_url = os.environ.get("DATABASE_URL", None)
if database_url:
    DATABASES["default"] = dj_database_url.parse(database_url, conn_max_age=600)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = True
SECURE_SSL_REDIRECT = False

# DIGITAL IDENTITY

SECURE_SSL_REDIRECT = False
ALASTRIA_NODE_IP = "http://63.33.206.111/rpc"
WEALIZE_NODE_IP = "http://15.188.13.9/rpc"
BACKEND_DOMAIN = "http://192.168.1.50:8000"
ISSUER_PRIVATE_KEY = "0x7127ecd378d08bcd69e00838137fc71bb58c453f7e058aa1c6d5e683da88052d"
ISSUER_ADDRESS = "0x51deb237b0dff3b91b5d9ba1a39aaeab47993554"
ISSUER_DID = "did:ala:quor:redT:012b19f0337ff5b928fe8f8e8e0a6b2a105abff2"
