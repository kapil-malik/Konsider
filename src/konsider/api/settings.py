"""Deployment-neutral local API configuration."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _configured_path(value: str | None, default: Path) -> Path:
    return Path(value).expanduser().resolve() if value else default.resolve()


@dataclass(frozen=True)
class ApiSettings:
    release_root: Path
    active_release_path: Path
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> ApiSettings:
        values = os.environ if environ is None else environ
        release_root = _configured_path(
            values.get("KONSIDER_RELEASE_ROOT"), PROJECT_ROOT / "data" / "releases"
        )
        origins = tuple(
            origin.strip()
            for origin in values.get("KONSIDER_CORS_ORIGINS", "").split(",")
            if origin.strip()
        )
        return cls(
            release_root=release_root,
            active_release_path=_configured_path(
                values.get("KONSIDER_ACTIVE_RELEASE_PATH"), release_root / "active.json"
            ),
            environment=values.get("KONSIDER_ENVIRONMENT", "development"),
            log_level=values.get("KONSIDER_LOG_LEVEL", "INFO").upper(),
            cors_origins=origins,
        )
