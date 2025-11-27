
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

from .conf import method_var, path_var, request_id_var


def request_id_middleware(get_response: Callable[[HttpRequest], HttpResponse]):
    def middleware(request: HttpRequest) -> HttpResponse:
        rid = request.META.get("HTTP_X_REQUEST_ID") or uuid.uuid4().hex
        request.id = rid

        # Bind request info to contextvars for logging
        tok_r = request_id_var.set(rid)
        tok_p = path_var.set(request.path)
        tok_m = method_var.set(request.method)
        try:
            response = get_response(request)
        finally:
            # Avoid context bleed between requests
            request_id_var.reset(tok_r)
            path_var.reset(tok_p)
            method_var.reset(tok_m)

        response["X-Request-ID"] = rid
        return response

    return middleware
