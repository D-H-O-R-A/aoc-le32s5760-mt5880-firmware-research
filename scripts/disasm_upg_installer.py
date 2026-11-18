#!/usr/bin/env python3
"""
Reproduces Capstone ARM disassembly of the TV firmware upgrader internals:
1. libmtkapp.so:
   - sub_404f28 (PART -> nand_%d vs PMTD -> mtd0..mtd13)
   - _phm_upg_model_start_upgrade (bank-switch skip on 3rdp, erase call)
   - sub_407d4c / sub_4074c0 (METHOD=FILE safe rm -rf, mkdir, tar zxf extraction)
2. libdtv_common.so:
   - x_dlm_set_aes_key_iv (0x9b7ec), dlm_aes (0x97154),
     dlm_locate_codefile_hdr (0x98b60, key 0x94102909*4),
     x_dlm_download_by_tag (0x995b4..0x99698, MD5(key/iv) + "reserved mtk inc")
"""

import argparse
import re
import struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM


def disasm_block(data: bytes, start: int, end: int, title: str, limit: int = 120) -> None:
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    print(f"\n=== {title} (0x{start:06x}..0x{end:06x}) ===")
    cnt = 0
    for ins in md.disasm(data[start:end], start):
        print(f"  0x{ins.address:06x}: {ins.mnemonic:<8} {ins.op_str}")
        cnt += 1
        if cnt >= limit:
            print("  ... [truncated]")
            break


def dump_pic_strings(data: bytes, got_base: int, start: int, end: int, title: str) -> None:
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    print(f"\n=== {title} (resolved PC/GOT refs @ 0x{start:06x}..0x{end:06x}) ===")
    for ins in md.disasm(data[start:end], start):
        if "[pc," in ins.op_str:
            m = re.search(r"#(-?0x[0-9a-f]+|-?\d+)", ins.op_str)
            if m:
                t = ins.address + 8 + int(m.group(1), 0)
                if 0 <= t <= len(data) - 4:
                    rel = struct.unpack_from("<i", data, t)[0]
                    addr = (got_base + rel) & 0xffffffff
                    if 0 < addr < len(data) - 4:
                        raw = data[addr:addr + 72].split(b"\x00")[0]
                        if len(raw) >= 2 and all(32 <= b < 127 or b in (9, 10) for b in raw):
                            print(f"  0x{ins.address:06x}: {ins.mnemonic:<8} {ins.op_str:<20} -> 0x{addr:06x}: {raw!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Disassemble libmtkapp.so & libdtv_common.so UPG mechanisms")
    parser.add_argument("--libmtkapp", required=True, help="Path to extracted/appfs1/basic/libmtkapp.so")
    parser.add_argument("--libdtv", required=True, help="Path to extracted/appfs1/basic/libdtv_common.so")
    args = parser.parse_args()

    mtk = open(args.libmtkapp, "rb").read()
    dlm = open(args.libdtv, "rb").read()

    # Check key strings in libmtkapp.so
    print("=== libmtkapp.so UPG Format & Whitelist Strings ===")
    for needle in [b"nand_%d", b"mtd10", b"smth", b"tar zxf %s -C %s", b"/ro_data/smarthome/", b"mkdir %s", b"Upgrade NG", b"Upgrade Successful"]:
        pos = mtk.find(needle)
        print(f"  0x{pos:06x}: {mtk[pos:pos + 64].split(bytes([0]))[0]!r}")

    print("\n=== libmtkapp.so PMTD Target Strings (.rodata @ 0x5b0b54..0x5b0c20) ===")
    pos = 0x5b0b54
    idx = 0
    while pos < 0x5b0c18 and idx <= 22:
        s = mtk[pos:pos + 24].split(b"\x00")[0]
        if s:
            print(f"  PMTD[{idx:2d}] @ 0x{pos:06x}: {s.decode('ascii', 'replace')!r}")
            idx += 1
            pos += len(s) + 1
            pos = (pos + 3) & ~3
        else:
            pos += 4

    disasm_block(mtk, 0x404f28, 0x405040, "libmtkapp.so sub_404f28 (METHOD device path builder)")
    dump_pic_strings(mtk, 0x68aa74, 0x4074f8, 0x4075b0, "libmtkapp.so sub_4074c0 (tar zxf vs busybox unzip gate)")
    dump_pic_strings(mtk, 0x68aa74, 0x407d9c, 0x408190, "libmtkapp.so sub_407d4c (rm -rf -> mkdir -> tar)")

    disasm_block(mtk, 0x4060d0, 0x4061b0, "libmtkapp.so AES/RSA key file loader (reads raw 33-byte AES_Prod files)")
    disasm_block(mtk, 0x40ae50, 0x40af20, "libmtkapp.so _phm_upg_model_start_upgrade bank switch skip")

    print("\n=== libdtv_common.so DLM Crypto Constants ===")
    for needle in [b"#DH@FiRm", b"reserved mtk inc", b"New MTK Signature", b"New Philips Signature", b"Validate codefile HMAC"]:
        pos = dlm.find(needle)
        print(f"  0x{pos:06x}: {dlm[pos:pos + 48].split(bytes([0]))[0]!r}")

    disasm_block(dlm, 0x98b60, 0x98ce0, "libdtv_common.so dlm_locate_codefile_hdr (0x94102909*4 key & #DH@FiRm)")
    disasm_block(dlm, 0x995b4, 0x99698, "libdtv_common.so x_dlm_download_by_tag (MD5(key/iv) & 'reserved mtk inc')")


if __name__ == "__main__":
    main()
