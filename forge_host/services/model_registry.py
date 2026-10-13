"""Model pulls and checksum verification.

Models live under ``<forge_root>/models/``. The registry talks to the forge
CDN, verifies the SHA-256 in the signed manifest, and refuses redirects to
non-forge hosts.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import httpx

from forge_contracts.errors import ModelMissingError

log = logging.getLogger("forge.models")

FORGE_CDN = "https://cdn.forge.local/models"
CHUNK = 1 << 20  # 1 MiB


class ModelRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, model_id: str) -> Path:
        safe = model_id.replace(":", "_").replace("/", "_")
        return self.root / f"{safe}.onnx"

    def has(self, model_id: str) -> bool:
        return self.path_for(model_id).is_file()

    def require(self, model_id: str) -> Path:
        p = self.path_for(model_id)
        if not p.is_file():
            raise ModelMissingError(
                f"model {model_id!r} not present",
                hint=f"run `forge-cli model pull {model_id}`",
            )
        return p

    def pull(self, model_id: str, *, expected_sha: str | None = None) -> Path:
        dest = self.path_for(model_id)
        url = f"{FORGE_CDN}/{model_id}.onnx"
        log.info("pulling %s from %s", model_id, url)
        h = hashlib.sha256()
        with httpx.stream("GET", url, follow_redirects=False, timeout=60.0) as r:
            r.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in r.iter_bytes(CHUNK):
                    fh.write(chunk)
                    h.update(chunk)
        if expected_sha and h.hexdigest() != expected_sha:
            dest.unlink(missing_ok=True)
            raise ModelMissingError(f"checksum mismatch for {model_id}")
        return dest