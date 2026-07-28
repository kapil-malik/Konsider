from pathlib import Path

from konsider.api.settings import PROJECT_ROOT, ApiSettings


def test_default_settings_are_absolute_and_project_relative() -> None:
    settings = ApiSettings.from_env({})

    assert settings.release_root == (PROJECT_ROOT / "data" / "releases").resolve()
    assert settings.active_release_path == (settings.release_root / "active.json").resolve()
    assert settings.catalog_path is None
    assert settings.release_root.is_absolute()


def test_environment_settings_support_distinct_paths_and_cors(tmp_path: Path) -> None:
    settings = ApiSettings.from_env(
        {
            "KONSIDER_RELEASE_ROOT": str(tmp_path / "releases"),
            "KONSIDER_ACTIVE_RELEASE_PATH": str(tmp_path / "pointer.json"),
            "KONSIDER_CATALOG_PATH": str(tmp_path / "catalog.json"),
            "KONSIDER_ENVIRONMENT": "test",
            "KONSIDER_LOG_LEVEL": "debug",
            "KONSIDER_CORS_ORIGINS": "http://localhost:5173, https://example.test",
        }
    )

    assert settings.release_root == (tmp_path / "releases").resolve()
    assert settings.active_release_path == (tmp_path / "pointer.json").resolve()
    assert settings.catalog_path == (tmp_path / "catalog.json").resolve()
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.cors_origins == ("http://localhost:5173", "https://example.test")
