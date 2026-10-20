#!/usr/bin/env python3
"""
honey_readme.py — README.md + LICENSE generator for the Honey mod loader.

Usage:
    python honey_readme.py                          # interactive prompt
    python honey_readme.py --out README.md          # custom README path
    python honey_readme.py --license-out LICENSE    # custom license path
    python honey_readme.py --non-interactive        # scripted defaults
    python honey_readme.py --force                  # overwrite existing files

No third-party dependencies. Python 3.8+.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Brand vocabulary — edit here if the naming changes.
# ---------------------------------------------------------------------------
BRAND = {
    "product": "Honey",
    "tagline": "A version-stable mod loader for Minecraft.",
    "runtime": "Hive",
    "registry": "Comb",
    "events": "Nectar",
    "shim": "Wax",
    "dev_env": "Apiary",
    "mascot": "🐝",
}


# ---------------------------------------------------------------------------
# License templates
# ---------------------------------------------------------------------------
# {year} and {author} are substituted at render time.
LICENSE_TEMPLATES: Dict[str, str] = {
    "MIT": """\
MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "Apache-2.0": """\
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Copyright {year} {author}

   [Full Apache-2.0 text: https://www.apache.org/licenses/LICENSE-2.0.txt]
""",
    "GPL-3.0": """\
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) {year} {author}

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.

 [Full GPL-3.0 text: https://www.gnu.org/licenses/gpl-3.0.txt]
""",
    "LGPL-3.0": """\
                   GNU LESSER GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) {year} {author}

 This library is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library.  If not, see <https://www.gnu.org/licenses/>.

 [Full LGPL-3.0 text: https://www.gnu.org/licenses/lgpl-3.0.txt]
""",
    "MPL-2.0": """\
Mozilla Public License Version 2.0

Copyright (c) {year} {author}

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

[Full MPL-2.0 text: https://www.mozilla.org/en-US/MPL/2.0/]
""",
    "BSD-3-Clause": """\
BSD 3-Clause License

Copyright (c) {year} {author}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""",
    "Unlicense": """\
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
""",
}

LICENSE_CHOICES = list(LICENSE_TEMPLATES.keys()) + ["Custom"]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@dataclass
class ProjectInfo:
    name: str = BRAND["product"]
    tagline: str = BRAND["tagline"]
    description: str = ""
    mc_version: str = "26.3"
    java_version: str = "21"
    status: str = "pre-alpha"
    license: str = "MIT"
    license_holder: str = ""
    repo_url: str = ""
    author: str = ""
    features: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    non_goals: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    install_steps: List[str] = field(default_factory=list)
    build_steps: List[str] = field(default_factory=list)
    roadmap: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "honey"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(130)
    return value or default


def ask_list(prompt: str, default: Optional[List[str]] = None) -> List[str]:
    default = default or []
    shown = ", ".join(default)
    raw = ask(prompt, shown)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def bullet(items: List[str], fallback: str = "_TBD_") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def numbered(items: List[str], fallback: str = "_TBD_") -> str:
    if not items:
        return f"1. {fallback}"
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))


