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


import base64
import logging
import re
import traceback

from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from project import settings


def encode_text(text, secret):
    encoded = []
    for i, c in enumerate(text):
        encoded.append(chr(ord(c) ^ ord(secret[i % len(secret)])))
    return "".join(encoded)


def decode_text(encoded_text, secret):
    return encode_text(base64.b64decode(encoded_text).decode("utf-8"), secret)  # XORing again decodes it


def send_bulk_emails(subject, html_msg, sender, recipients):
    # Conecte al servidor SMTP usando STARTTLS

    # Create a secure SSL context
    context = ssl.create_default_context()

    print(f"Enviando email from {settings.EMAIL_HOST}:{settings.EMAIL_PORT} {settings.EMAIL_HOST_USER} ")
    # with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_server:
    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as smtp_server:
        smtp_server.ehlo()
        smtp_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)  # Inicie sesión en el servidor

        # Recorra cada destinatario y envíeles un email individual
        for recipient in recipients:
            # msg = MIMEText(body, "html")  # Cree un objeto MIMEText con el cuerpo del email en formato HTML
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject  # Establezca el asunto del email
            msg["From"] = sender  # Establezca el remitente
            msg["To"] = recipient  # Establezca el destinatario actual

            plain_message = strip_tags(re.sub(r"<head>.*?</head>", "", html_msg, flags=re.DOTALL))
            part1 = MIMEText(plain_message, "plain")
            part2 = MIMEText(html_msg, "html")
            msg.attach(part1)
            msg.attach(part2)

            errs = smtp_server.sendmail(sender, recipient, msg.as_string())  # Envíe el email
            if errs:
                print(f"Error enviando email a {recipient}: {errs}")
            else:
                print(f"¡Mensaje enviado a {recipient}!")


def send_test_email(to_email: str):
    subject = "Test Email from ISBE Identity Credentials Issuer"
    html_msg = "<html><body><h1>This is a test email</h1><p>If you received this email, the configuration is correct.</p></body></html>"
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = [to_email]

    try:
        send_bulk_emails(subject, html_msg, sender, recipients)
        print(f"Test email sent to {to_email}")
    except Exception as e:
        traceback.print_exc()
        print(f"Failed to send test email to {to_email}: {e}")


if __name__ == "__main__":
    send_test_email("jdavidlb27@gmail.com")
    print("Test email function executed.")
