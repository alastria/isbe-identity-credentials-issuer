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

import os

# Insert standard header into code files

HEADER_CONTAINS = "Copyright (c) 2025 Comunidad de Madrid & Alastria"

HEADER_PY = """# Copyright (c) 2025 Comunidad de Madrid & Alastria
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
# limitations under the License."""

HEADER_JS = """/**
* Copyright (c) 2025 Comunidad de Madrid & Alastria
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
*
* You may obtain a copy of the License at
* [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0 "http://www.apache.org/licenses/license-2.0")
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/"""


def insert_header_in_code_file(file_path, header):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    if HEADER_CONTAINS in content[:500]:
        return  # Header already present
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(header + "\n\n" + content)
        print(f"Inserted header in {file_path}")


if __name__ == "__main__":
    # Define the directory to scan for code files
    directory_to_scan = "."

    # Define the file extensions to consider as code files
    code_file_extensions = {".py", ".js", ".ts"}

    for root, _, files in os.walk(directory_to_scan):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in code_file_extensions):
                file_path = os.path.join(root, file_name)
                if "/." in file_path or file_name.startswith(".") or "node_modules" in file_path:
                    continue  # Skip hidden files and directories
                if file_name.endswith(".py"):
                    insert_header_in_code_file(file_path, HEADER_PY)
                elif file_name.endswith((".js", ".ts")):
                    insert_header_in_code_file(file_path, HEADER_JS)
