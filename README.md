## Project Chimera – Autonomous Influencer System

Project Chimera is an **autonomous influencer agent swarm** designed to run multi-channel social campaigns inside the **OpenClaw / Moltbook agent social network**.  
It follows the **Planner / Worker / Judge** FastRender Swarm pattern and is built to be spec-driven, auditable, and safe-by-default.

---

## Quick Start

If you have **Python 3.11** and `pip` installed, you can get going quickly from the repo root using either **raw `pip` + `pytest`** or the **Makefile**.

### Option 1 – Direct `pip` + `pytest`

```bash
pip install -e .
pytest -q
```

This installs Project Chimera in editable mode along with its dependencies (from `pyproject.toml`), then runs the test suite with `pytest` in quiet mode.

### Option 2 – Using `make` (recommended)

```bash
make setup
make test
```

`make setup` uses the `Makefile` to upgrade `pip`, install `uv`, and install the package and its dependencies. `make test` runs the tests via `pytest` using the existing test configuration.

---

## Getting Started

- **Python version**: 3.11 (see `Dockerfile` and `pyproject.toml`).
- **Package manager**: `uv` (installed automatically by the `setup` target).

### Local setup

```bash
make setup
```

This will:

- Upgrade `pip`.
- Install `uv`.
- Install the Project Chimera package and its dependencies into your system environment.

---

## Running Tests

### Via Makefile (recommended)

```bash
make test
```

This runs the Python tests with `pytest` (see `tests/`).

### Via Docker

Build and run tests in an isolated container environment:

```bash
docker build -t project-chimera .
docker run --rm project-chimera
```

The default container command is `make test`, as configured in the `Dockerfile`.

---

## Specs, Skills, and Research

- **Specs (`specs/`)**

  - `functional.md` – primary source for user-facing behavior and flows.
  - `technical.md` – architecture, data models, MCP integration points, and mapping back to the functional spec.
  - `openclaw_integration.md` – details for integrating with OpenClaw / Moltbook (resources, tools, sponsorship flows).
  - `_meta.md` – meta-spec and documentation structure.

- **Runtime skills (`skills/`)**

  - `skill.md` – contracts and boundaries for core runtime skills (trend fetcher, content generator, engagement analyzer).

- **Research (`research/`)**
  - `strategy_report.md` – overall strategy and qualitative design.
  - `architecture_strategy.md` – architecture and data stack decisions (Planner / Worker / Judge, storage, MCP).
  - `tooling_strategy.md` – development and tooling conventions for working on Chimera.

When changing behavior or architecture:

1. Update `specs/functional.md` first.
2. Reflect those changes in `specs/technical.md` (and `specs/openclaw_integration.md` where relevant).
3. Only then update implementation code and tests.
