#!/usr/bin/env python3
"""
Reproduces Capstone ARM/Thumb disassembly of the hardware/kernel Secure Boot chain:
1. MT5880 Preloader (uboot.bin[0..0xa040], base 0xfb000000): eFuse 0xf0008664 & SW flag,
   BootROM RSA-2048 calls, HW LZHS peripheral 0xf00080b0, infinite halt on verify error.
2. Linux vmlinux.bin (base 0xc0008000): dm_mount_root_nfsb (0xc00095d4),
   populate_table_nfsb (0xc0224404), and nfsb_rsa_check (0xc0028dfc / 0xc0028e38).
"""

import argparse
import re
import struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB


def dump_thumb(data: bytes, start_va: int, end_va: int, base: int, title: str) -> None:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    print(f"\n=== {title} (Thumb @ 0x{start_va:08x}..0x{end_va:08x}) ===")
    for ins in md.disasm(data[start_va - base : end_va - base], start_va):
        extra = ""
        if "[pc," in ins.op_str:
            m = re.search(r"#(0x[0-9a-f]+|\d+)", ins.op_str)
            if m:
                pool = ((ins.address + 4) & ~3) + int(m.group(1), 0)
                if 0 <= pool - base <= len(data) - 4:
                    val = struct.unpack_from("<I", data, pool - base)[0]
                    extra = f" ; [0x{pool:08x}] = 0x{val:08x}"
        print(f"  0x{ins.address:08x}: {ins.mnemonic:<8} {ins.op_str}{extra}")


def dump_arm(data: bytes, start_va: int, end_va: int, base: int, title: str, limit: int = 120) -> None:
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    print(f"\n=== {title} (ARM @ 0x{start_va:08x}..0x{end_va:08x}) ===")
    cnt = 0
    for ins in md.disasm(data[start_va - base : end_va - base], start_va):
        extra = ""
        if "[pc," in ins.op_str:
            m = re.search(r"#(-?0x[0-9a-f]+|-?\d+)", ins.op_str)
            if m:
                pool = ins.address + 8 + int(m.group(1), 0)
                if 0 <= pool - base <= len(data) - 4:
                    val = struct.unpack_from("<I", data, pool - base)[0]
                    s = ""
                    if base <= val < base + len(data) - 4:
                        raw = data[val - base : val - base + 40].split(b"\x00")[0]
                        if len(raw) >= 4 and all(32 <= b < 127 or b == 10 for b in raw):
                            s = f" ({raw!r})"
                    extra = f" ; *(0x{pool:08x})=0x{val:08x}{s}"
        print(f"  0x{ins.address:08x}: {ins.mnemonic:<8} {ins.op_str}{extra}")
        cnt += 1
        if cnt >= limit:
            print("  ... [truncated for brevity]")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Disassemble Preloader + Linux NFSB enforcement")
    parser.add_argument("--uboot", required=True, help="Path to extracted/uboot.bin")
    parser.add_argument("--vmlinux", required=True, help="Path to scratch/vmlinux.bin")
    args = parser.parse_args()

    ub = open(args.uboot, "rb").read()
    print(f"uboot.bin length: {len(ub)} bytes")
    print(f"Preloader SW secure flag @ 0xfb0053bc (file +0x53bc): {struct.unpack_from('<I', ub, 0x53bc)[0]}")
    print(f"LZHS header @ 0xa040: {ub[0xa040:0xa050].hex()}")
    out_sz, comp_sz = struct.unpack_from("<II", ub, 0xa040)
    print(f"  decompressed_size={out_sz} bytes (0x{out_sz:x}), compressed_size={comp_sz} bytes (0x{comp_sz:x}), csum=0x{ub[0xa048]:02x}")
    print(f"  U-Boot RSA signature @ +0x6c4b0..+0x6c5b0 (prefix): {ub[0x6c4b0:0x6c4d0].hex()}")
    print(f"  U-Boot RSA cert      @ +0x6c5b0..+0x6c6b0 (prefix): {ub[0x6c5b0:0x6c5d0].hex()}")

    dump_thumb(ub, 0xfb00048c, 0xfb000534, 0xfb000000, "Preloader Main U-Boot Loader & Halt on RSA Failure")
    dump_thumb(ub, 0xfb00144c, 0xfb00153c, 0xfb000000, "Preloader eFuse (0xf0008664) + RSA Verify + HW LZHS (0xf00080b0)")

    vm_raw = open(args.vmlinux, "rb").read()
    ih_magic, _hcrc, _ts, ih_size, ih_load, ih_ep = struct.unpack(">IIIIII", vm_raw[:24])
    assert ih_magic == 0x27051956
    print(f"\nvmlinux.bin uImage hdr: magic=0x{ih_magic:08x}, size={ih_size} B, load=0x{ih_load:08x}, ep=0x{ih_ep:08x} (stripping 0x40 hdr -> base=0xc0008000)")
    vm = vm_raw[0x40:]
    dump_arm(vm, 0xc0028d44, 0xc0029048, 0xc0008000, "Linux Kernel nfsb_header accessors & nfsb_rsa_check", limit=240)
    dump_arm(vm, 0xc0009594, 0xc0009990, 0xc0008000, "Linux Kernel dm_mount_root_nfsb (rfsA/rfsB)", limit=280)
    dump_arm(vm, 0xc02243c4, 0xc0224658, 0xc0008000, "Linux Kernel populate_table_nfsb (3rdA/3rdB)", limit=200)


if __name__ == "__main__":
    main()
