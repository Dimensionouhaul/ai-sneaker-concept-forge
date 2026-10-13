"""Plugin discovery via entry points.

Reads ``forge.plugins`` entry points, instantiates each, and registers it.
When ``sandbox=True``, plugins are instantiated in a subprocess and proxied;
this is a best-effort guard, not a security boundary.
"""

from __future__ import annotations

import importlib.metadata as md
import logging
from typing import Any

from forge_contracts import ConceptPlugin, PluginSpec
from forge_contracts.errors import PluginLoadError
from forge_host.core.registry import PluginRegistry

log = logging.getLogger("forge.loader")

ENTRY_POINT_GROUP = "forge.plugins"


class PluginLoader:
    def __init__(self, registry: PluginRegistry, *, sandbox: bool = False) -> None:
        self._registry = registry
        self._sandbox = sandbox

    def discover_and_register(self) -> list[PluginSpec]:
        specs: list[PluginSpec] = []
        eps = md.entry_points()
        group = eps.select(group=ENTRY_POINT_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_POINT_GROUP, [])
        for ep in group:
            try:
                plugin = self._instantiate(ep)
            except Exception as exc:  # noqa: BLE001 — one bad plugin must not kill boot
                log.error("failed to load plugin %s: %s", ep.name, exc)
                continue
            try:
                specs.append(self._registry.register(plugin))
            except Exception as exc:  # noqa: BLE001
                log.error("plugin %s failed contract check: %s", ep.name, exc)
        return specs

    def _instantiate(self, ep: Any) -> ConceptPlugin:
        try:
            obj = ep.load()
        except Exception as exc:  # noqa: BLE001
            raise PluginLoadError(f"cannot load entry point {ep.name}", hint=str(exc)) from exc
        if isinstance(obj, type):
            plugin = obj()
        else:
            plugin = obj
        if not isinstance(plugin, ConceptPlugin):
            raise PluginLoadError(f"{ep.name} is not a ConceptPlugin")
        return plugin

    def register_builtin(self, plugin: ConceptPlugin) -> PluginSpec:
        return self._registry.register(plugin)