# ---------------------------------------------------------------------------
# Interactive collection
# ---------------------------------------------------------------------------
def collect_interactive(info: ProjectInfo) -> ProjectInfo:
    print(f"\n{BRAND['mascot']}  {BRAND['product']} generator\n" + "-" * 40)
    info.name = ask("Project name", info.name)
    info.tagline = ask("One-line tagline", info.tagline)
    info.description = ask(
        "Short description (1-2 sentences)",
        "Honey is a mod loader that guarantees runtime-level compatibility "
        "across Minecraft versions through a stable abstraction layer.",
    )
    info.mc_version = ask("Target Minecraft version", info.mc_version)
    info.java_version = ask("Target Java version", info.java_version)
    info.status = ask("Project status", info.status)

    print("\n-- License --")
    print("Available: " + ", ".join(LICENSE_CHOICES))
    info.license = ask("License", info.license)
    default_holder = info.author or "your name"
    info.license_holder = ask("Copyright holder (for LICENSE file)", default_holder)

    info.repo_url = ask(
        "Repository URL",
        f"https://github.com/{slugify(info.name)}/{slugify(info.name)}",
    )
    info.author = ask("Author / maintainer", info.author or info.license_holder)

    info.features = ask_list(
        "Features (comma-separated)",
        [
            f"Stable abstraction layer ({BRAND['shim']}) isolates mods from MC internals",
            f"Event system ({BRAND['events']}) with typed hooks like OnPlayerJoin",
            "Deterministic compatibility guarantees at runtime, not post-hoc patching",
        ],
    )
    info.goals = ask_list(
        "Goals (comma-separated)",
        [
            f"Run mods written against {info.mc_version} on future versions without recompilation",
            "Define a stable IR/API surface before exposing it to mod authors",
        ],
    )
    info.non_goals = ask_list(
        "Non-goals (comma-separated)",
        [
            "Replacing Fabric/NeoForge for existing mods",
            "Bytecode-patching arbitrary mods after the fact",
        ],
    )
    info.prerequisites = ask_list(
        "Prerequisites (comma-separated)",
        [f"Java {info.java_version}+", f"Minecraft {info.mc_version}"],
    )
    info.install_steps = ask_list(
        "Install steps (comma-separated)",
        ["Download the latest release", "Drop the loader jar into your launcher's mods folder"],
    )
    info.build_steps = ask_list(
        "Build steps (comma-separated)",
        ["./gradlew build", "The output jar is in build/libs/"],
    )
    info.roadmap = ask_list(
        "Roadmap items (comma-separated)",
        [
            f"{info.mc_version} adapter spec for the stable layer",
            f"{BRAND['events']} event bus prototype",
            "First end-to-end mod running on the abstraction layer",
        ],
    )
    return info


# ---------------------------------------------------------------------------
# Rendering — README
# ---------------------------------------------------------------------------
def render_readme(info: ProjectInfo) -> str:
    today = _dt.date.today().isoformat()
    mascot = BRAND["mascot"]

    parts: List[str] = []
    parts.append(f"# {mascot} {info.name}\n")
    parts.append(f"> {info.tagline}\n")
    parts.append(
        f"**Status:** {info.status} · **Target:** Minecraft {info.mc_version} · "
        f"**Java:** {info.java_version}+ · **License:** {info.license}\n"
    )

    if info.description:
        parts.append("## Overview\n")
        parts.append(info.description.strip() + "\n")

    parts.append("## Features\n")
    parts.append(bullet(info.features) + "\n")

    parts.append("## Architecture\n")
    parts.append(
        f"{info.name} is built around a stable abstraction layer — the **{BRAND['shim']}** layer — "
        "that sits between mods and Minecraft's internals. Mods target this layer's contracts, "
        "so changes in the underlying game do not force mod authors to re-port.\n"
    )
    parts.append("| Component | Role |")
    parts.append("| --- | --- |")
    parts.append(f"| {BRAND['shim']} | Stable abstraction / compatibility layer |")
    parts.append(f"| {BRAND['runtime']} | Loader runtime |")
    parts.append(f"| {BRAND['registry']} | Module / extension registry |")
    parts.append(f"| {BRAND['events']} | Typed event bus (e.g. `OnPlayerJoin`) |")
    parts.append(f"| {BRAND['dev_env']} | Development & test environment |")
    parts.append("")

    parts.append("## Goals\n")
    parts.append(bullet(info.goals) + "\n")
    parts.append("## Non-goals\n")
    parts.append(bullet(info.non_goals) + "\n")

    parts.append("## Prerequisites\n")
    parts.append(bullet(info.prerequisites) + "\n")

    parts.append("## Installation\n")
    parts.append(numbered(info.install_steps) + "\n")

    parts.append("## Building from source\n")
    parts.append("```bash\n" + "\n".join(info.build_steps) + "\n```\n")

    parts.append("## Roadmap\n")
    parts.append(bullet(info.roadmap) + "\n")

    parts.append("## Contributing\n")
    parts.append(
        "Contributions are welcome. Please open an issue before starting large changes. "
        "See [CONTRIBUTING.md](CONTRIBUTING.md) for details.\n"
    )

    parts.append("## License\n")
    parts.append(
        f"Released under the {info.license} license. See [LICENSE.md](LICENSE.md) "
        "for the full text.\n"
    )

    parts.append("---")
    parts.append(f"_Generated {today} by honey_readme.py — edit freely, then delete this line._")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Rendering — LICENSE
