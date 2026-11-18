#!/usr/bin/env python3
"""
Verifies end-to-end two-level dm-bht MD5 Merkle trees on stock NFSB partitions
(3rdA 23,767 4KB blocks, rfsA 12,514 4KB blocks), inspects SquashFS 4.0 superblocks,
audits TV boot scripts stripping vendor license boilerplate, and diffs opera.ini
vs custom opera_new.ini.
"""

import argparse
import hashlib
import os
import struct


def verify_dmbht(pkg_path: str, tag: str, poff: int, size: int) -> None:
    with open(pkg_path, "rb") as f:
        f.seek(poff)
        hdr = f.read(0xe7)
        assert hdr[:4] == b"NFSB"
        version = hdr[4]
        fs_off_sec = struct.unpack(">I", hdr[5:9])[0]
        fs_sz_sec = struct.unpack(">I", hdr[9:13])[0]
        depth = hdr[13]
        hash_algo = hdr[14:30].split(b"\x00")[0].decode("ascii", "replace")
        hash_sz_sec = struct.unpack(">I", hdr[30:34])[0]
        blk_sec = struct.unpack(">I", hdr[34:38])[0]
        root_hex = hdr[38:102].split(b"\x00")[0].decode("ascii", "replace")

        fs_off = fs_off_sec * 512
        fs_sz = fs_sz_sec * 512
        hash_sz = hash_sz_sec * 512
        n_blocks = fs_sz // 4096
        n_leaf_pages = (n_blocks + 255) // 256

        f.seek(poff + fs_off)
        sq_hdr = f.read(64)
        s_magic, inodes, mkfs_time, blk_sz, _frags, comp_id, _flags, _no_ids, maj, minv, _root_ino, bytes_used = struct.unpack_from(
            "<IIIIIIHHHHQQ", sq_hdr, 0
        )

        f.seek(poff + fs_off)
        data = f.read(fs_sz)
        f.seek(poff + fs_off + fs_sz)
        tree = f.read(size - (fs_off + fs_sz))

    # Level 1 leaves start at page 1 (offset 4096) in hash tree
    leaf_calc = b"".join(hashlib.md5(data[i * 4096 : (i + 1) * 4096]).digest() for i in range(n_blocks))
    leaf_ok = leaf_calc == tree[4096 : 4096 + n_blocks * 16]

    # Level 0 parent page at tree[0:4096] holds MD5s of all Level-1 leaf pages
    lvl0_calc = b"".join(hashlib.md5(tree[(1 + p) * 4096 : (2 + p) * 4096]).digest() for p in range(n_leaf_pages))
    lvl0_ok = lvl0_calc == tree[0 : n_leaf_pages * 16]
    lvl0_zero_pad = tree[n_leaf_pages * 16 : 4096] == (b"\x00" * (4096 - n_leaf_pages * 16))
    root_calc = hashlib.md5(tree[0:4096]).hexdigest()
    root_ok = root_calc == root_hex

    assert leaf_ok and lvl0_ok and lvl0_zero_pad and root_ok

    print(f"=== NFSB + SquashFS + dm-bht Verification: {tag} ({size:,} bytes) ===")
    print(f"  NFSB Header      : version={version}, depth={depth}, algo={hash_algo!r}, blk_sectors={blk_sec} ({blk_sec * 512} B)")
    print(f"  Geometry         : fs_off=0x{fs_off:x} ({fs_off_sec} sec), fs_size=0x{fs_sz:x} ({fs_sz_sec} sec = {n_blocks} x 4KB)")
    print(f"  Hash Tree Size   : {hash_sz} B ({hash_sz_sec} sec = {hash_sz // 4096} pages: 1 parent + {n_leaf_pages} leaf)")
    print(f"  SquashFS @ 0x{fs_off:x} : magic={sq_hdr[:4]!r} v{maj}.{minv}, inodes={inodes}, blk_sz={blk_sz}, comp_id=0x{comp_id:x}, used={bytes_used:,} B")
    print(f"  Leaf MD5 Match   : {leaf_ok} ({n_blocks:,} / {n_blocks:,} 4KB blocks verified)")
    print(f"  Level-0 Match    : {lvl0_ok} ({n_leaf_pages} leaf pages verified, zero-pad={lvl0_zero_pad})")
    print(f"  Signed Root MD5  : {root_hex}")
    print(f"  Computed Root    : {root_calc} (EXACT MATCH={root_ok})\n")


def strip_license_and_dump(path: str, label: str) -> None:
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    print(f"=== Boot Script Excerpt: {label} ({len(lines)} total lines) ===")
    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if idx <= 75 and (s.startswith("#") or not s):
            continue
        if s:
            print(f"  L{idx:03d}: {line}")
    print()


def parse_ini(path: str) -> dict[tuple[str, str], str]:
    res = {}
    sec = ""
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        if s.startswith("[") and s.endswith("]"):
            sec = s[1:-1]
        elif "=" in s:
            k, v = s.split("=", 1)
            res[(sec, k.strip())] = v.strip()
    return res


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify dm-bht Merkle trees, boot scripts, and opera.ini diff")
    parser.add_argument("--workspace", required=True, help="Path to AOC/LE32S5760 base workspace")
    parser.add_argument("--repo", required=True, help="Path to research repository root")
    args = parser.parse_args()
    ws, repo = args.workspace, args.repo

    pkg_path = os.path.join(ws, "extracted/upgrade_loader.pkg")
    verify_dmbht(pkg_path, "3rdA", 0x05D360B0, 97738752)
    verify_dmbht(pkg_path, "rfsA", 0x0FE99539, 51466240)

    for rel, lbl in [
        ("extracted/appfs1/etc/rc.d/rc.local.partial", "etc/rc.d/rc.local.partial"),
        ("extracted/appfs1/etc/scripts/dmverity_mount_3rda.sh", "etc/scripts/dmverity_mount_3rda.sh"),
        ("extracted/appfs1/etc/scripts/dmverity_mount_3rdb.sh", "etc/scripts/dmverity_mount_3rdb.sh"),
        ("extracted/appfs1/etc/scripts/ubi_mount_3rd_rw.sh", "etc/scripts/ubi_mount_3rd_rw.sh"),
        ("extracted/appfs1/etc/scripts/ubi_mount_perm.sh", "etc/scripts/ubi_mount_perm.sh"),
        ("extracted/appfs1/etc/scripts/ubi_mount_ro_data.sh", "etc/scripts/ubi_mount_ro_data.sh"),
        ("extracted/appfs1/basic/autorun.sh", "basic/autorun.sh"),
    ]:
        strip_license_and_dump(os.path.join(ws, rel), lbl)

    stock_ini = parse_ini(os.path.join(ws, "extracted/rootfs1/nettv/opera/opera_home/opera.ini"))
    cust_ini = parse_ini(os.path.join(repo, "custom_payload/nettv/opera_new.ini"))
    print("=== Configuration Delta: stock opera.ini vs custom opera_new.ini ===")
    all_keys = sorted(set(stock_ini) | set(cust_ini))
    for k in all_keys:
        sv = stock_ini.get(k, "<ABSENT>")
        cv = cust_ini.get(k, "<ABSENT>")
        if sv != cv:
            print(f"  [{k[0]}] {k[1]}: stock={sv!r}  -->  custom={cv!r}")


if __name__ == "__main__":
    main()
