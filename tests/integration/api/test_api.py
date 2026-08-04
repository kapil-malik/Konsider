import json
from pathlib import Path

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.settings import ApiSettings

ROOT = Path(__file__).resolve().parents[3]


def test_default_paths_load_the_schema_current_release_from_any_working_directory(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    with TestClient(create_app()) as client:
        response = client.get("/api/v2/health")

    assert response.status_code == 200
    assert response.json()["release_id"] == "2026-08-04.1"


def test_missing_release_returns_safe_503(tmp_path) -> None:
    missing = tmp_path / "private" / "releases"
    settings = ApiSettings(
        release_root=missing,
        active_release_path=missing / "active.json",
    )
    with TestClient(create_app(settings=settings)) as client:
        health = client.get("/api/v2/health")
        catalog = client.get("/api/v2/catalog")

    assert health.status_code == catalog.status_code == 503
    assert health.json()["error"]["code"] == "release_unavailable"
    assert str(tmp_path) not in health.text
    assert str(tmp_path) not in catalog.text


def test_legacy_active_pointer_is_rejected_by_the_public_runtime(tmp_path) -> None:
    release_root = tmp_path / "releases"
    release_root.mkdir()
    pointer = release_root / "active.json"
    pointer.write_text(
        json.dumps(
            {
                "release_id": "2026-07-28.2",
                "schema_version": "konsider-release-4.0",
            }
        ),
        encoding="utf-8",
    )
    settings = ApiSettings(
        release_root=release_root,
        active_release_path=pointer,
    )
    with TestClient(create_app(settings=settings)) as client:
        response = client.get("/api/v2/health")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "release_unavailable"


def test_unexpected_service_failure_returns_safe_500() -> None:
    class BrokenService:
        def catalog(self):
            raise RuntimeError("private failure detail")

    with TestClient(
        create_app(service=BrokenService()),  # type: ignore[arg-type]
        raise_server_exceptions=False,
    ) as client:
        response = client.get("/api/v2/catalog")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "private failure detail" not in response.text


def test_openapi_has_only_the_final_structured_public_surface() -> None:
    schema = create_app().openapi()
    assert set(schema["paths"]) == {
        "/api/v2/health",
        "/api/v2/catalog",
        "/api/v2/rankings",
        "/api/v2/comparisons",
        "/api/v2/countries/{country_code}/details",
        "/api/v2/opportunity-filters",
    }
    serialized = json.dumps(schema)
    for removed in (
        "/api/v1/",
        '"profiles"',
        '"profile_id"',
        '"resolved_profile_id"',
        '"uncertainty_status"',
        '"locality_status"',
    ):
        assert removed not in serialized
