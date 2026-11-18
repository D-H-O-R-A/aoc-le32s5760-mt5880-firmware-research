#!/usr/bin/env python3
"""
Generates deterministic cryptographic and structural inventories from an extracted
AOC LE32S5760 (MT5880 / TPV MTK2K14PLF) workspace alongside tracked repository artifacts.

Outputs created/refreshed under --repo:
  - firmware-forensics/FIRMWARE_HASH_MANIFEST.txt
  - firmware-forensics/FIRMWARE_BINARY_INVENTORY.csv
  - kernel-analysis/KERNEL_MODULE_INVENTORY.csv
  - filesystem/FILESYSTEM_INVENTORY.csv
"""

import argparse
import csv
import hashlib
import os
import re
import stat
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_pkg_and_nfsb import parse_pkg_headers  # noqa: E402


ELF_MACHINES = {
    0x03: "x86",
    0x08: "MIPS",
    0x28: "ARM (32-bit)",
    0x3E: "x86-64",
    0xB7: "AArch64",
}

ELF_TYPES = {
    1: "ET_REL (Relocatable)",
    2: "ET_EXEC (Executable)",
    3: "ET_DYN (Shared Object / PIE)",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def inspect_elf_header(data_prefix: bytes) -> Tuple[str, str, str]:
    """Parses the 52-byte ELF header prefix cleanly using stdlib."""
    if len(data_prefix) < 20 or data_prefix[:4] != b"\x7fELF":
        if data_prefix[:4] == b"NFSB":
            return ("N/A", "N/A", "NFSB Verity Container")
        if data_prefix[:4] == b"\x27\x05\x19\x56":
            return ("ARM (32-bit)", "32-bit", "U-Boot uImage")
        if data_prefix[:4] == b"hsqs":
            return ("N/A", "N/A", "SquashFS (little-endian)")
        if data_prefix[:4] == b"UBI#":
            return ("N/A", "N/A", "UBI Erase Counter Header")
        return ("N/A", "N/A", "Raw / Data Binary")
    ei_class = data_prefix[4]
    bits = "32-bit" if ei_class == 1 else ("64-bit" if ei_class == 2 else "unknown")
    endian = "<" if data_prefix[5] == 1 else ">"
    e_type = int.from_bytes(data_prefix[16:18], "little" if endian == "<" else "big")
    e_machine = int.from_bytes(data_prefix[18:20], "little" if endian == "<" else "big")
    mach_name = ELF_MACHINES.get(e_machine, f"0x{e_machine:x}")
    type_name = ELF_TYPES.get(e_type, f"ET_{e_type}")
    return (mach_name, bits, type_name)


def parse_modinfo(ko_path: Path) -> Dict[str, str]:
    data = ko_path.read_bytes()
    out: Dict[str, str] = {}
    for key in ("vermagic", "license", "description", "author", "srcversion", "depends"):
        pat = re.compile(key.encode("ascii") + rb"=([^\x00]+)")
        matches = [m.decode("utf-8", errors="replace").strip() for m in pat.findall(data)]
        out[key] = "; ".join(dict.fromkeys(matches)) if matches else ""
    return out


def collect_repo_tracked_files(repo: Path) -> List[Path]:
    """Lists stable deterministic source/script/payload files tracked in repo."""
    targets: List[Path] = []
    for sub in ("scripts", "custom_payload", "evidence", "docs"):
        p = repo / sub
        if not p.is_dir():
            continue
        for dp, _, fns in os.walk(p):
            if "__pycache__" in dp:
                continue
            for fn in fns:
                fp = Path(dp) / fn
                if fp.suffix in (".pyc", ".pyo"):
                    continue
                targets.append(fp)
    for top in ("LICENSE", ".gitignore"):
        tp = repo / top
        if tp.is_file():
            targets.append(tp)
    return sorted(targets, key=lambda p: str(p.relative_to(repo)))


def build_inventories(ws: Path, repo: Path) -> None:
    (repo / "firmware-forensics").mkdir(parents=True, exist_ok=True)
    (repo / "kernel-analysis").mkdir(parents=True, exist_ok=True)
    (repo / "filesystem").mkdir(parents=True, exist_ok=True)

    manifest_lines: List[str] = [
        "# FIRMWARE_HASH_MANIFEST.txt",
        "# Deterministic SHA-256 verification manifest for AOC LE32S5760/20 (MT5880 / TPV MTK2K14PLF)",
        "# Format: <sha256>  <size_bytes>  <scope>  <relative_path>",
        "# SECTION A entries reside in the local research workspace and are excluded from Git by .gitignore.",
        "# SECTION B entries are tracked directly in the Git repository and validated automatically in CI.",
        "",
        "# === SECTION A: EXTERNAL WORKSPACE ARTIFACTS (EXCLUDED FROM GIT) ===",
    ]

    bin_rows: List[List[str]] = []

    def add_binary(scope: str, path: Path, rel_label: str, category: str, evidence_src: str) -> None:
        if not path.is_file():
            return
        digest = sha256_file(path)
        size = path.stat().st_size
        with path.open("rb") as f:
            head = f.read(64)
        mach, bits, kind = inspect_elf_header(head)
        manifest_lines.append(f"{digest}  {size}  {scope}  {rel_label}")
        bin_rows.append([category, rel_label, str(size), digest, mach, bits, kind, "CONFIRMED", evidence_src])

    # 1. Outer factory ZIP & PKG
    zip_p = ws / "original_firmware" / "LE32S5760_V2.011_V0.2.zip"
    pkg_p = ws / "extracted" / "upgrade_loader.pkg"
    add_binary("WORKSPACE", zip_p, "original_firmware/LE32S5760_V2.011_V0.2.zip", "factory_archive", "ZIP Archive")
    add_binary("WORKSPACE", pkg_p, "extracted/upgrade_loader.pkg", "factory_pkg", "Unpacked OEM PKG")

    # 2. All 16 PKG partitions directly hashed in memory from upgrade_loader.pkg
    if pkg_p.is_file():
        pkg_data, entries = parse_pkg_headers(str(pkg_p))
        for tag, hoff, poff, sz in entries:
            payload = pkg_data[poff : poff + sz]
            digest = sha256_bytes(payload)
            mach, bits, kind = inspect_elf_header(payload[:64])
            rel_label = f"extracted/upgrade_loader.pkg#part:{tag}"
            manifest_lines.append(f"{digest}  {sz}  WORKSPACE_VIRTUAL  {rel_label}")
            bin_rows.append(["pkg_partition", rel_label, str(sz), digest, mach, bits, kind, "CONFIRMED", f"PKG offset 0x{poff:x}"])

    # 3. Core low-level extracted images
    for cat, rel, src in [
        ("bootloader", "extracted/uboot.bin", "PKG load partition"),
        ("bootloader_env", "extracted/uenv", "PKG uenv ARM ELF object"),
        ("kernel", "scratch/vmlinux.bin", "LZHS decompressed kerA/kerB"),
        ("service_binary", "extracted/appfs1/basic/dtv_svc", "appfs1 main TV daemon"),
        ("system_binary", "extracted/appfs1/bin/busybox", "appfs1 BusyBox v1.15.3"),
        ("ui_shell", "extracted/rootfs1/bin/SystemManager", "rootfs1 Qt UI manager"),
        ("browser_engine", "extracted/rootfs1/nettv/opera/opera", "rootfs1 Opera Presto 6213"),
        ("app_netflix", "extracted/rootfs1/netflix/nrd-app/bin/nrd-app", "rootfs1 Netflix NRD binary"),
        ("app_dial", "extracted/rootfs1/vendor/dialserver/dialserver", "rootfs1 DIAL daemon"),
        ("core_lib", "extracted/appfs1/basic/libmtkapp.so", "UI/Upgrade middleware"),
        ("core_lib", "extracted/appfs1/basic/libdtv_common.so", "DLM crypto & partition API"),
        ("core_lib", "extracted/appfs1/basic/libnettv_proxy.so", "NetTV proxy shared library"),
        ("core_lib", "extracted/rootfs1/nettv/libnettv.so", "NetTV browser controller"),
        ("core_lib", "extracted/appfs1/lib/libc-2.12.2.so", "GNU C Library 2.12.2"),
        ("core_lib", "extracted/appfs1/basic/lib/libssl.so.1.0.0", "OpenSSL 1.0.0d TLS library"),
        ("core_lib", "extracted/appfs1/basic/lib/libcrypto.so.1.0.0", "OpenSSL 1.0.0d crypto library"),
        ("core_lib", "extracted/appfs1/basic/lib/libcurl.so.4.2.0", "libcurl 7.21.7"),
        ("core_lib", "extracted/rootfs1/lib/libxml2.so.2.7.8", "libxml2 2.7.8"),
        ("core_lib", "extracted/rootfs1/qt/lib/libQtCore.so.4.8.3", "QtCore 4.8.3"),
        ("core_lib", "extracted/rootfs1/qt/lib/libQtDeclarative.so.4.8.3", "QtDeclarative QML 4.8.3"),
        ("drm_lib", "extracted/appfs1/basic/lib/libplayready.so", "Microsoft PlayReady DRM"),
        ("drm_lib", "extracted/rootfs1/widevine/libWVStreamControlAPI.so", "Widevine DRM"),
    ]:
        add_binary("WORKSPACE", ws / rel, rel, cat, src)

    # 4. Kernel modules (.ko) + filesystem inventory
    ko_rows: List[List[str]] = []
    fs_rows: List[List[str]] = []

    seen_ko: Dict[str, Path] = {}
    for tree_name, part_label in [("extracted/appfs1", "appfs1"), ("extracted/rootfs1", "rootfs1")]:
        root_dir = ws / tree_name
        if not root_dir.is_dir():
            continue
        for dp, dns, fns in os.walk(root_dir, followlinks=False):
            dns.sort()
            fns.sort()
            dp_path = Path(dp)
            for dn in dns:
                sub = dp_path / dn
                st = os.lstat(sub)
                rel = sub.relative_to(root_dir)
                fs_rows.append([part_label, str(rel), "dir", "0", oct(stat.S_IMODE(st.st_mode)), "", ""])
            for fn in fns:
                fp = dp_path / fn
                rel = fp.relative_to(root_dir)
                st = os.lstat(fp)
                mode = oct(stat.S_IMODE(st.st_mode))
                if stat.S_ISLNK(st.st_mode):
                    target = os.readlink(fp)
                    fs_rows.append([part_label, str(rel), "symlink", str(st.st_size), mode, target, ""])
                elif stat.S_ISREG(st.st_mode):
                    digest = sha256_file(fp)
                    fs_rows.append([part_label, str(rel), "file", str(st.st_size), mode, "", digest])
                    if fn.endswith(".ko"):
                        ws_rel = str(fp.relative_to(ws))
                        seen_ko[ws_rel] = fp
                        add_binary("WORKSPACE", fp, ws_rel, "kernel_module", f"Linux 3.0.13 {part_label}")
                else:
                    fs_rows.append([part_label, str(rel), "special", str(st.st_size), mode, "", ""])

    for ws_rel, ko_path in sorted(seen_ko.items()):
        mi = parse_modinfo(ko_path)
        digest = sha256_file(ko_path)
        size = ko_path.stat().st_size
        ko_rows.append([
            ko_path.name,
            ws_rel,
            str(size),
            digest,
            mi["vermagic"],
            mi["license"],
            mi["description"],
            mi["author"],
            mi["depends"],
            mi["srcversion"],
            "CONFIRMED",
        ])

    # 5. Tracked repository artifacts (Section B)
    manifest_lines.append("")
    manifest_lines.append("# === SECTION B: TRACKED REPOSITORY ARTIFACTS (CI VERIFIED) ===")
    for rp in collect_repo_tracked_files(repo):
        rel_repo = str(rp.relative_to(repo))
        digest = sha256_file(rp)
        size = rp.stat().st_size
        manifest_lines.append(f"{digest}  {size}  REPO  {rel_repo}")

    manifest_path = repo / "firmware-forensics" / "FIRMWARE_HASH_MANIFEST.txt"
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    bin_csv = repo / "firmware-forensics" / "FIRMWARE_BINARY_INVENTORY.csv"
    with bin_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "path", "size_bytes", "sha256", "elf_machine", "elf_bits", "abi_or_type", "status", "evidence_source"])
        w.writerows(bin_rows)

    ko_csv = repo / "kernel-analysis" / "KERNEL_MODULE_INVENTORY.csv"
    with ko_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module_name", "path", "size_bytes", "sha256", "vermagic", "license", "description", "author", "depends", "srcversion", "status"])
        w.writerows(ko_rows)

    fs_csv = repo / "filesystem" / "FILESYSTEM_INVENTORY.csv"
    with fs_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["partition", "root_relative_path", "entry_type", "size_bytes", "mode_octal", "symlink_target", "sha256_if_file"])
        w.writerows(fs_rows)

    print(f"Wrote {manifest_path} ({len(manifest_lines)} lines)")
    print(f"Wrote {bin_csv} ({len(bin_rows)} binaries)")
    print(f"Wrote {ko_csv} ({len(ko_rows)} kernel modules)")
    print(f"Wrote {fs_csv} ({len(fs_rows)} filesystem entries)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate firmware hash, binary, kernel-module, and filesystem inventories.")
    default_repo = SCRIPT_DIR.parent
    parser.add_argument("--repo", default=str(default_repo), help="Repository root directory")
    parser.add_argument("--workspace", default=str(default_repo.parent), help="Workspace root holding extracted firmware")
    args = parser.parse_args()
    build_inventories(Path(args.workspace).resolve(), Path(args.repo).resolve())


if __name__ == "__main__":
    main()
