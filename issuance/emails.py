
import logging
import os
import traceback
from email.mime.image import MIMEImage

import sentry_sdk
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from project import settings

logger = logging.getLogger("django")

PATH_LOGO = os.path.join(settings.BASE_DIR, "issuance/static/images/logo_isbe.png")


def send_email_user_enrollment(email_to, qr_content):
    context = {"url": f"{settings.FRONTEND_URL}/user-enrollment", "qr_content": qr_content}

    email_plaintext_message = render_to_string("email/isbe/user_enrollment.html", context)
    email_html_message = render_to_string("email/isbe/user_enrollment.html", context)

    try:
        msg = EmailMultiAlternatives(
            _("[ISBE] Has sido designado para completar el proceso técnico de enrolamiento en "),
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
