"""Shared contracts between the Forge host and every plugin.

Nothing in this package may import from ``forge_host`` or ``forge_plugins``.
It is the ABI. If you change a type here, bump the minor version and note
it in ``CHANGELOG``.
"""

from forge_contracts.plugin import (
    Artifact,
    ConceptPlugin,
    GenerationRequest,
    GenerationResult,
    ParamField,
    ParamSchema,
    PluginError,
    PluginKind,
    PluginSpec,
)

__all__ = [
    "Artifact",
    "ConceptPlugin",
    "GenerationRequest",
    "GenerationResult",
    "ParamField",
    "ParamSchema",
    "PluginError",
    "PluginKind",
    "PluginSpec",
]

CONTRACTS_VERSION = "0.9.4"