from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

CONFIG_KEY_VC_TYPES = "VC_TYPES"
CONFIG_KEY_PROFILE = "PROFILE"


class Configuration(models.Model):
    key = models.CharField(max_length=100)
    value = models.TextField()
    tag = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.key}: {self.value}"


class IssuedCredential(models.Model):
    vc_type = models.CharField(_("VC Tpre"), max_length=200)
    subject_id = models.CharField(_("Subject ID"), max_length=200)
    preauth_code = models.CharField(_("Preauth code"), max_length=200)
    preauth_code_expires_in = models.DateTimeField(_("Preauth code expiry time"))
    status = models.CharField(_("Status"), max_length=50)  # e.g., pending, active, revoked
    creation_at = models.DateTimeField(_("Creation time"), auto_now_add=True)
    update_at = models.DateTimeField(_("Update time"), blank=True, null=True)
    token_claims = models.JSONField(_("Token Claims"), blank=True, null=True)
    tmf_claims = models.JSONField(_("TMF Claims"), blank=True, null=True)
    credential_id = models.CharField(_("Credential ID"), max_length=200, blank=True, null=True)
    credential_data = models.JSONField(_("Credential data"), blank=True, null=True)

    def __str__(self):
        return f"Credential {self.vc_type} for {self.subject_id} update at {self.update_at}"

    class Meta:
        verbose_name = _("Issued Credential")
        verbose_name_plural = _("Issued Credentials")
