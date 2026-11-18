#!/usr/bin/env python3
"""
Extracts ELF32 dynamic linking metadata (DT_NEEDED, RPATH, SONAME, section layout)
across core firmware binaries and disassembles SystemManager (SMConfig/dynqml),
dtv_svc (sys_start.c customer_version), and libnettv.so (_imnettv_copydata).
"""

import argparse
import os
import re
import struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM


def vaddr_to_off(phdrs: list[tuple[int, int, int, int]], vaddr: int) -> int | None:
    for p_off, p_vaddr, p_filesz, _ in phdrs:
        if p_vaddr <= vaddr < p_vaddr + p_filesz:
            return p_off + (vaddr - p_vaddr)
    return None


def audit_elf(path: str) -> None:
    d = open(path, "rb").read()
    assert d[:4] == b"\x7fELF" and d[4] == 1, f"Not ELF32: {path}"
    e_type, e_machine, _, e_entry, e_phoff, e_shoff = struct.unpack_from("<HHIIII", d, 16)
    e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHHHH", d, 42)

    loads = []
    dyn_off = dyn_sz = 0
    for i in range(e_phnum):
        pt, po, pv, pp, pfs, pms, pf, pa = struct.unpack_from("<IIIIIIII", d, e_phoff + i * e_phentsize)
        if pt == 1:
            loads.append((po, pv, pfs, pms))
        elif pt == 2:
            dyn_off, dyn_sz = po, pfs

    needed, rpaths, soname = [], [], None
    if dyn_off:
        dyn_entries = []
        strtab_va = strsz = None
        for off in range(dyn_off, dyn_off + dyn_sz, 8):
            tag, val = struct.unpack_from("<II", d, off)
            if tag == 0:
                break
            dyn_entries.append((tag, val))
            if tag == 5:  # DT_STRTAB
                strtab_va = val
            elif tag == 10:  # DT_STRSZ
                strsz = val
        if strtab_va is not None and strsz:
            stoff = vaddr_to_off(loads, strtab_va)
            if stoff is not None:
                strtab = d[stoff : stoff + strsz]
                for tag, val in dyn_entries:
                    s = strtab[val : val + 256].split(b"\x00")[0].decode("ascii", "replace")
                    if tag == 1:  # DT_NEEDED
                        needed.append(s)
                    elif tag in (15, 29):  # DT_RPATH / DT_RUNPATH
                        rpaths.append(s)
                    elif tag == 14:  # DT_SONAME
                        soname = s

    print(f"=== ELF Audit: {os.path.basename(path)} ({len(d):,} bytes) ===")
    print(f"  e_type={e_type} ({'ET_EXEC' if e_type == 2 else 'ET_DYN' if e_type == 3 else e_type}), entry=0x{e_entry:08x}, soname={soname!r}")
    if rpaths:
        print(f"  RPATH/RUNPATH: {'; '.join(rpaths)}")
    if e_shoff and e_shnum:
        shstr_off = struct.unpack_from("<I", d, e_shoff + e_shstrndx * e_shentsize + 16)[0]
        secs = []
        for i in range(e_shnum):
            sh_name, _, _, sh_addr, sh_off, sh_size, *_ = struct.unpack_from("<IIIIIIIIII", d, e_shoff + i * e_shentsize)
            sname = d[shstr_off + sh_name : shstr_off + sh_name + 32].split(b"\x00")[0].decode("ascii", "replace")
            if sname in (".text", ".rodata", ".dynsym", ".dynamic", ".got", ".data", ".bss"):
                secs.append(f"{sname}@0x{sh_addr:x}(off=0x{sh_off:x},sz=0x{sh_size:x})")
        print(f"  Sections: {', '.join(secs)}")
    print(f"  DT_NEEDED ({len(needed)}): {', '.join(needed)}\n")


def disasm_exec_or_pic(path: str, load_va: int, got_va: int | None, start_va: int, end_va: int, title: str) -> None:
    d = open(path, "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    print(f"\n=== {title} (0x{start_va:06x}..0x{end_va:06x}) ===")
    s_off = start_va - load_va
    e_off = end_va - load_va
    for ins in md.disasm(d[s_off:e_off], start_va):
        extra = ""
        if "[pc," in ins.op_str:
            m = re.search(r"#(-?0x[0-9a-f]+|-?\d+)", ins.op_str)
            if m:
                pool_va = ins.address + 8 + int(m.group(1), 0)
                pool_off = pool_va - load_va
                if 0 <= pool_off <= len(d) - 4:
                    raw_i = struct.unpack_from("<i", d, pool_off)[0]
                    raw_u = raw_i & 0xffffffff
                    target_va = ((got_va + raw_i) & 0xffffffff) if got_va is not None else raw_u
                    t_off = target_va - load_va
                    s = ""
                    if 0 <= t_off < len(d) - 4:
                        cand = d[t_off : t_off + 64].split(b"\x00")[0]
                        if len(cand) >= 2 and all(32 <= b < 127 or b in (9, 10) for b in cand):
                            s = f" {cand!r}"
                    extra = f" ; *(0x{pool_va:x})->0x{target_va:06x}{s}"
        print(f"  0x{ins.address:06x}: {ins.mnemonic:<8} {ins.op_str}{extra}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit firmware ELFs and disassemble SystemManager/dtv_svc/libnettv")
    parser.add_argument("--workspace", required=True, help="Path to AOC/LE32S5760 base workspace")
    args = parser.parse_args()
    ws = args.workspace

    rel_bins = [
        "extracted/rootfs1/qt/AEDK/SystemManager/SystemManager",
        "extracted/appfs1/basic/dtv_svc",
        "extracted/rootfs1/nettv/libnettv.so",
        "extracted/rootfs1/nettv/libopera_hbbtv.so",
        "extracted/rootfs1/nettv/opera/browser.out",
        "extracted/rootfs1/netflix/nrd-app/netflix",
        "extracted/rootfs1/leanback/wrp_leanback",
        "extracted/appfs1/basic/libmtkapp.so",
        "extracted/appfs1/basic/libdtv_common.so",
    ]
    for rel in rel_bins:
        audit_elf(os.path.join(ws, rel))

    sm_path = os.path.join(ws, "extracted/rootfs1/qt/AEDK/SystemManager/SystemManager")
    disasm_exec_or_pic(sm_path, 0x8000, None, 0x1619e4, 0x161a70, "SystemManager main path initialization")
    disasm_exec_or_pic(sm_path, 0x8000, None, 0x16e428, 0x16e4b8, "SystemManager SMConfig initialization")
    disasm_exec_or_pic(sm_path, 0x8000, None, 0x1db58c, 0x1db620, "SystemManager dynqml==0 (qrc:/HomeScreen/HSMain.qml)")
    disasm_exec_or_pic(sm_path, 0x8000, None, 0x1db7a4, 0x1db840, "SystemManager dynqml==1 (/res/HomeScreen/HSMain.qml)")

    dtv_path = os.path.join(ws, "extracted/appfs1/basic/dtv_svc")
    disasm_exec_or_pic(dtv_path, 0x8000, 0x411170, 0x036190, 0x036320, "dtv_svc mount_3rd_rw & customer_version Opera copy")

    net_path = os.path.join(ws, "extracted/rootfs1/nettv/libnettv.so")
    disasm_exec_or_pic(net_path, 0x0, None, 0x188b48, 0x188d20, "libnettv.so _imnettv_copydata opera_new.ini hook")


if __name__ == "__main__":
    main()
