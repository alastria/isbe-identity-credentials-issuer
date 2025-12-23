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
import traceback
from email.mime.image import MIMEImage

import sentry_sdk
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from issuance.models import CONFIG_URL_ANDROID, CONFIG_URL_IOS, CONFIG_URL_LOGIN, Configuration
from project import settings

logger = logging.getLogger("django")

PATH_LOGO = os.path.join(settings.BASE_DIR, "issuance/static/images/logo_isbe.png")


def send_email_user_enrollment(email_to, qr_content):
    url_ios = Configuration.objects.filter(key=CONFIG_URL_IOS).first()
    url_android = Configuration.objects.filter(key=CONFIG_URL_ANDROID).first()
    url_login = Configuration.objects.filter(key=CONFIG_URL_LOGIN).first()

    context = {
        "url_login": url_login.value if url_login else "#",
        "url_ios": url_ios.value if url_ios else "#",
        "url_android": url_android.value if url_android else "#",
        "qr_content": qr_content,
    }

    email_plaintext_message = render_to_string("email/isbe/user_enrollment.html", context)
    email_html_message = render_to_string("email/isbe/user_enrollment.html", context)

    try:
        msg = EmailMultiAlternatives(
            _("[ISBE] Bienvenida y acceso al área privada de ISBE"),
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [email_to],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.mixed_subtype = "related"

        fp = open(PATH_LOGO, "rb")
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header("Content-ID", "<logo_image>")
        msg_img.add_header("Content-Disposition", "attachment;filename=logo_image.png")
        msg.attach(msg_img)

        msg_qr = MIMEImage(qr_content)
        msg_qr.add_header("Content-ID", "<qr_image>")
        msg_qr.add_header("Content-Disposition", "attachment;filename=qr_image.png")
        msg.attach(msg_qr)

        msg.send()
        logger.info(f"Email sent to {email_to} for user enrollment.")
    except Exception as e:
        logger.error("Error in email_user_enrollment:")
        logger.error(e)
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        raise e
