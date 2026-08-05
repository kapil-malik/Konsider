"""Audited source registration and capture primitives for destination-side TFC inputs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Callable, Mapping

from konsider.contracts import ContractError, validate_contract


class TfcSourceError(ValueError):
    """Raised when a TFC source registration or capture is invalid."""


@dataclass(frozen=True)
class CapturedTfcSource:
    source_id: str
    asset: str
    content: bytes
    checksum: str


class TfcSourceRegistry:
    """A small source-family-neutral registry; source metadata remains data, not parser code."""

    def __init__(self, source_manifest: Mapping[str, object]) -> None:
        try:
            validate_contract(
                source_manifest,
                "tfc-source-legal-manifest",
                context="TFC source registry",
                schema_generation=4,
            )
        except ContractError as exc:
            raise TfcSourceError(str(exc)) from exc
        sources = source_manifest["sources"]
        self._sources = {source["source_id"]: dict(source) for source in sources}  # type: ignore[index]
        if len(self._sources) != len(sources):  # type: ignore[arg-type]
            raise TfcSourceError("TFC source IDs must be unique.")

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._sources))

    def get(self, source_id: str) -> dict[str, object]:
        try:
            return dict(self._sources[source_id])
        except KeyError as exc:
            raise TfcSourceError(f"Unknown TFC source {source_id}.") from exc

    def capture_online(
        self,
        source_id: str,
        fetcher: Callable[[str], bytes],
    ) -> CapturedTfcSource:
        """Capture through an injected worker fetcher; API runtime never calls this method."""

        source = self.get(source_id)
        asset = str(source["asset"])
        content = fetcher(asset)
        checksum = f"sha256:{hashlib.sha256(content).hexdigest()}"
        if checksum != source["checksum"]:
            raise TfcSourceError(f"Checksum mismatch while capturing TFC source {source_id}.")
        return CapturedTfcSource(source_id, asset, content, checksum)


__all__ = ["CapturedTfcSource", "TfcSourceError", "TfcSourceRegistry"]
