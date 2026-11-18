#!/usr/bin/env python3
"""
Deterministic comparative forensic diff tool for AOC LE32S5760/20 firmware:
  1. Compares mirrored A/B partitions inside stock upgrade_loader.pkg (`kerA` vs `kerB`,
     `rfsA` vs `rfsB`, `3rdA` vs `3rdB`).
  2. Compares stock `upgrade_loader.pkg` vs laboratory `custom_upgrade_loader.pkg`.
  3. Compares stock `extracted/rootfs1` vs `build/staging_rootfs` + `custom_payload`.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_pkg_and_nfsb import parse_pkg_headers  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def diff_byte_ranges(a: bytes, b: bytes, max_ranges: int = 16) -> List[Dict[str, Any]]:
    """Finds contiguous offset intervals where two equal-length byte strings differ."""
    limit = min(len(a), len(b))
    ranges: List[Dict[str, Any]] = []
    i = 0
    while i < limit:
        if a[i] != b[i]:
            start = i
            while i < limit and a[i] != b[i]:
                i += 1
            ranges.append({"start": start, "end": i, "length": i - start})
            if len(ranges) >= max_ranges:
                break
        i += 1
    return ranges


def compare_workspace(ws: Path, repo: Path, json_out: Path) -> Dict[str, Any]:
    pkg_p = ws / "extracted" / "upgrade_loader.pkg"
    custom_pkg_p = ws / "build" / "custom_upgrade_loader.pkg"
    stock_rfs = ws / "extracted" / "rootfs1"
    staging_rfs = ws / "build" / "staging_rootfs"

    result: Dict[str, Any] = {
        "ab_mirrors": [],
        "stock_vs_custom_pkg": [],
        "staging_rootfs_delta": {"added": [], "modified": []},
        "custom_payload_files": [],
    }

    if pkg_p.is_file():
        pkg_data, pkg_entries = parse_pkg_headers(str(pkg_p))
        by_tag = {t: (poff, sz) for t, _h, poff, sz in pkg_entries}
        for a_tag, b_tag in [("kerA", "kerB"), ("rfsA", "rfsB"), ("3rdA", "3rdB")]:
            if a_tag in by_tag and b_tag in by_tag:
                pa, sza = by_tag[a_tag]
                pb, szb = by_tag[b_tag]
                da = pkg_data[pa : pa + sza]
                db = pkg_data[pb : pb + szb]
                sa = sha256_bytes(da)
                sb = sha256_bytes(db)
                ranges = diff_byte_ranges(da, db) if da != db else []
                result["ab_mirrors"].append({
                    "pair": f"{a_tag} vs {b_tag}",
                    "size_a": sza,
                    "size_b": szb,
                    "sha256_a": sa,
                    "sha256_b": sb,
                    "bit_identical": da == db and sza == szb,
                    "diff_ranges_sample": ranges,
                })

        if custom_pkg_p.is_file():
            cp_data, cp_entries = parse_pkg_headers(str(custom_pkg_p))
            cp_by_tag = {t: (poff, sz) for t, _h, poff, sz in cp_entries}
            for tag, _h, poff, sz in pkg_entries:
                if tag not in cp_by_tag:
                    continue
                cpoff, csz = cp_by_tag[tag]
                d1 = pkg_data[poff : poff + sz]
                d2 = cp_data[cpoff : cpoff + csz]
                identical = (sz == csz and d1 == d2)
                result["stock_vs_custom_pkg"].append({
                    "partition": tag,
                    "stock_size": sz,
                    "custom_size": csz,
                    "bit_identical": identical,
                    "stock_nfsb_header_prefix": d1[:4].decode("ascii", "replace") if not identical else "",
                    "custom_header_prefix_hex": d2[:16].hex() if not identical else "",
                })

    if stock_rfs.is_dir() and staging_rfs.is_dir():
        for dp, _, fns in os.walk(staging_rfs):
            for fn in sorted(fns):
                sp = Path(dp) / fn
                if sp.is_symlink():
                    continue
                rel = str(sp.relative_to(staging_rfs))
                op = stock_rfs / rel
                if not op.exists():
                    result["staging_rootfs_delta"]["added"].append({
                        "path": rel,
                        "size_bytes": sp.stat().st_size,
                        "sha256": sha256_bytes(sp.read_bytes()),
                    })
                else:
                    b_new = sp.read_bytes()
                    b_old = op.read_bytes()
                    if b_new != b_old:
                        result["staging_rootfs_delta"]["modified"].append({
                            "path": rel,
                            "stock_size": len(b_old),
                            "modified_size": len(b_new),
                            "delta_bytes": len(b_new) - len(b_old),
                            "stock_sha256": sha256_bytes(b_old),
                            "modified_sha256": sha256_bytes(b_new),
                        })

    cp_dir = repo / "custom_payload"
    if cp_dir.is_dir():
        for dp, _, fns in os.walk(cp_dir):
            for fn in sorted(fns):
                fp = Path(dp) / fn
                result["custom_payload_files"].append({
                    "path": str(fp.relative_to(repo)),
                    "size_bytes": fp.stat().st_size,
                    "sha256": sha256_bytes(fp.read_bytes()),
                })

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare stock banks, custom PKG, and rootfs staging delta.")
    default_repo = SCRIPT_DIR.parent
    parser.add_argument("--repo", default=str(default_repo), help="Repository root directory")
    parser.add_argument("--workspace", default=str(default_repo.parent), help="Workspace root directory")
    parser.add_argument(
        "--out",
        default=str(default_repo / "comparative-analysis" / "comparison_metrics.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()
    res = compare_workspace(Path(args.workspace).resolve(), Path(args.repo).resolve(), Path(args.out).resolve())
    print("=== A/B Mirror Partition Parity ===")
    for item in res["ab_mirrors"]:
        print(f"  {item['pair']}: identical={item['bit_identical']} (sizeA={item['size_a']}, sizeB={item['size_b']})")
    print("=== Stock vs Custom PKG Delta ===")
    for item in res["stock_vs_custom_pkg"]:
        if not item["bit_identical"]:
            print(f"  CHANGED {item['partition']}: stock={item['stock_size']} B -> custom={item['custom_size']} B (hdr={item['custom_header_prefix_hex'][:16]}...)")
    print(
        f"=== Staging Rootfs Delta: {len(res['staging_rootfs_delta']['added'])} added, "
        f"{len(res['staging_rootfs_delta']['modified'])} modified ==="
    )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
