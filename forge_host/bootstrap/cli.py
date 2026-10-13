"""``forge-cli`` — headless commands for CI, model pulls, and plugin listing."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from forge_host.core.config import load_config
from forge_host.core.registry import PluginRegistry
from forge_host.services.loader import PluginLoader
from forge_host.services.model_registry import ModelRegistry

app = typer.Typer(help="Headless Forge commands.", no_args_is_help=True)
model_app = typer.Typer(help="Model management.")
plugin_app = typer.Typer(help="Plugin management.")
app.add_typer(model_app, name="model")
app.add_typer(plugin_app, name="plugin")


@app.command("config")
def show_config() -> None:
    cfg = load_config()
    typer.echo(json.dumps(json.loads(cfg.model_dump_json()), indent=2))


@plugin_app.command("list")
def list_plugins() -> None:
    reg = PluginRegistry()
    loader = PluginLoader(reg)
    loaded = loader.discover_and_register()
    for spec in loaded:
        typer.echo(f"{spec.id:24} {spec.kind.value:10} v{spec.version}  {spec.display_name}")


@model_app.command("pull")
def pull_model(model_id: str, dest: Path | None = None) -> None:
    cfg = load_config()
    target = dest or cfg.paths.models
    reg = ModelRegistry(target)
    path = reg.pull(model_id)
    typer.echo(f"pulled {model_id} -> {path}")


if __name__ == "__main__":
    app()