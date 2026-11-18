# Chapter 1 — Hardware Architecture, `upgrade_loader.pkg` Anatomy, Flash Topology & Userland Audit

**Scope:** This chapter characterizes the embedded hardware platform, factory package format (`upgrade_loader.pkg`), NAND flash partitioning (`cfig`), Linux kernel startup choreography, dynamic linker resolution order (`LD_LIBRARY_PATH` vs vendor defects), ELF32 shared-library linkage surface, and BusyBox userland capabilities of the **AOC LE32S5760/20** (`TPV MTK2K14PLF` / **MediaTek MT5880**). Every memory offset, partition byte count, shared-library dependency, and command inventory cited below is directly verified by [`scripts/inspect_pkg_and_nfsb.py`](../scripts/inspect_pkg_and_nfsb.py), [`scripts/inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py), [`scripts/disasm_systemmanager_and_nettv.py`](../scripts/disasm_systemmanager_and_nettv.py), and [`scripts/inspect_dmbht_and_boot_scripts.py`](../scripts/inspect_dmbht_and_boot_scripts.py).

---

## 1.1 Platform Identification & Computational Envelope

The AOC LE32S5760/20 belongs to TPV Technology's **MTK2K14PLF** 2014–2016 Latin America smart television board family. Across factory DLM upgrade headers, kernel strings, and Qt/NetTV userland executables, the device identifies itself through the following verified metadata:

| Platform Attribute | Verified Value / Signature | Source Artifact |
|---|---|---|
| **Chassis / Board Family** | `TPV MTK2K14PLF` (`LT0` / `PHILIPS_2K14` lineage) | [`evidence/04_upg_container_crypto_proof.txt`](../evidence/04_upg_container_crypto_proof.txt), [`evidence/05_runtime_engines_and_busybox_audit.txt`](../evidence/05_runtime_engines_and_busybox_audit.txt) |
| **Model Identifier** | `LE32S5760/20` | DLM header `+0x50`, `ixml` `<MODEL>` |
| **Product Build Tag** | `IDTV0801_002224_9_001_23_001_225` | DLM decrypted header `+0x0C..+0x48` |
| **Firmware Release** | `002.001.205.146` (`V2.011`) | `ixml` `<VERSION>` |
| **Processor ISA** | ARMv7-A (`VFPv3`, little-endian ARM32 + Thumb-2, dual-core SMP **MT5880**) | Disassembled ELFs + `vmlinux.bin` + RPATH `451_vfp_ca9` |
| **Linux Kernel** | `Linux-3.0.13` (uImage `IH_MAGIC=0x27051956`, `load=0x00007fc0`, `ep=0x00008000`) | [`evidence/01_pkg_and_nfsb_proof.txt`](../evidence/01_pkg_and_nfsb_proof.txt) |
| **Compiler & Toolchain** | GNU GCC `4.5.1` (`451_vfp_ca9`, `gnuarm-4.5.1_vfp_ca9`) + GNU `glibc` | `SystemManager` & `netflix` ELF `RPATH` ([`evidence/06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt)) |
| **Graphics Stack** | DirectFB `1.4.1` (`libdirectfb.so`) + Qt Embedded `4.8.3` (`QWS_DISPLAY=directfb`) | `SystemManager` `RPATH`, `autorun.sh` line 108 |
| **Media & DRM Hardware** | MediaTek `libmtal.so`, `libcmpb.so`, `libmtkdrm.so`, `libmtk_hw_decrypt.so` | `dtv_svc` & `libnettv.so` `DT_NEEDED` |
| **Console UART** | `stty -F /dev/ttyMT3 115200` | `rc.local.partial` line 5 ([`evidence/07_dmbht_and_boot_scripts_audit.txt`](../evidence/07_dmbht_and_boot_scripts_audit.txt)) |

### 1.1.1 ABI & Memory Constraints Governing Third-Party Execution

Inspecting both dynamic sections and startup memory setup establishes four structural constraints on userland customization:

