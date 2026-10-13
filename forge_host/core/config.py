"""Forge configuration: paths, defaults, and env overrides.

Config resolution order (later wins):
  1. built-in defaults
  2. ``~/.config/forge/config.yaml``
  3. ``./forge.yaml`` in the working directory
  4. environment variables prefixed ``FORGE_``
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel, Field


class ForgePaths(BaseModel):
    root: Path
    models: Path
    cache: Path
    output: Path
    plugins: Path
    renders: Path


class ForgeConfig(BaseModel):
    paths: ForgePaths
    prefer_gpu: bool = True
    sandbox_plugins: bool = False
    max_concurrent_jobs: int = Field(default=2, ge=1, le=8)
    default_steps: int = Field(default=28, ge=4, le=120)
    default_cfg: float = Field(default=6.5, ge=1.0, le=20.0)
    log_level: str = "INFO"


def _default_paths() -> ForgePaths:
    root = Path(user_data_dir("forge", "forge-crew"))
    return ForgePaths(
        root=root,
        models=root / "models",
        cache=root / "cache",
        output=Path.cwd() / "generated_concepts",
        plugins=root / "plugins",
        renders=Path.cwd() / "renders",
    )


def _apply_env(cfg: ForgeConfig) -> ForgeConfig:
    updates: dict[str, object] = {}
    if (v := os.environ.get("FORGE_NO_GPU")):
        updates["prefer_gpu"] = v.lower() not in {"1", "true", "yes"}
    if (v := os.environ.get("FORGE_SANDBOX")):
        updates["sandbox_plugins"] = v.lower() in {"1", "true", "yes"}
    if (v := os.environ.get("FORGE_LOG_LEVEL")):
        updates["log_level"] = v.upper()
    return cfg.model_copy(update=updates) if updates else cfg


def load_config() -> ForgeConfig:
    cfg = ForgeConfig(paths=_default_paths())
    candidates = [
        Path(user_config_dir("forge", "forge-crew")) / "config.yaml",
        Path.cwd() / "forge.yaml",
    ]
    for path in candidates:
        if path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            cfg = cfg.model_copy(update=data)
    cfg = _apply_env(cfg)
    cfg.paths.root.mkdir(parents=True, exist_ok=True)
    cfg.paths.models.mkdir(parents=True, exist_ok=True)
    cfg.paths.cache.mkdir(parents=True, exist_ok=True)
    cfg.paths.output.mkdir(parents=True, exist_ok=True)
    return cfg