from __future__ import annotations

from collections.abc import Callable, Iterable
import json
from pathlib import Path

import pytest


@pytest.fixture
def require_local_raw_artifacts() -> Callable[..., None]:
    """Skip raw-backed tests when intentionally uncommitted source bytes are unavailable."""

    def require(
        project_root: Path,
        *,
        manifests: Iterable[Path],
        additional_paths: Iterable[Path] = (),
    ) -> None:
        required_paths = list(additional_paths)
        for manifest in manifests:
            artifacts = json.loads(manifest.read_text(encoding="utf-8"))
            for artifact in artifacts:
                path = Path(artifact["path"])
                required_paths.append(path if path.is_absolute() else project_root / path)

        missing = [path for path in required_paths if not path.is_file()]
        if missing:
            pytest.skip(
                "Licensed third-party raw artifacts are intentionally excluded from Git; "
                f"{len(missing)} required local file(s) are unavailable."
            )

    return require
