# Contributing to ai-sneaker-concept-forge

Thanks for wanting to forge with us. This repo is a plugin-host desktop tool:
the **host** (`forge_host/`) owns the window, the registry, the loader, and the
job queue. Everything that actually *makes* a sneaker concept is a **plugin**
(`forge_plugins/`), and every plugin talks to the host through the shared
**contracts** package (`forge_contracts/`).

If you're adding a new generator (a new diffusion model, a new silhouette
prior, a new material sampler), you almost never touch the host. You add a
plugin.

## Dev setup

```bash
git clone https://github.com/forge-crew/ai-sneaker-concept-forge.git
cd ai-sneaker-concept-forge
python -m venv .venv
. .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -e ".[dev,cpu]"
pytest -q
ruff check .
mypy forge_host forge_contracts forge_plugins
```

Windows users: we ship a `scripts/dev_bootstrap.ps1` that does the same thing
with the right venv paths. CI runs on `windows-latest` and `ubuntu-latest`.

## Plugin anatomy

A plugin is a class that subclasses `ConceptPlugin` from `forge_contracts`
and registers itself via a `[project.entry-points."forge.plugins"]` entry in
`pyproject.toml`. The host discovers it at boot, calls `describe()` to learn
its capabilities, and only then wires it into the pipeline.

Rules for plugins:

1. **No UI imports.** Plugins never import PySide6. The host is the only
   thing that draws.
2. **Declare your inputs.** `describe()` must return a `PluginSpec` with a
   fully typed `ParamSchema`. The host auto-builds the param panel from it.
3. **Never block the event loop.** Long work goes into `asyncio.to_thread`
   or a worker pool. The host will kill plugins that stall >30s.
4. **Deterministic seeds.** Every generation call takes a `seed: int`. Same
   seed + same params = same output, byte-for-byte, modulo the model's own
   nondeterminism which you must document in the spec.
5. **No network at generation time.** Models are pulled at install time via
   `forge-cli model pull <id>`. Generation is offline.

## Naming

- Plugins: `snake_case` module, `PascalCase` class ending in `Plugin`.
- Concepts in docs: "sneaker concept", "silhouette", "last", "palette",
  "upper", "midsole", "outsole", "eyestay", "heel counter", "toe box".
- Don't call a plugin an "assistant" or a "helper". It's a plugin.

## Commit style

Conventional commits. `feat(palette_diffusion): add Q8 quant path`,
`fix(loader): handle missing entry point gracefully`, etc.

## PR checklist

- [ ] `pytest -q` green
- [ ] `ruff check .` clean
- [ ] `mypy` clean on touched packages
- [ ] New plugin has an entry in `docs/PLUGINS.md`
- [ ] New param has a `description` in its `ParamField`

## Code of conduct

Be a decent person. We're here to make weird sneakers with computers.