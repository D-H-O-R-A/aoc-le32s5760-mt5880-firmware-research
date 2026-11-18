#!/usr/bin/env python3
"""
Verifies SHA-256 checksums recorded in firmware-forensics/FIRMWARE_HASH_MANIFEST.txt.

Modes:
  --ci               Verifies all tracked REPO files committed in Git (safe on CI runners).
  --workspace <dir>  Also verifies extracted workspace files and virtual PKG partition hashes.
"""

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_pkg_and_nfsb import parse_pkg_headers  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest_path: Path) -> List[Tuple[str, int, str, str]]:
    entries: List[Tuple[str, int, str, str]] = []
    for raw in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 3)
        if len(parts) != 4:
            raise ValueError(f"Malformed manifest line: {raw!r}")
        digest, size_s, scope, rel_path = parts
        entries.append((digest.lower(), int(size_s), scope, rel_path))
    return entries


def verify(repo: Path, workspace: Path, ci_only: bool) -> int:
    manifest_path = repo / "firmware-forensics" / "FIRMWARE_HASH_MANIFEST.txt"
    entries = parse_manifest(manifest_path)

    pkg_cache: Dict[str, bytes] = {}
    if not ci_only:
        pkg_path = workspace / "extracted" / "upgrade_loader.pkg"
        if pkg_path.is_file():
            pkg_data, p_entries = parse_pkg_headers(str(pkg_path))
            for tag, _hoff, poff, sz in p_entries:
                pkg_cache[f"extracted/upgrade_loader.pkg#part:{tag}"] = pkg_data[poff : poff + sz]

    checked = 0
    mismatches: List[str] = []
    missing: List[str] = []

    for exp_sha, exp_size, scope, rel_path in entries:
        if scope == "REPO":
            target = repo / rel_path
            if not target.is_file():
                missing.append(f"[REPO] {rel_path}")
                continue
            actual_size = target.stat().st_size
            actual_sha = sha256_file(target)
        else:
            if ci_only:
                continue
            if scope == "WORKSPACE_VIRTUAL":
                payload = pkg_cache.get(rel_path)
                if payload is None:
                    missing.append(f"[WORKSPACE_VIRTUAL] {rel_path}")
                    continue
                actual_size = len(payload)
                actual_sha = hashlib.sha256(payload).hexdigest()
            else:
                target = workspace / rel_path
                if not target.is_file():
                    missing.append(f"[WORKSPACE] {rel_path}")
                    continue
                actual_size = target.stat().st_size
                actual_sha = sha256_file(target)

        checked += 1
        if actual_size != exp_size or actual_sha != exp_sha:
            mismatches.append(
                f"{rel_path}: expected ({exp_size} B, {exp_sha}), got ({actual_size} B, {actual_sha})"
            )

    mode_str = "CI (REPO only)" if ci_only else "FULL (REPO + WORKSPACE)"
    print(f"Hash verification mode: {mode_str}")
    print(f"Verified entries: {checked}, Missing: {len(missing)}, Mismatches: {len(mismatches)}")
    if missing:
        print("Missing entries:")
        for m in missing[:20]:
            print(" ", m)
        return 1
    if mismatches:
        print("Hash/size mismatches:")
        for m in mismatches:
            print(" ", m)
        return 1
    print("[PASS] All checked manifest entries match SHA-256 and byte sizes.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify SHA-256 manifest entries.")
    default_repo = SCRIPT_DIR.parent
    parser.add_argument("--repo", default=str(default_repo), help="Repository root directory")
    parser.add_argument("--workspace", default=str(default_repo.parent), help="Local workspace root")
    parser.add_argument("--ci", action="store_true", help="Verify only committed repository files (CI safe)")
    args = parser.parse_args()
    raise SystemExit(verify(Path(args.repo).resolve(), Path(args.workspace).resolve(), args.ci))


if __name__ == "__main__":
    main()
