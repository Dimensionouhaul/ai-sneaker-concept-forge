"""In-memory plugin registry.

Holds ``PluginSpec`` -> instance. The loader writes; the UI reads; the
pipeline resolves by kind. Registration is idempotent by ``spec.id``.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from forge_contracts import ConceptPlugin, PluginKind, PluginSpec
from forge_contracts.errors import PluginContractError

log = logging.getLogger("forge.registry")


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, ConceptPlugin] = {}
        self._specs: dict[str, PluginSpec] = {}

    def register(self, plugin: ConceptPlugin) -> PluginSpec:
        spec = plugin.describe()
        if not spec.id or "." in spec.id:
            raise PluginContractError(
                f"invalid plugin id {spec.id!r}",
                hint="use a dotted-free id like 'palette_diffusion'",
            )
        if spec.id in self._plugins:
            log.warning("plugin %s already registered; replacing", spec.id)
        self._plugins[spec.id] = plugin
        self._specs[spec.id] = spec
        return spec

    def get(self, plugin_id: str) -> ConceptPlugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise PluginContractError(
                f"plugin {plugin_id!r} not registered",
                hint="run `forge-cli plugin list` to see what's available",
            ) from exc

    def spec(self, plugin_id: str) -> PluginSpec:
        return self._specs[plugin_id]

    def specs(self) -> list[PluginSpec]:
        return sorted(self._specs.values(), key=lambda s: s.id)

    def by_kind(self, kind: PluginKind) -> list[PluginSpec]:
        return [s for s in self.specs() if s.kind == kind]

    def first_of_kind(self, kind: PluginKind) -> ConceptPlugin:
        specs = self.by_kind(kind)
        if not specs:
            raise PluginContractError(
                f"no plugin of kind {kind.value!r} registered",
                hint=f"install a {kind.value} plugin",
            )
        return self._plugins[specs[0].id]

    def __contains__(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins

    def __len__(self) -> int:
        return len(self._plugins)

    def ids(self) -> Iterable[str]:
        return self._specs.keys()