from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_preflight_covers_backend_frontend_and_clean_checkout() -> None:
    verifier = (ROOT / "scripts" / "verify_ci.py").read_text(encoding="utf-8")
    for required in (
        '"pytest"',
        '"ruff"',
        '"black"',
        '"compileall"',
        '"--basetemp=.ci-tmp/pytest"',
        '"install", "--frozen-lockfile"',
        '"scripts/export_openapi.py"',
        '"run", "typecheck"',
        '"run", "lint"',
        '"run", "test", "--run"',
        '"run", "build"',
        '"run", "e2e"',
        'ci_environment["CI"] = "true"',
        '"worktree", "add"',
        'os.environ.get("KONSIDER_GIT")',
        'ROOT / ".ci-worktrees"',
        '"worktree", "prune"',
    ):
        assert required in verifier

    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
    assert "scripts/verify_ci.py --clean-revision HEAD" in hook


def test_readme_requires_preflight_before_every_push() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "before every push, including minor edits" in readme
    assert "python scripts/verify_ci.py --clean-revision HEAD" in readme
    assert "git config core.hooksPath .githooks" in readme
