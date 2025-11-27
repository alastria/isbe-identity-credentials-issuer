
import logging
import os
from email.mime.image import MIMEImage

import sentry_sdk
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.signals import reset_password_token_created

from user.views import CustomResetPasswordRequestToken

logger = logging.getLogger("django")

PATH_LOGO = os.path.join(settings.BASE_DIR, "user/static/images/logo_demo.png")


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    context = {"reset_password_url": f"{settings.FRONTEND_URL}/password-reset/{reset_password_token.key}"}

    if CustomResetPasswordRequestToken.last_url:
        context["reset_password_url"] = f"{CustomResetPasswordRequestToken.last_url}?token={reset_password_token.key}"
        CustomResetPasswordRequestToken.last_url = None
    email_plaintext_message = render_to_string("email/password_reset_email.txt", context)
    email_html_message = render_to_string("email/password_reset_email.html", context)

    try:
        msg = EmailMultiAlternatives(
            _("Solicitud para restablecer contraseña en Demo"),
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [reset_password_token.user.email],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.mixed_subtype = "related"

        fp = open(PATH_LOGO, "rb")
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header("Content-ID", "<logo_image>")
        msg_img.add_header("Content-Disposition", "attachment;filename=logo_image.png")
        msg.attach(msg_img)

        msg.send()
    except Exception as e:
        logger.error("Error in password_reset_token_created")
        logger.error(e)
        sentry_sdk.capture_exception(e)
        raise e


@receiver(post_save, sender=User)
def send_welcome_message(sender, created, instance, **kwargs):
    if not created:
        return

    if not instance.email:
        return

    email_plaintext_message = render_to_string("email/welcome_message.html", {"web_app_url": settings.BACKEND_DOMAIN})
    email_html_message = render_to_string("email/welcome_message.html", {"web_app_url": settings.BACKEND_DOMAIN})
    try:
        msg = EmailMultiAlternatives(
            _("Bienvenido a Demo"),
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.mixed_subtype = "related"

        fp = open(PATH_LOGO, "rb")
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header("Content-ID", "<logo_image>")
        msg_img.add_header("Content-Disposition", "attachment;filename=logo_image.png")
        msg.attach(msg_img)

        msg.send()
    except Exception as e:
        logger.error("Error in send_welcome_message:")
        logger.error(e)
        sentry_sdk.capture_exception(e)
        raise e
