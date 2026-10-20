# 🐝 Honey Loader

> A version-stable mod loader for Minecraft.

**Status:** pre-alpha · **Target:** Minecraft 26.3 · **Java:** 25+ · **License:** MIT

## Overview

Honey is a mod loader that guarantees runtime-level compatibility across Minecraft versions through a stable abstraction layer.

## Features

- Stable abstraction layer (Wax) isolates mods from MC internals
- Event system (Nectar) with typed hooks like OnPlayerJoin
- Deterministic compatibility guarantees at runtime
- not post-hoc patching

## Architecture

Honey Loader is built around a stable abstraction layer — the **Wax** layer — that sits between mods and Minecraft's internals. Mods target this layer's contracts, so changes in the underlying game do not force mod authors to re-port.

| Component | Role |
| --- | --- |
| Wax | Stable abstraction / compatibility layer |
| Hive | Loader runtime |
| Comb | Module / extension registry |
| Nectar | Typed event bus (e.g. `OnPlayerJoin`) |
| Apiary | Development & test environment |

## Goals

- Run mods written against 26.3 on future versions without recompilation
- Define a stable IR/API surface before exposing it to mod authors

## Non-goals

- Replacing Fabric/NeoForge for existing mods
- Bytecode-patching arbitrary mods after the fact

## Prerequisites

- Java 25+
- Minecraft 26.3

## Installation

1. Download the latest release
2. Drop the loader jar into your launcher's mods folder

## Building from source

```bash
./gradlew build
The output jar is in build/libs/
```

## Roadmap

- 26.3 adapter spec for the stable layer
- Nectar event bus prototype
- First end-to-end mod running on the abstraction layer

## Contributing

Contributions are welcome. Please open an issue before starting large changes. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Released under the MIT license. See [LICENSE.md](LICENSE.md) for the full text.

---
_Generated 2026-10-20 by honey_readme.py — edit freely, then delete this line._
