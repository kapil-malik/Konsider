"""Run the same backend and frontend gates required before a GitHub push."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
GENERATED_API_FILES = (
    Path("contracts/openapi/konsider-api-3.0.json"),
    Path("web/src/api/openapi.json"),
    Path("web/src/api/schema.d.ts"),
)


class VerificationError(RuntimeError):
    """Raised when local CI parity cannot be established."""


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    check: bool = True,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    printable = subprocess.list2cmdline(list(command))
    print(f"\n==> [{cwd}] {printable}", flush=True)
    return subprocess.run(command, cwd=cwd, check=check, env=env, text=True)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pnpm() -> str:
    configured = os.environ.get("KONSIDER_PNPM")
    command = configured or shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if command is None:
        raise VerificationError(
            "pnpm is unavailable. Install pnpm 11.9.0 or set KONSIDER_PNPM to its executable."
        )
    return command


def _git() -> str:
    configured = os.environ.get("KONSIDER_GIT")
    command = configured or shutil.which("git")
    if command is None:
        raise VerificationError(
            "git is unavailable. Add git to PATH or set KONSIDER_GIT to its executable."
        )
    return command


def verify_backend(root: Path) -> None:
    """Run the complete backend job locally."""

    (root / ".ci-tmp").mkdir(exist_ok=True)
    _run(
        (
            sys.executable,
            "-m",
            "pytest",
            "--basetemp=.ci-tmp/pytest",
            "-p",
            "no:cacheprovider",
        ),
        cwd=root,
    )
    _run((sys.executable, "-m", "ruff", "check", "."), cwd=root)
    _run((sys.executable, "-m", "black", "--check", "."), cwd=root)
    _run((sys.executable, "-m", "compileall", "-q", "src", "tests"), cwd=root)


def verify_frontend(root: Path) -> None:
    """Run generated-contract, static, component, build, and browser gates."""

    pnpm = _pnpm()
    web = root / "web"
    before = {relative: _digest(root / relative) for relative in GENERATED_API_FILES}
    _run((pnpm, "install", "--frozen-lockfile"), cwd=web)
    _run((sys.executable, "scripts/export_openapi.py"), cwd=web)
    after = {relative: _digest(root / relative) for relative in GENERATED_API_FILES}
    changed = [
        relative.as_posix()
        for relative in GENERATED_API_FILES
        if before[relative] != after[relative]
    ]
    if changed:
        raise VerificationError(
            "Generated API artifacts were stale before verification: " + ", ".join(changed)
        )
    _run((pnpm, "run", "typecheck"), cwd=web)
    _run((pnpm, "run", "lint"), cwd=web)
    _run((pnpm, "run", "test", "--run"), cwd=web)
    _run((pnpm, "run", "build"), cwd=web)
    ci_environment = os.environ.copy()
    ci_environment["CI"] = "true"
    _run((pnpm, "run", "e2e"), cwd=web, env=ci_environment)


def verify(root: Path, *, backend: bool, frontend: bool) -> None:
    if backend:
        verify_backend(root)
    if frontend:
        verify_frontend(root)


def verify_clean_revision(revision: str, *, backend: bool, frontend: bool) -> None:
    """Verify committed bytes in a clean checkout without ignored local source files."""

    worktrees = ROOT / ".ci-worktrees"
    worktrees.mkdir(exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="prepush-", dir=worktrees))
    checkout = temporary / "checkout"
    git = _git()
    added = False
    try:
        _run((git, "worktree", "add", "--detach", str(checkout), revision), cwd=ROOT)
        added = True
        verify(checkout, backend=backend, frontend=frontend)
    finally:
        if added:
            cleanup = _run(
                (git, "worktree", "remove", "--force", str(checkout)),
                cwd=ROOT,
                check=False,
            )
            if cleanup.returncode:
                # Windows can briefly retain handles to Playwright/node_modules files even after
                # every verification command succeeds. Clean what is available and prune the
                # already-detached registration without turning a cache-cleanup race into a
                # false failed preflight.
                shutil.rmtree(checkout, ignore_errors=True)
                _run((git, "worktree", "prune"), cwd=ROOT, check=False)
                if checkout.exists():
                    print(
                        f"WARNING: deferred removal of ignored CI worktree residue: {checkout}",
                        file=sys.stderr,
                    )
        shutil.rmtree(temporary, ignore_errors=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--backend", action="store_true", help="Run only backend CI gates.")
    selection.add_argument("--frontend", action="store_true", help="Run only frontend CI gates.")
    parser.add_argument(
        "--clean-revision",
        metavar="REVISION",
        help="Verify a committed revision in a temporary clean git worktree.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    backend = not args.frontend
    frontend = not args.backend
    try:
        if args.clean_revision:
            verify_clean_revision(args.clean_revision, backend=backend, frontend=frontend)
        else:
            verify(ROOT, backend=backend, frontend=frontend)
    except (subprocess.CalledProcessError, VerificationError) as exc:
        print(f"\nCI preflight FAILED: {exc}", file=sys.stderr)
        return 1
    print("\nCI preflight PASSED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
