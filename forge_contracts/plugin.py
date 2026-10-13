"""Core plugin ABI for ai-sneaker-concept-forge.

A plugin declares its kind, its parameter schema, and its generation
contract. The host never introspects plugin internals — it only reads
``PluginSpec`` and calls ``generate``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PluginKind(str, Enum):
    SILHOUETTE = "silhouette"
    PALETTE = "palette"
    MATERIAL = "material"
    VOICE = "voice"
    COMPOSER = "composer"


ParamType = Literal["int", "float", "str", "bool", "enum", "color", "path"]


class ParamField(BaseModel):
    name: str
    type: ParamType
    default: Any
    description: str = ""
    min: float | None = None
    max: float | None = None
    choices: list[str] | None = None

    @field_validator("choices")
    @classmethod
    def _choices_required_for_enum(cls, v: list[str] | None, info: Any) -> list[str] | None:
        if info.data.get("type") == "enum" and not v:
            raise ValueError("enum fields require non-empty choices")
        return v


class ParamSchema(BaseModel):
    fields: list[ParamField] = Field(default_factory=list)

    def names(self) -> set[str]:
        return {f.name for f in self.fields}


class PluginSpec(BaseModel):
    id: str
    kind: PluginKind
    display_name: str
    version: str
    author: str = "forge-crew"
    description: str = ""
    params: ParamSchema = Field(default_factory=ParamSchema)
    produces: list[str] = Field(default_factory=list)
    consumes: list[str] = Field(default_factory=list)
    gpu_recommended: bool = False
    model_ids: list[str] = Field(default_factory=list)


class Artifact(BaseModel):
    kind: Literal["image", "text", "mesh", "swatch", "board"]
    path: Path
    width: int | None = None
    height: int | None = None
    mime: str | None = None


class GenerationRequest(BaseModel):
    prompt: str
    palette: list[str] = Field(default_factory=list)
    silhouette_seed: int = 0
    seed: int = 0
    steps: int = 28
    cfg_scale: float = 6.5
    params: dict[str, Any] = Field(default_factory=dict)
    output_dir: Path
    upstream: dict[str, list[Artifact]] = Field(default_factory=dict)


class GenerationResult(BaseModel):
    artifacts: list[Artifact] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class PluginError(Exception):
    def __init__(self, code: str, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


class ConceptPlugin(ABC):
    """Every generator plugin implements this."""

    @abstractmethod
    def describe(self) -> PluginSpec: ...

    def warmup(self) -> None:
        return None

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def teardown(self) -> None:
        return None