"""Wire up logging, config, registry, loader, and the main window."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from forge_host.core.config import ForgeConfig, load_config
from forge_host.core.registry import PluginRegistry
from forge_host.services.loader import PluginLoader
from forge_host.services.model_registry import ModelRegistry
from forge_host.ui.main_window import MainWindow

log = logging.getLogger("forge.host")


def build_config(argv: list[str]) -> ForgeConfig:
    cfg = load_config()
    if "--sandbox" in argv:
        cfg = cfg.model_copy(update={"sandbox_plugins": True})
    if "--no-gpu" in argv:
        cfg = cfg.model_copy(update={"prefer_gpu": False})
    return cfg


def run(argv: list[str]) -> int:
    logging.basicConfig(
        level=logging.DEBUG if "--verbose" in argv else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    cfg = build_config(argv)
    log.info("forge host booting; config=%s", cfg.model_dump(exclude={"paths"}))
    return asyncio.run(_main(cfg))


async def _main(cfg: ForgeConfig) -> int:
    registry = PluginRegistry()
    loader = PluginLoader(registry, sandbox=cfg.sandbox_plugins)
    models = ModelRegistry(cfg.paths.models)
    loaded = loader.discover_and_register()
    log.info("registered %d plugins", len(loaded))
    for spec in registry.specs():
        log.info("  plugin %s (%s) v%s", spec.id, spec.kind.value, spec.version)

    window = MainWindow(cfg, registry, models)
    return await window.run_async()


__all__ = ["run", "build_config", "_main"]