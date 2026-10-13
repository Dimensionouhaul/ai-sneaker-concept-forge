"""Concept generation pipeline — chains plugins by kind.

Order: silhouette -> palette -> material -> voice -> composer.
Any stage may be swapped for a different plugin of the same kind.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from forge_contracts import Artifact, GenerationRequest, GenerationResult, PluginKind
from forge_host.core.registry import PluginRegistry

log = logging.getLogger("forge.pipeline")

STAGE_ORDER: tuple[PluginKind, ...] = (
    PluginKind.SILHOUETTE,
    PluginKind.PALETTE,
    PluginKind.MATERIAL,
    PluginKind.VOICE,
)


@dataclass(slots=True)
class StageReport:
    kind: PluginKind
    plugin_id: str
    seconds: float
    artifact_count: int


class ConceptPipeline:
    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    async def run(self, request: GenerationRequest) -> tuple[GenerationResult, list[StageReport]]:
        reports: list[StageReport] = []
        upstream: dict[str, list[Artifact]] = {}
        notes: list[str] = []

        for kind in STAGE_ORDER:
            plugin = self._registry.first_of_kind(kind)
            plugin.warmup()
            stage_req = request.model_copy(update={"upstream": dict(upstream)})
            t0 = time.perf_counter()
            result = await plugin.generate(stage_req)
            dt = time.perf_counter() - t0
            upstream[kind.value] = result.artifacts
            notes.extend(result.notes)
            reports.append(StageReport(kind, plugin.describe().id, dt, len(result.artifacts)))
            log.info(
                "stage %s via %s -> %d artifacts in %.2fs",
                kind.value,
                plugin.describe().id,
                len(result.artifacts),
                dt,
            )

        composer = self._registry.first_of_kind(PluginKind.COMPOSER)
        composer.warmup()
        final_req = request.model_copy(update={"upstream": upstream})
        t0 = time.perf_counter()
        final = await composer.generate(final_req)
        reports.append(
            StageReport(PluginKind.COMPOSER, composer.describe().id, time.perf_counter() - t0, len(final.artifacts))
        )
        final.notes = [*notes, *final.notes]
        return final, reports