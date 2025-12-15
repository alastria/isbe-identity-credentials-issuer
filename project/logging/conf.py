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
