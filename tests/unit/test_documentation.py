import json
import re
from pathlib import Path

from konsider.api.app import create_app
from konsider.application import RecommendationService

ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_ROOTS = [
    ROOT / "README.md",
    ROOT / ".ai",
    ROOT / "apps",
    ROOT / "contracts",
    ROOT / "docs",
    ROOT / "web",
]
IGNORED_DIRECTORIES = {"node_modules", "dist", "coverage", "playwright-report", "test-results"}


def _markdown_files() -> list[Path]:
    files = []
    for root in MARKDOWN_ROOTS:
        candidates = [root] if root.is_file() else root.rglob("*.md")
        files.extend(path for path in candidates if IGNORED_DIRECTORIES.isdisjoint(path.parts))
    return sorted(files)


def test_relative_markdown_links_resolve() -> None:
    pattern = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
    broken = []
    for path in _markdown_files():
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative_path = target.split("#", 1)[0]
            if relative_path and not (path.parent / relative_path).resolve().exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not broken, "Broken Markdown links:\n" + "\n".join(broken)


def test_json_documentation_examples_are_valid() -> None:
    fenced_json = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
    failures = []
    for path in _markdown_files():
        for index, example in enumerate(fenced_json.findall(path.read_text(encoding="utf-8")), 1):
            try:
                json.loads(example)
            except json.JSONDecodeError as exc:
                failures.append(f"{path.relative_to(ROOT)} block {index}: {exc}")
    assert not failures, "Invalid JSON examples:\n" + "\n".join(failures)


def test_documented_api_paths_match_openapi() -> None:
    api_document = (ROOT / "docs" / "operations" / "api.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"`(/api/v1/[^`]+)`", api_document))
    openapi = create_app(service=RecommendationService()).openapi()
    assert documented == set(openapi["paths"])


def test_current_documents_name_the_active_release() -> None:
    active = json.loads((ROOT / "data" / "releases" / "active.json").read_text(encoding="utf-8"))
    for relative_path in [
        "README.md",
        "docs/README.md",
        "docs/architecture/system-architecture.md",
        "docs/history/releases/README.md",
        "docs/operations/api.md",
        "docs/operations/worker.md",
        "docs/product/roadmap.md",
    ]:
        assert active["release_id"] in (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_5_closure_and_forward_roadmap_are_linked() -> None:
    closure = ROOT / "docs" / "research" / "phase5-closure-report.md"
    roadmap = (ROOT / "docs" / "product" / "roadmap.md").read_text(encoding="utf-8")
    index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert closure.exists()
    assert "Phase 5: criteria expansion and source feasibility — complete" in roadmap
    assert "Phase 6: deterministic evidence and explanations — recommended next" in roadmap
    assert "Phase 7: conversational exploration" in roadmap
    assert "Phase 2E:" not in roadmap
    assert "Phase 2F:" not in roadmap
    assert "research/phase5-closure-report.md" in index
