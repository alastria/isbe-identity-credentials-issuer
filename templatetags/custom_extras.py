
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from project import settings

register = template.Library()


@register.filter()
@stringfilter
def vertical_bar_to_html_br(value):
    return mark_safe(value.replace("|", "<br />"))


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


# settings value
@register.simple_tag
def get_google_tag_active():
    return settings.GOOGLE_TAG_ACTIVE
