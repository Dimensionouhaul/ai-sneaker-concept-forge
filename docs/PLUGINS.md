# Plugin contract reference

Every plugin subclasses `ConceptPlugin` and returns a `PluginSpec` from
`describe()`. The host reads the spec, builds the param panel, and calls
`generate()` with a `GenerationRequest`.

## Lifecycle

1. `__init__()` — cheap. No model loading. No network.
2. `describe() -> PluginSpec` — pure. Called once at registration.
3. `warmup()` — optional. Load weights into memory. Called on first use.
4. `generate(request) -> GenerationResult` — the work.
5. `teardown()` — optional. Release VRAM.

## Param schema

`ParamField` supports: `int`, `float`, `str`, `bool`, `enum`, `color`,
`path`. Each field has `name`, `type`, `default`, `description`, and
optional `min`/`max`/`choices`. The host renders these in the plugin's
panel without any UI code from the plugin.

## Result contract

`GenerationResult` carries:

- `artifacts: list[Artifact]` — image buffers, mesh files, text blocks
- `metrics: dict[str, float]` — timing, steps, seed echo
- `notes: list[str]` — human-readable notes merged into the concept board

## Failure

Raise `PluginError` with a `code` and a `hint`. The host shows the hint in
the status bar and marks the node red. Do not print. Do not sys.exit.