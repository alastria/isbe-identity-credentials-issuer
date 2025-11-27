
import logging
import contextvars

request_id_var = contextvars.ContextVar("request_id", default=None)
path_var = contextvars.ContextVar("path", default=None)
method_var = contextvars.ContextVar("method", default=None)

class ContextVarsFilter(logging.Filter):
    """Inject request_id/path/method into every log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "-"
        record.path = path_var.get() or "-"
        record.method = method_var.get() or "-"
        return True