1. **DirectFB-Only Rendering Surface:** Neither X11 (`libX11.so`), Wayland (`libwayland-client.so`), nor Android Binder exists anywhere in `extracted/appfs1/` or `extracted/rootfs1/`. Every visual process — `SystemManager`, `dtv_svc`, `browser.out`, `netflix`, and `wrp_leanback` — explicitly requires `libdirectfb.so` in its ELF `DT_NEEDED` table (`evidence/06_systemmanager_and_nettv_disasm.txt`, lines 5–36).
2. **GCC 4.5.1 / `glibc` ABI Ceiling:** `SystemManager` was built in `/home/mtkvm/qtbuild/osslibrary/451_vfp_ca9/qt-4.8.3-dfb1.4.1/lib` and `netflix` carries build tree `/release/auto/p4/w/20150420_194932/TPV_linux_REL_PHILIPS_2K14/.../gnuarm-4.5.1_vfp_ca9/`. Any new dynamic binary linked on modern toolchains expecting newer GLIBC symbol versions (`GLIBC_2.17+` or `GLIBCXX_3.4.20+`) will fail dynamic relocation on the stock root filesystem.
3. **512 MB Shared Unified DRAM Architecture:** DRAM simultaneously hosts the Linux kernel (`~4.4 MB` uncompressed + buffers), TrustZone secure monitor RAM, DirectFB 1080p/768p framebuffers (`am_view_port`: `1 0 0 1920 1080`), hardware decoder ring buffers (`libcmpb.so`), SquashFS compressed page cache, and `tmpfs` scratch mounts (`/tmp`, where Opera's writable runtime directory `/tmp/opera_home` and `/tmp/upgrade` staging payloads reside).
4. **Tightly Coupled MediaTek Hardware Decoders:** Browser and streaming media playback inside Opera depends directly on MediaTek's Unified Video Abstraction plugins (`libuva.so`, `libuvabackend-capi.so`, `libuvabackend-mtk.so`, `libuvabackend-tpvision.so`), making generic software decoders computationally non-viable on ARMv7 dual-core SoCs without NEON/VPU offload via `libcmpb.so`.

---

## 1.2 Factory Package Anatomy: `upgrade_loader.pkg` (`323,840,461` Bytes)

MediaTek's cold-boot and full-recovery factory package format (`upgrade_loader.pkg`) packs raw NAND partition images sequentially after an outer **152-byte (`0x98`) container header**. Each partition entry consists of a **12-byte descriptor header** containing:

- Bytes `[0..4)`: 4-byte ASCII partition tag (`"3rdB"`, `"3rdA"`, `"rfsA"`, etc.).
- Bytes `[4..8)`: Little-endian `uint32_t` flags / metadata field.
- Bytes `[8..12)`: Little-endian `uint32_t` payload size (`sz` bytes), followed immediately by `sz` raw payload bytes.

Running [`scripts/inspect_pkg_and_nfsb.py`](../scripts/inspect_pkg_and_nfsb.py) against stock `extracted/upgrade_loader.pkg` (`323,840,461` bytes, `SHA-256: 219de76d6dea7f62fe3648392f6262031e230cc33380c2b173c22fc667089b83`) maps all **16 embedded partition entries** with zero trailing padding (`0x134c69cd + 65536 = 0x134d69cd = 323,840,461` bytes) ([`evidence/01_pkg_and_nfsb_proof.txt`](../evidence/01_pkg_and_nfsb_proof.txt), lines 1–20):

| Idx | Tag | Header Offset | Payload Offset | Payload Size (Bytes) | Size (MB) | Cryptographic / Filesystem Role |
|---:|---|---:|---:|---:|---:|---|
| 1 | `3rdB` | `0x00000098` | `0x000000a4` | `97,738,752` | `93.21 MB` | Secondary `/3rd` SquashFS 4.0 bank (`NFSB` RSA-1024 + `dm-bht`) |
| 2 | `3rdA` | `0x05d360a4` | `0x05d360b0` | `97,738,752` | `93.21 MB` | Primary `/3rd` SquashFS 4.0 bank (`NFSB` RSA-1024 + `dm-bht`) |
| 3 | `roda` | `0x0ba6c0b0` | `0x0ba6c0bc` | `5,767,168` | `5.50 MB` | `/ro_data` UBI volume (`TPV_MTK2K14PLF_*` keys, E-DFU web assets) |
| 4 | `cfig` | `0x0bfec0bc` | `0x0bfec0c8` | `237` | `0.00 MB` | Plaintext newline-delimited NAND/MTD partition layout specification |
| 5 | `load` | `0x0bfec1b5` | `0x0bfec1c1` | `1,314,592` | `1.25 MB` | Preloader (`[0..0xa040]`) + HW-LZHS U-Boot + RSA-2048 sig/cert |
| 6 | `uenv` | `0x0c12d0e1` | `0x0c12d0ed` | `2,384` | `0.00 MB` | U-Boot environment metadata (`env.c`) |
| 7 | `adsp` | `0x0c12da3d` | `0x0c12da49` | `1,272,368` | `1.21 MB` | Audio DSP microcode image |
| 8 | `aqda` | `0x0c264479` | `0x0c264485` | `131,216` | `0.13 MB` | Audio Quality calibration tables (`AQ.bin`) |
| 9 | `pqda` | `0x0c284515` | `0x0c284521` | `11,534,336` | `11.00 MB` | Picture Quality calibration tables (`pq.bin`) |
| 10 | `rfsB` | `0x0cd84521` | `0x0cd8452d` | `51,466,240` | `49.08 MB` | Secondary `/` RootFS + `/basic` SquashFS 4.0 (`NFSB` RSA-1024) |
| 11 | `rfsA` | `0x0fe9952d` | `0x0fe99539` | `51,466,240` | `49.08 MB` | Primary `/` RootFS + `/basic` SquashFS 4.0 (`NFSB` RSA-1024) |
| 12 | `kerB` | `0x12fae539` | `0x12fae545` | `2,638,124` | `2.52 MB` | Secondary Linux `uImage` (`0x27051956`) + TrustZone + RSA trailers |
| 13 | `kerA` | `0x13232671` | `0x1323267d` | `2,638,124` | `2.52 MB` | Primary Linux `uImage` (`0x27051956`) + TrustZone + RSA trailers |
| 14 | `usig` | `0x134b67a9` | `0x134b67b5` | `512` | `0.00 MB` | Upgrade cryptographic signature / recovery tag |
| 15 | `chtD` | `0x134b69b5` | `0x134b69c1` | `65,536` | `0.06 MB` | Broadcast channel map bank D |
| 16 | `chtC` | `0x134c69c1` | `0x134c69cd` | `65,536` | `0.06 MB` | Broadcast channel map bank C |

### 1.2.1 Factory Recovery Redundancy & Missing RW Partitions

Two critical insights emerge directly from the `upgrade_loader.pkg` layout:

1. **Symmetric Dual-Bank Factory Provisioning:** `3rdA` (`0x05d360b0`) and `3rdB` (`0x000000a4`) contain identical `97,738,752`-byte payloads sharing the exact same `NFSB` header SHA-256 (`7f8488da5bcdda386be1047c91f8bdb50848600d69ee8878c09db130f8277beb`). Likewise, `rfsA` and `rfsB` (`51,466,240` bytes each) share `b9226006f291e7f3c42103e9eb8f90dbc20ffe95125497ba4a6540daa135794d`, and `kerA`/`kerB` (`2,638,124` bytes each) share identical `0x25152c` and `0x283f2c` trailers.
2. **Omission of `perm` (`mtd11`) and `3rdw` (`mtd12`):** Neither `/perm` nor `/3rd_rw` appears inside `upgrade_loader.pkg`. Factory recovery explicitly preserves device-unique provisioning data on `perm` (HDCP keys, PlayReady keys, MAC/ESN credentials) and user-mutable application state on `3rdw`.

---

## 1.3 Embedded NAND Partition Map (`cfig`) and Storage Security Model

Partition #4 (`cfig`, `237` bytes at `0x0bfec0c8`) encodes the platform's logical-to-MTD binding table ([`evidence/01_pkg_and_nfsb_proof.txt`](../evidence/01_pkg_and_nfsb_proof.txt), lines 21–22):

```text
START
  uenv -> nand -> 1     kerA -> nand -> 4     kerB -> nand -> 5
  rfsA -> nand -> 6     rfsB -> nand -> 7     3rdA -> nand -> 9
  3rdB -> nand -> 10    perm -> nand -> 11    3rdw -> nand -> 12
  roda -> nand -> 13    game -> nand -> 14    pqda -> nand -> 17
  aqda -> nand -> 18    ddb  -> nand -> 26    chtC -> nand -> 27
  chtD -> nand -> 28    adsp -> nand -> 29    Seur -> nand -> 30
END
```

Combining `cfig` with the mount scripts inside `extracted/appfs1/etc/scripts/` (`evidence/07_dmbht_and_boot_scripts_audit.txt`) classifies every non-volatile MTD partition into four distinct trust/mutability tiers:

| Logical Name | MTD Node | Device / Mount Binding | Filesystem Type | Cryptographic Integrity | Write Mutability |
|---|---|---|---|---|---|
| `load` / `uenv` | `mtd0` / `mtd1` | Raw flash / U-Boot env | Raw binary | BootROM RSA-2048 (`eFuse 0xf0008664`) | Locked read-only |
| `kerA` / `kerB` | `mtd4` / `mtd5` | Booted by U-Boot (`0xd00000`) | `uImage` + TrustZone | Dual RSA-2048 (`0x25152c` & `0x283f2c`) | Locked read-only |
| `rfsA` / `rfsB` | `mtd6` / `mtd7` | Kernel `dm_mount_root_nfsb` -> `/` | SquashFS 4.0 | **`NFSB` RSA-1024 (`e=3`) + `dm-bht` MD5** | **Immutable RO** |
| `3rdA` / `3rdB` | `mtd9` / `mtd10` | `dmsetup create dm-1 --table "0 0 verity /dev/mtdblock{9,10}"` -> `/3rd` | SquashFS 4.0 | **`NFSB` RSA-1024 (`e=3`) + `dm-bht` MD5** | **Immutable RO** |
| `perm` | `mtd11` | `ubiattach -m 11 -d 2` -> `ubi2:perm` -> `/perm` | UBIFS (`no_chk_data_crc`) | None at block level (`drmkey` encrypted separately) | Critical vendor calibration (DO NOT wipe) |
| **`3rdw`** | **`mtd12`** | **`ubiattach -m 12 -d 4` -> `ubi4:3rd_rw` -> `/3rd_rw`** | **UBIFS (`no_chk_data_crc`)** | **None (`dm-verity` / `NFSB` absent)** | **Writable RW persistent target** |
| `roda` | `mtd13` | `ubiattach -m 13 -d 3` -> `mount -r ubi3:ro_data /ro_data` | UBIFS RO | Holds `/ro_data/key/TPV_MTK2K14PLF_*` | Mounted Read-Only (`-r`) |
| `game` | `mtd14` | `/dev/mtdsdm14` -> `/game` | Read-only SDM | Referenced by `dtv_svc` (`0x0360ac`) | Immutable RO |

The absence of `NFSB`/`dm-verity` on **`mtd12` (`ubi4:3rd_rw`)** paired with `dtv_svc`'s explicit `customer_version` provisioning guard (Section 1.4) provides the foundational architectural opening exploited constructively in Chapter 5.

---

## 1.4 Linux Startup Choreography, Mount Graph & Linker Resolution Semantics

Examining `extracted/appfs1/etc/rc.d/rc.local.partial`, `extracted/appfs1/etc/rc.d/rc.local`, `extracted/appfs1/basic/autorun.sh`, and the disassembled initialization routine `sys_start.c` inside `extracted/appfs1/basic/dtv_svc` (`0x035d18..0x036320`) yields the complete cold-boot sequence from `/sbin/init` through Smart TV browser spawn:

```mermaid
sequenceDiagram
    participant RC as /etc/rc.d/rc.local (+partial)
    participant Auto as /basic/autorun.sh
    participant DTV as /basic/dtv_svc (sys_start.c)
    participant SM as SystemManager (Qt 4.8.3)
    participant NetTV as libnettv.so (_imnettv_copydata)
    participant Opera as /usr/opera/browser.out

    RC->>RC: rc.local.partial: ttyMT3 115200, mkdir /tmp/mnt, 127.0.0.1 -> /tmp/hosts
    RC->>RC: insmod fusion.ko, dtv_driver_adpt.ko, dtv_driver.ko, ins_eth_mod, ins_wifi_mod
    RC->>RC: Check mtk_eep 0x2c20 / 0x2c25 -> ITM factory test gate (skipped on normal boot)
    RC->>Auto: Execute /basic/autorun.sh
    Auto->>Auto: L86: export LD_LIBRARY_PATH=...:/3rd/lib:/3rd/qt/lib:...
    Auto->>Auto: L99: export LD_PRELOAD=/basic/lib/preloadable_libiconv.so
    Auto->>Auto: L114-124: PATH+=/3rd_rw/nettv, LD_LIBRARY_PATH+=:/3rd_rw/nettv:/3rd/qt/qt_lib, LD_RRELOAD=(typo!)
    Auto->>DTV: Launch /basic/dtv_svc -input_fifo & ; /basic/tty_man (blocking foreground)
    DTV->>DTV: 0x035fbc: sh /etc/scripts/mount_perm.sh (ubiattach -m 11 -d 2 -> /perm)
    DTV->>DTV: 0x035f28 / 0x035d6c: sh /etc/scripts/mount_3rda.sh or 3rdb (dmsetup verity -> /3rd)
    DTV->>DTV: 0x036190: sh /etc/scripts/mount_3rd_rw.sh (ubiattach -m 12 -d 4 -> /3rd_rw)
    DTV->>DTV: 0x03628c: open("/3rd_rw/upgrade/customer_version")
    alt customer_version absent (factory fresh flash)
        DTV->>DTV: 0x0362a0..0x036300: rm -rf /3rd_rw/nettv/opera; mkdir -p; cp -rf /3rd/nettv/opera/*; sync; create customer_version
    else customer_version exists (normal TV state)
        DTV->>DTV: Branch 0x0363c0 -> Preserve /3rd_rw/nettv intact across reboots!
    end
    DTV->>DTV: 0x035e20..0x035f14: mount_ro_data.sh, mount_game.sh, ins_all_mod.sh, /3rd/bin/jsapp.run &
    DTV-->>SM: Spawn SystemManager (checks sm_config.ini -> dynqml==0 -> qrc:/HomeScreen/HSMain.qml)
    SM->>NetTV: User opens Browser / NetTV
    NetTV->>NetTV: 0x1889c4..0x188b54: ensure /mnt/browser/{ClientCert,opcacrt6}.*; cp /usr/opera/opera_home/* -> /tmp/opera_home/
    NetTV->>NetTV: 0x188c74: access("/3rd_rw/nettv/opera_new.ini") == 0
    NetTV->>NetTV: 0x188cb4..0x188cc0: cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync ; chmod 666
    NetTV->>Opera: Exec browser.out using /tmp/opera_home/opera.ini
```

### 1.4.1 Dynamic Linker Precedence & The `LD_RRELOAD` Defect in `autorun.sh`

Static inspection of `extracted/appfs1/basic/autorun.sh` (`evidence/07_dmbht_and_boot_scripts_audit.txt`, lines 170–239) exposes two architectural traps that defeat naive library-interposition attacks:

1. **Read-Only Directory Precedence in `LD_LIBRARY_PATH`:**
   When `ginga_tbr` is present (Brazilian/LATAM DTV SKU), line 86 overwrites `LD_LIBRARY_PATH` cleanly before `/3rd_rw` is appended:
   ```sh
   L086: export LD_LIBRARY_PATH=/basic/ginga/lib:/3rd/ginga/lib:/3rd/ginga/lib/ncl/ginga:...:/basic:/basic/lib:/3rd/lib:/3rd/qt/lib:...
   L115: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/3rd_rw/nettv:/3rd/qt/qt_lib
   L123: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/3rd/nettv:/basic/nettv
   ```
   Because GNU `ld-linux.so.3` resolves DT_NEEDED shared objects left-to-right across `LD_LIBRARY_PATH` (and because `SystemManager` also embeds `RPATH=/home/mtkvm/qtbuild/...` without overriding system paths ahead of line 86), any library residing in `/basic/lib`, `/3rd/lib`, or `/3rd/qt/lib` — such as `libssl.so.1.0.0`, `libcrypto.so.1.0.0`, `libcurl.so.4`, `libQtCore.so.4`, or `libdirectfb.so` — **always resolves to the SquashFS read-only copy before `/3rd_rw/nettv` is ever consulted**. Placing newer shared libraries into `/3rd_rw/nettv` cannot shadow existing `/basic` or `/3rd` libraries.
2. **Literal Vendor Typo `LD_RRELOAD` (Line 124):**
   Line 99 correctly exports `LD_PRELOAD=/basic/lib/preloadable_libiconv.so`, whereas line 124 attempts to force MediaTek's UVA backend via:
   ```sh
   L124: export LD_RRELOAD=/3rd/nettv/libuvabackend-tpvision.so
   ```
   The variable `LD_RRELOAD` is an unrecognized environment token ignored completely by GNU `ld.so`, illustrating why `browser.out` instead explicitly links `libuvabackend-tpvision.so` in its ELF `DT_NEEDED` table (`evidence/06_systemmanager_and_nettv_disasm.txt`, line 25).
3. **Unreachable `/3rd/run.sh` in `rc.local` Until Foreground Blocking Exits:**
   Inside `autorun.sh`, lines 148–149 launch `/basic/dtv_svc -input_fifo &` and then block synchronously on `/basic/tty_man` (line 149). Only if `/basic/tty_man` exits (and `/basic/app_man` is absent) does execution proceed past `autorun.sh` to `rc.local` line 197 (`if [ -f /3rd/run.sh ]; then sh /3rd/run.sh; fi`).

---

## 1.5 Dynamic Linkage Graph (`DT_NEEDED`) Across Core Firmware ELFs

Using our ELF32 parser in [`scripts/disasm_systemmanager_and_nettv.py`](../scripts/disasm_systemmanager_and_nettv.py) (`evidence/06_systemmanager_and_nettv_disasm.txt`, lines 1–46), we extract the exact shared-library dependency graph for all nine principal executables and subsystem libraries:

| Binary | ELF Type | Entry VA | `DT_NEEDED` Count | Distinguishing Dependencies |
|---|---|---:|---:|---|
| **`SystemManager`** | `ET_EXEC` | `0x00018d18` | `17` | `libQtDeclarative.so.4`, `libQtScript.so.4`, `libQtSql.so.4`, `libQtXml.so.4`, `libQtGui.so.4`, `libdirectfb.so`, `libQtNetwork.so.4`, `libQtCore.so.4` (ZERO `libcurl`/`libssl`/`libmtal`) |
| **`dtv_svc`** | `ET_EXEC` | `0x000329d8` | `41` | `libdtv_common.so`, `libmtkapp.so`, `libnettv_proxy.so`, `libginga_tbr_pic.so`, `libmtkdrm.so`, `libtommath.so`, `libtomcrypt.so`, `libhdcp2x.so`, `libwfd.so`, `libsecurestorage.so`, `libcmpb.so` |
| **`libnettv.so`** | `ET_DYN` | `0x000acc10` | `36` | `libSSPK.so`, `libmarlin.so`, `libplayready.so`, `libPRGlue.so`, `libWVPlaybackAPI.so`, `libWVStreamControlAPI.so`, `libuvabackend-mtk.so`, `libuvadrmbackend-{clearkey,playready}.so`, `libcurl.so.4`, `libssl.so.1.0.0` |
| **`libopera_hbbtv.so`** | `ET_DYN` (`soname`) | `0x000b3fa8` | `7` | `libpthread.so.0`, `libdl.so.2`, `libopera_hbbtv_appman.so`, `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6` (**self-contained statically embedded OpenSSL!**) |
| **`browser.out`** | `ET_EXEC` | `0x000118d0` | `20` | `libopera_hbbtv.so`, `libopera_hbbtv_appman.so`, `libuva.so`, `libuvabackend-{capi,tpvision}.so`, `libhtvLib.so`, `libTrace.so`, `libdirectfb.so` |
| **`netflix`** | `ET_EXEC` | `0x002355c8` | `31` | `libapp_client.so`, `libJavaScriptCore.so`, `libWTF.so`, `libmng.so.1`, `libwebp.so.4`, `libplayready.so`, `libssl.so.1.0.0`, `libcrypto.so.1.0.0`, `libcurl.so.4`, `libcmpb.so` |
| **`wrp_leanback`** | `ET_EXEC` | `0x00008bec` | `23` | `libapp_if.so`, `libdtv_common.so`, `libdirectfb.so`, `libcurl.so.4`, `libssl.so.1.0.0`, `libcrypto.so.1.0.0` |
| **`libmtkapp.so`** | `ET_DYN` | `0x001132f8` | `21` | `libdtv_common.so`, `libnettv_proxy.so`, `libsmartfs.so`, `libsecurestorage.so`, `libcmpb.so`, `libssl.so.1.0.0` |
| **`libdtv_common.so`** | `ET_DYN` | `0x0003b420` | `16` | `libcrypto.so.1.0.0`, `libssl.so.1.0.0`, `libcurl.so.4`, `libsmartfs.so`, `libsecurestorage.so`, `libdirectfb.so` |

Notice a crucial security and architectural contrast embedded directly in line 20 of [`evidence/06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt):
- **`netflix`** (`dtv_svc`, `libnettv.so`, `wrp_leanback`) dynamically imports `/basic/lib/libssl.so.1.0.0` and `/basic/lib/libcrypto.so.1.0.0` (OpenSSL `1.0.0d`, February 2011) alongside statically compiled OpenSSL symbols inside `netflix` (`evidence/05_runtime_engines_and_busybox_audit.txt`).
- **`libopera_hbbtv.so` (`15,717,224` bytes)** imports **only 7 core C/C++/appman libraries** and deliberately omits `libssl.so.1.0.0` and `libcrypto.so.1.0.0`, instead baking its own internal SSL/TLS `1.0`/`1.1`/`1.2` + `ECDH`/`ECDSA` cipher suite stack directly into its `~11.4 MB` `.text` segment (`0x000b3fa8` + `0xae21bc` bytes). Consequently, Opera is uniquely capable of speaking **`TLS 1.2`** despite the host root filesystem shipping OpenSSL `1.0.0d`.

---

## 1.6 Userland BusyBox & Binary Tooling Audit

An exhaustive inventory of `extracted/appfs1/bin` executed by [`scripts/inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py) (`evidence/05_runtime_engines_and_busybox_audit.txt`, lines 19–30) establishes the exact shell execution envelope available to any boot script or installer hook:

- **Present in `/bin` (`73` binaries/applets):**
  `agetty`, `arping`, `awk`, `basename`, `bash`, `blkid`, `blkid.static`, `busybox`, `cat`, `chmod`, `chrt`, `cp`, `date`, `depmod`, `df`, `dibbler-client`, `dirname`, `dmesg`, `dmsetup`, `du`, `echo`, `find`, `fw_printenv`, `getopt`, `grep`, `gzip`, `head`, `hostname`, `ifconfig`, `insmod`, `kill`, `ln`, `login`, `losetup`, `ls`, `lsmod`, `mkdir`, `mknod`, `modprobe`, `mount`, `mount.static`, `mountpoint`, `mv`, `nice`, `ping`, `ping6`, `ps`, `pwd`, `reboot`, `rm`, `rmmod`, `route`, `sed`, `sh`, `sleep`, `sort`, `stty`, `sync`, `sysctl`, `tar`, `top`, `touch`, `ubiattach`, `ubidetach`, `ubiformat`, `ubimkvol`, `ubinfo`, `udhcpc`, `umount`, `umount.static`, `vi`, `which`, `xargs`.
- **Supplementary Utilities in `/sbin` and `/usr/bin`:**
  `/sbin`: `autologin`, `bgm_interface.script`, `dhcpc.script`, `dns.script`, `getty`, `ifconfig`, `ifconfig.script`, `init`, `mnet_down.script`, `setmac`, `udhcpc`.
  `/usr/bin`: `cli`, `ldd`, `suspend.sh`, `usb_path`, `xml`.
- **Explicitly Verified Absent (`present=False` for all 10 checked tools):**
  - Process/priority tools: `pidof`, `pgrep`, `renice`, `ionice`, `killall`
  - Permission/decompression utilities: `chown`, `unzip` (`tar` and `gzip` are present; `unzip` is absent — directly explaining why `libmtkapp.so`'s `busybox unzip` branch is fatal outside `/ro_data/smarthome/`)
  - Scripting/HTTP clients: `python`, `python3`, `curl`

### Engineering Consequence for Payload Design

Any script intended to run natively on the AOC LE32S5760/20 must rely strictly on POSIX `sh` builtins, `awk`, `grep`, `sed`, `ps`, `kill`, and `tar`. Draft optimization scripts found in early community firmware mods routinely called `pidof`, `pgrep`, `renice`, `ionice`, `chown`, and `127.0.0.1:8888` Python proxies — all of which fail cleanly on `extracted/appfs1` because none of those executables were compiled into BusyBox `rfsA`/`rfsB`.