# ---------------------------------------------------------------------------
def render_license(info: ProjectInfo) -> str:
    year = _dt.date.today().year
    holder = info.license_holder or info.author or "the copyright holder"

    key = info.license.strip()
    # Normalize a few common aliases.
    aliases = {
        "apache": "Apache-2.0",
        "apache2": "Apache-2.0",
        "apache 2.0": "Apache-2.0",
        "gpl": "GPL-3.0",
        "gpl3": "GPL-3.0",
        "lgpl": "LGPL-3.0",
        "lgpl3": "LGPL-3.0",
        "mpl": "MPL-2.0",
        "mpl2": "MPL-2.0",
        "bsd": "BSD-3-Clause",
        "bsd3": "BSD-3-Clause",
        "mit": "MIT",
        "unlicense": "Unlicense",
    }
    normalized = aliases.get(key.lower(), key)

    template = LICENSE_TEMPLATES.get(normalized)
    if template is None:
        # Custom / unknown license: emit a placeholder the user can fill in.
        return (
            f"{info.license} License\n\n"
            f"Copyright (c) {year} {holder}\n\n"
            "[Paste the full license text here. If this is a standard license, "
            "run the generator again and pick one from the list instead.]\n\n"
            f"See https://choosealicense.com/ for help choosing a license.\n"
        )

    return template.format(year=year, author=holder)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=f"Generate README.md and LICENSE.md for the {BRAND['product']} mod loader.",
    )
    p.add_argument("--out", default="README.md", help="README output path (default: README.md)")
    p.add_argument("--license-out", default="LICENSE.md",
                   help="LICENSE output path (default: LICENSE.md)")
    p.add_argument("--no-readme", action="store_true", help="Skip README generation")
    p.add_argument("--no-license", action="store_true", help="Skip LICENSE generation")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    p.add_argument("--non-interactive", action="store_true", help="Use defaults, no prompts")
    p.add_argument("--name", default=BRAND["product"], help="Project name")
    p.add_argument("--tagline", default=BRAND["tagline"], help="Tagline")
    p.add_argument("--mc-version", default="26.3", help="Target Minecraft version")
    p.add_argument("--java-version", default="21", help="Target Java version")
    p.add_argument("--license", default="MIT", help="SPDX-ish license name, or 'Custom'")
    p.add_argument("--author", default="", help="Author / copyright holder")
    p.add_argument("--status", default="pre-alpha", help="Project status")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    readme_path = Path(args.out)
    license_path = Path(args.license_out)

    # Preflight: refuse to clobber unless --force.
    targets = []
    if not args.no_readme:
        targets.append(readme_path)
    if not args.no_license:
        targets.append(license_path)
    for path in targets:
        if path.exists() and not args.force:
            print(f"error: {path} already exists (use --force to overwrite)", file=sys.stderr)
            return 1

    info = ProjectInfo(
        name=args.name,
        tagline=args.tagline,
        mc_version=args.mc_version,
        java_version=args.java_version,
        license=args.license,
        status=args.status,
        author=args.author,
    )

    if not args.non_interactive:
        info = collect_interactive(info)
    else:
        info.description = (
            f"{info.name} is a mod loader that guarantees runtime-level compatibility "
            "across Minecraft versions through a stable abstraction layer."
        )
        info.features = [
            f"Stable abstraction layer ({BRAND['shim']}) isolates mods from MC internals",
            f"Event system ({BRAND['events']}) with typed hooks like OnPlayerJoin",
            "Deterministic compatibility guarantees at runtime, not post-hoc patching",
        ]
        info.goals = [
            f"Run mods written against {info.mc_version} on future versions without recompilation"
        ]
        info.non_goals = ["Replacing Fabric/NeoForge for existing mods"]
        info.prerequisites = [f"Java {info.java_version}+", f"Minecraft {info.mc_version}"]
        info.install_steps = [
            "Download the latest release",
            "Drop the loader jar into your mods folder",
        ]
        info.build_steps = ["./gradlew build"]
        info.roadmap = [f"{info.mc_version} adapter spec for the stable layer"]
        info.license_holder = info.author or "the copyright holder"

    if not args.no_readme:
        readme = render_readme(info)
        readme_path.write_text(readme, encoding="utf-8")
        print(f"{BRAND['mascot']} wrote {readme_path} ({len(readme)} bytes)")

    if not args.no_license:
        license_text = render_license(info)
        license_path.write_text(license_text, encoding="utf-8")
        print(f"{BRAND['mascot']} wrote {license_path} ({len(license_text)} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())