#!/usr/bin/env python3
"""
Inspects stock MTK upgrade_loader.pkg partition table, cfig layout, and NFSB
cryptographic headers, mathematically verifying raw RSA-1024 (e=3) signatures
against the public modulus embedded in decompressed Linux kernel (vmlinux.bin).
"""

import argparse
import hashlib
import os
import struct


KNOWN_PARTS = [
    b"3rdB", b"3rdA", b"roda", b"cfig", b"load", b"uenv",
    b"adsp", b"aqda", b"pqda", b"rfsB", b"rfsA", b"kerB",
    b"kerA", b"usig", b"chtD", b"chtC",
]


def parse_pkg_headers(pkg_path: str):
    """Parses tagged partitions inside an MTK upgrade_loader.pkg file."""
    data = open(pkg_path, "rb").read()
    pos = 0x98  # 152-byte outer package prefix
    entries = []
    while pos + 12 <= len(data):
        tag = data[pos:pos + 4]
        if tag not in KNOWN_PARTS:
            break
        _hdr_val, size = struct.unpack_from("<II", data, pos + 4)
        payload_off = pos + 12
        entries.append((tag.decode("ascii"), pos, payload_off, size))
        pos = payload_off + size
    return data, entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify PKG partitions and NFSB RSA-1024 signatures")
    parser.add_argument("--pkg", required=True, help="Path to stock upgrade_loader.pkg")
    parser.add_argument("--custom-pkg", default=None, help="Optional modified upgrade_loader.pkg to prove RSA rejection")
    parser.add_argument("--vmlinux", required=True, help="Path to decompressed vmlinux.bin (VA base 0xc0008000)")
    args = parser.parse_args()

    pkg, entries = parse_pkg_headers(args.pkg)
    print(f"=== MTK PKG Partition Table ({os.path.basename(args.pkg)}, {len(pkg)} bytes) ===")
    print(f"{'Idx':<4} {'Tag':<6} {'HeaderOff':<12} {'PayloadOff':<12} {'SizeBytes':<12} {'SizeMB':<8}")
    print("-" * 60)
    by_tag = {}
    for idx, (tag, hoff, poff, sz) in enumerate(entries, 1):
        print(f"{idx:<4} {tag:<6} 0x{hoff:08x}   0x{poff:08x}   {sz:<12} {sz / (1024 * 1024):6.2f} MB")
        by_tag[tag] = (hoff, poff, sz)

    if "cfig" in by_tag:
        _, poff, sz = by_tag["cfig"]
        cfig_tokens = pkg[poff:poff + sz].decode("ascii", "replace").strip().splitlines()
        print("\n=== Embedded NAND Partition Map ('cfig') ===")
        print(" -> ".join(cfig_tokens))

    for ktag in ("kerA", "kerB"):
        if ktag in by_tag:
            _, poff, sz = by_tag[ktag]
            kdata = pkg[poff:poff + sz]
            uimg_magic = kdata[:4].hex()
            # Signature & certificate trailers observed in stock kerA/kerB
            print(f"\n=== Kernel Image ({ktag}, {sz} bytes) ===")
            print(f"  uImage magic: 0x{uimg_magic} (0x27051956 = U-Boot uImage)")
            print(f"  Trailer @ 0x25152c..0x25154c: {kdata[0x25152c:0x25154c].hex()}")
            print(f"  Trailer @ 0x283f2c..0x283f4c: {kdata[0x283f2c:0x283f4c].hex()}")

    vm_raw = open(args.vmlinux, "rb").read()
    # vmlinux.bin starts with a 64-byte U-Boot uImage header (IH_MAGIC=0x27051956, load=0x00007fc0, ep=0x00008000)
    ih_magic, _hcrc, _ts, ih_size, ih_load, ih_ep = struct.unpack(">IIIIII", vm_raw[:24])
    assert ih_magic == 0x27051956, f"Unexpected uImage header magic: 0x{ih_magic:08x}"
    vm = vm_raw[0x40:]
    base = 0xc0008000
    e_bytes = vm[0xc04292f0 - base : 0xc0429370 - base]  # 128-byte BE RSA exponent
    n_bytes = vm[0xc0429370 - base : 0xc04293f0 - base]  # 128-byte BE RSA-1024 modulus
    e = int.from_bytes(e_bytes, "big")
    n = int.from_bytes(n_bytes, "big")
    print("\n=== Linux Kernel Embedded NFSB RSA-1024 Key (vmlinux.bin @ VA 0xc0008000, uImage hdr stripped) ===")
    print(f"  uImage Header : magic=0x{ih_magic:08x}, payload_size={ih_size} B, load=0x{ih_load:08x}, ep=0x{ih_ep:08x}")
    print(f"  Exponent @ VA 0xc04292f0 (128B BE): e = {e}")
    print(f"  Modulus  @ VA 0xc0429370 (128B BE): {n.bit_length()} bits")
    print(f"  N[:32] = {n_bytes[:32].hex()}")
    print(f"  N[-32:] = {n_bytes[-32:].hex()}")

    print("\n=== Mathematical Verification of NFSB Headers (pow(sig, e, N) == 0^96 || SHA256(hdr[0:0x67])) ===")
    for ptag in ("3rdB", "3rdA", "rfsB", "rfsA"):
        _, poff, _ = by_tag[ptag]
        hdr = pkg[poff : poff + 0xe7]
        assert hdr[:4] == b"NFSB", f"Missing NFSB magic on {ptag}"
        hash_alg = hdr[0x0e:0x20].split(b"\x00")[0].decode("ascii", "replace")
        sig = int.from_bytes(hdr[0x67:0xe7], "big")
        dec = pow(sig, e, n).to_bytes(128, "big")
        calc_sha = hashlib.sha256(hdr[:0x67]).digest()
        zero_pad_ok = (dec[:96] == b"\x00" * 96)
        exact_match = (dec == (b"\x00" * 96) + calc_sha)
        print(f"  [{ptag}] @ 0x{poff:08x}: magic=NFSB v{hdr[4]}, tree_hash={hash_alg!r}, hdr_sha256={calc_sha.hex()}")
        print(f"           RSA_dec_upper96_zero={zero_pad_ok}, RSA_exact_match={exact_match}")
        assert exact_match, f"NFSB verification failed for {ptag}"

    if args.custom_pkg and os.path.isfile(args.custom_pkg):
        cpkg, centries = parse_pkg_headers(args.custom_pkg)
        c_by_tag = {t: (h, p, s) for (t, h, p, s) in centries}
        _, cpoff, csz = c_by_tag["3rdA"]
        chdr = cpkg[cpoff : cpoff + 0xe7]
        csig = int.from_bytes(chdr[0x67:0xe7], "big")
        cdec = pow(csig, e, n).to_bytes(128, "big")
        ccalc = hashlib.sha256(chdr[:0x67]).digest()
        c_ok = (cdec == (b"\x00" * 96) + ccalc)
        print(f"\n=== Counter-Proof on Modified Package ({os.path.basename(args.custom_pkg)}) ===")
        print(f"  [3rdA] size={csz} bytes, patched hdr[0x18:0x1c]={chdr[0x18:0x1c].hex()}")
        print(f"  hdr_sha256={ccalc.hex()}")
        print(f"  RSA_dec[-32:]={cdec[-32:].hex()} | RSA_exact_match={c_ok} (REJECTED BY KERNEL)")
        assert not c_ok


if __name__ == "__main__":
    main()
