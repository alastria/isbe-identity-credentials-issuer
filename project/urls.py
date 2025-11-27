
"""<SITE_NAME> URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import logging

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import redirect
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from project.settings import BACKEND_DOMAIN, SITE_NAME
from user.views import CustomResetPasswordRequestToken, LoginViewCustom, password_change

log = logging.getLogger(__name__)


class Health(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request):
        log.info("api health")
        return JsonResponse(
            {
                "status": "ok",
                "debug": settings.DEBUG,
            }
        )


def f_403(request, exception):
    return HttpResponseForbidden("Forbidden")
    # return render(request, "403.html", {})


def f_404(request, exception):
    return HttpResponseNotFound("Not found")
    # return render(request, "404.html", {})


def f_500(request):
    return HttpResponseServerError("Server error")
    # return render(request, "500.html", {})


handler403 = f_403
handler404 = f_404
handler500 = f_500

admin.site.site_header = f"{SITE_NAME}"
admin.site.index_title = f"{SITE_NAME}"
admin.site.site_title = f"{SITE_NAME}"


schema_view = get_schema_view(
    openapi.Info(
        title=f"{SITE_NAME} API",
        default_version="v1",
        description=f"This api is {SITE_NAME}",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    url=BACKEND_DOMAIN,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("api/v1/health", Health.as_view(), name="api-health"),
    path("api/v1/api-token-auth", LoginViewCustom.as_view()),
    path(
        "api/v1/custom/password-reset",
        CustomResetPasswordRequestToken.as_view(),
        name="custom-reset-password-request",
    ),
    path(
        "api/v1/password-reset",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("api/v1/password-change", password_change, name="password_change"),
    path(
        "password-reset",
        auth_views.PasswordResetView.as_view(html_email_template_name="registration/custom_password_reset_email.html"),
        name="admin_password_reset",
    ),
    path(
        "password-reset",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "password-reset/done",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("admin/", admin.site.urls),
    path("", lambda x: redirect("admin/")),
    path("api/v1/issuance/", include("issuance.urls")),
    path("", include("django_prometheus.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
