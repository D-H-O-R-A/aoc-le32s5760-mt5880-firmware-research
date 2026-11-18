# Chapter 7 — ELF32 Dynamic Linking Topology, Memory Segment Maps & Startup Script Forensics

**Scope:** Understanding why specific binary hooks succeed or fail on the MediaTek MT5880 (`AOC LE32S5760/20`) requires exact knowledge of ELF virtual memory layouts, `PT_DYNAMIC` dependencies (`DT_NEEDED`, `RPATH`), `LD_LIBRARY_PATH` search precedence, and Linux init scripts (`/etc/rc.d/rc.local*`, `/etc/scripts/*`, `/basic/autorun.sh`). This chapter compiles complete section-level telemetry across all nine audited firmware ELFs (`evidence/06_systemmanager_and_nettv_disasm.txt`) alongside an end-to-end trace of storage mount scripts and hardware test gates (`evidence/07_dmbht_and_boot_scripts_audit.txt`).

---

## 7.1 ELF32 Virtual Memory Segments, Sections & `RPATH` Architecture

All core userland binaries and libraries inspected across `/basic` (`appfs1`) and `/3rd` (`rootfs1`) are 32-bit little-endian ARM ELF (`EI_CLASS = ELFCLASS32`, `e_machine = EM_ARM`, `VFPv3` hard/softfp AAPCS). Because TPV stripped debug symbols (`.symtab`/`.strtab`) while retaining section headers (`e_shnum = 27..30`) and dynamic linking tables (`.dynsym`, `.dynamic`, `.got`), exact static section geometry and runtime relocations remain directly observable.

### 7.1.1 Consolidated Section Geometry Table (`evidence/06_systemmanager_and_nettv_disasm.txt`)

| Binary Name | Type (`e_type`) | File Size | Entry Point | `.text` Range (VA / Size) | `.rodata` Range | `.got` VA | `.data` + `.bss` Span |
|---|---|---:|---:|---|---|---:|---|
| **`SystemManager`** | `ET_EXEC` | `9,438,748 B` | `0x00018d18` | `0x018d18` (`0x22f348` B) | `0x248068` (`0x6436ac` B) | `0x90f3b8` | `0x910080..0x911598` |
| **`dtv_svc`** | `ET_EXEC` | `4,255,100 B` | `0x000329d8` | `0x0329d8` (`0x2fe7f0` B) | `0x3311d0` (`0x56b3c` B) | `0x411170` | `0x4138d0..0x4be610` |
| **`libnettv.so`** | `ET_DYN` | `2,749,744 B` | `0x000acc10` | `0x0acc10` (`0x181500` B) | `0x22e118` (`0x3afbe` B) | `0x29df80` | `0x2a31e8..0x347a30` |
| **`libopera_hbbtv.so`** | `ET_DYN` | `15,717,224 B` | `0x000b3fa8` | `0x0b3fa8` (`0xae21bc` B) | `0xb96170` (`0xb1af4` B) | `0xf039c0` | `0xf04888..0xf0af54` |
| **`browser.out`** | `ET_EXEC` | `803,228 B` | `0x000118d0` | `0x0118d0` (`0x848e8` B) | `0x0961c0` (`0x2d2cf` B) | `0x0d2878` | `0x0d2afc..0x0ddbc0` |
| **`netflix`** | `ET_EXEC` | `10,201,088 B` | `0x002355c8` | `0x2355c8` (`0x62a580` B) | `0x85fb50` (`0x411e8` B) | `0x9c5700` | `0x9c8f40..0x9cfcdc` |
| **`wrp_leanback`** | `ET_EXEC` | `17,740 B` | `0x00008bec` | `0x008bec` (`0x1d0c` B) | `0x00a900` (`0x0bf8` B) | `0x01379c` | `0x013820..0x013fcc` |
| **`libmtkapp.so`** | `ET_DYN` | `32,794,624 B` | `0x001132f8` | `0x1132f8` (`0x43aa84` B) | `0x54dd88` (`0x816ec` B) | `0x68aa74` | `0x696080..0x223b784` |
| **`libdtv_common.so`** | `ET_DYN` | `2,153,828 B` | `0x0003b420` | `0x03b420` (`0x148f28` B) | `0x184350` (`0x4963c` B) | `0x209eb0` | `0x20c5d0..0x270fd4` |

### 7.1.2 Notable Structural Anomalies Revealed by ELF Headers

1. **`SystemManager` `6.5 MB` Compiled-in QML Resource Blob (`.rodata`):**
   Even though `.text` of `SystemManager` measures only `~2.35 MB` (`0x22f348` B), `.rodata` spans **`6,567,596` bytes (`0x6436ac`)** because Qt's `rcc` compiler embeds the entire compressed QML tree, HomeScreen icons, strings, and PNG textures inside `.rodata` (`qrc:/HomeScreen/HSMain.qml`). Without modifying `/3rd/qt/AEDK/SystemManager/sm_config.ini` (`[tpvlib] dynqml=true`), Qt initializes UI execution exclusively out of this read-only `.rodata` resource array.
2. **`libmtkapp.so` `25.9 MB` Embedded Static Data Block (`.data` + `.bss`):**
   `libmtkapp.so` exhibits a `25,919,929`-byte `.data` section (`0x18b81b9` B) housing pre-baked UI bitmap assets, font tables, localization string banks, and upgrade controller structs (`_phm_upg_model_*`), while keeping `.text` modular at `4.43 MB`.
3. **PIC vs Non-PIC Addressing Across Shared Objects:**
   - `libmtkapp.so` and `libdtv_common.so` compile with `-fPIC`, computing literal pointers through `.got` base register `r4` (`GOT_libmtkapp = 0x68aa74`, `GOT_libdtv = 0x209eb0`) plus negative `.rodata` addends (`add rX, r4, rel`).
   - `dtv_svc` (`e_type = ET_EXEC`, GOT `0x411170`) also employs GOT-relative addressing (`r4 = 0x411170`) in startup modules (`sys_start.c @ 0x035d18..0x036320`).
   - Conversely, `libnettv.so` (`e_type = ET_DYN`) uses direct zero-based segment offsets inside `_imnettv_copydata` (`0x1889a0..0x188d20`), while `SystemManager`, `netflix`, and `browser.out` (`ET_EXEC`) load direct 32-bit absolute virtual addresses (`0x8000` load base).
4. **Build Host Environment Leak via `DT_RPATH`:**
   - `SystemManager`: `/home/mtkvm/qtbuild/osslibrary/451_vfp_ca9/qt-4.8.3-dfb1.4.1/lib` — confirms Qt `4.8.3`, DirectFB `1.4.1`, and ARMv7-A Cortex-A9 VFP GCC `4.5.1`.
   - `netflix`: `$ORIGIN:/release/auto/p4/w/20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/third_party/cust_app/TPV_Vision/TPV/mbtaudio:/release/auto/p4/w/20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/oss/library/gnuarm-4.5.1_vfp_ca9/c-ares/cares-1.7.4/lib:...` — pins exact Perforce build timestamp (`2015-04-20 19:49:32`) and `c-ares 1.7.4`.

---

## 7.2 Complete Shared Library Dependency Graph (`DT_NEEDED` Matrix)

Cross-tabulating `DT_NEEDED` across all nine ELFs (`evidence/06_systemmanager_and_nettv_disasm.txt`, lines 5–46) exposes strict architectural compartmentalization:

| Subsystem Library | `SystemManager` | `dtv_svc` | `libnettv.so` | `libopera_hbbtv.so` | `browser.out` | `netflix` | `wrp_leanback` | `libmtkapp.so` | `libdtv_common.so` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`libdirectfb.so`** (Display) | Yes | Yes | Yes | — | Yes | Yes | Yes | Yes | Yes |
| **`libQtCore/Gui/Declarative`** | Yes | — | — | — | — | — | — | — | — |
| **`libssl.so.1.0.0` / `libcrypto`** | — | Yes | Yes | *(Embedded)* | — | Yes | Yes | Yes | Yes |
| **`libcurl.so.4` / `libcares.so.2`** | — | Yes | Yes | — | — | Yes | Yes | Yes | Yes |
| **`libdtv_common.so`** (DLM/Platform) | — | Yes | Yes | — | — | Yes | Yes | Yes | — |
| **`libmtal.so` / `libcmpb.so`** (VPU) | — | Yes | Yes | — | — | Yes | Yes (`mtal`) | Yes | Yes (`mtal`) |
| **`libsecurestorage.so` / DRM** | — | Yes | Yes | — | — | Yes | Yes | Yes | Yes |
| **`libplayready.so` / Widevine** | — | — | Yes (+WV/Marlin) | — | — | Yes (`playready`) | — | — | — |
| **`libuva.so` / `libuvabackend-*`** | — | — | Yes (`-mtk`) | — | Yes (`-capi`, `-tpvision`) | — | — | — | — |
| **`libopera_hbbtv.so`** | — | — | — | — | Yes | — | — | — | — |
| **`libJavaScriptCore.so` / `libWTF.so`** | — | — | — | — | — | Yes | — | — | — |
| **`libginga_tbr_pic.so`** (SBTVD) | — | Yes | — | — | — | — | — | — | — |

Key architectural deductions directly visible from this dependency matrix:
1. **`libopera_hbbtv.so` TLS Independence:** Of all network-facing engines (`dtv_svc`, `libnettv.so`, `netflix`, `wrp_leanback`, `libmtkapp.so`), **only `libopera_hbbtv.so`** isolates itself from `/basic/lib/libssl.so.1.0.0` (`OpenSSL 1.0.0d`), allowing Opera to negotiate `TLS 1.1` and `TLS 1.2` while `netflix` remains locked at `TLS 1.0` max.
2. **Modular Player Split:** `netflix` bundles its own WebKit-derived `libJavaScriptCore.so` + `libWTF.so` runtime (`Gibbon`), whereas YouTube Legacy (`wrp_leanback`) depends purely on Flash StageCraft and links neither `libopera_hbbtv` nor `JavaScriptCore`.
3. **`browser.out` Media Bridge:** `browser.out` delegates DOM/JS/networking exclusively to `libopera_hbbtv.so`, rendering video `<video>` and MSE/DASH tags through `libuva.so` -> `libuvabackend-capi.so` -> `libuvabackend-tpvision.so` and outputting telemetry through `libTrace.so`.

---

## 7.3 Startup Script Forensics (`rc.local.partial`, `rc.local`, `autorun.sh`)

Combining the verbatim boot scripts extracted from `extracted/appfs1/etc/rc.d/` and `extracted/appfs1/basic/autorun.sh` reconstructs every conditional path traversed between kernel `init` and UI presentation.

### 7.3.1 Stage 1 — Early Tmpfs & Console Plumbing (`etc/rc.d/rc.local.partial`)

Run asynchronously in background (`sh /etc/rc.d/rc.local.partial &` at `rc.local` line 3), `rc.local.partial` (`19` lines, `evidence/07_dmbht_and_boot_scripts_audit.txt`, lines 21–33) configures:
- Serial baud rate: `stty -F /dev/ttyMT3 115200` (UART port `/dev/ttyMT3`)
- Volatile runtime directories: `/tmp/mnt`, `/tmp/lib/dibbler`, `/tmp/dibbler` (DHCPv6 client state)
- Resolver/host defaults: empty `/tmp/resolv.conf` and `"127.0.0.1 localhost.localdomain localhost" > /tmp/hosts`
- Loopback interface: `ifconfig lo 127.0.0.1`
- Kernel tuning parameters: `sysctl -p /etc/sysctl.conf`

Notice why `/tmp/hosts` is created fresh in RAM (`tmpfs`) on every boot: `/etc/hosts` symlinks to `/tmp/hosts`. Any persistent host-blocking script must append idempotently (`grep -q`) after boot rather than modifying read-only `/etc` inside `rfsA`.

### 7.3.2 Stage 2 — Driver Load, EEPROM ITM Factory Trap & Feature Flags (`etc/rc.d/rc.local`)

`rc.local` (`205` lines) coordinates conditional hardware initialization driven by `/etc/config/*` flag files, kernel `/proc/cmdline` tokens, and raw EEPROM bytes:

| `rc.local` Lines | Trigger / Check | Action Executed | Engineering Significance |
|---|---|---|---|
| `5–12` | `/etc/scripts/mount_main.sh` | Sets `BASIC_MOUNTED="yes"` | Ensures `/basic` (`appfs1`) availability |
| `17–25` | `! -f /etc/config/fastboot` | Loads `ins_usb_core_mod.sh` + `ins_usb_sub_mod.sh` | USB storage drivers preloaded when fastboot off |
| `27–37` | `/3rd/upgrade/download.xml` exists | Mounts `/perm` + `/3rd`, runs `/etc/checker.sh` | Factory/OTA recovery checker hook prior to app boot |
| `41–44` | `/etc/readahead` exists | `busybox readahead $(cat /etc/readahead) &` | I/O page-cache warm-up |
| `46` | Unconditional (if `BASIC_MOUNTED`) | `insmod /basic/fusion.ko` | DirectFB Fusion kernel IPC module (multi-app DFB) |
| `54–81` | `/etc/config/no_delay_mount_{3rd,perm}` | Controls whether `rc.local` mounts `/3rd` / `/perm` eagerly or delegates to `dtv_svc` | On stock TV, `DELAY_MOUNT_3RD="yes"` delegates mounting directly to `dtv_svc` (`sys_start.c`) |
| `92–133` | `/proc/cmdline` (`usb_launch` / `manual_launch` / `all_launch`) | Runs `usb_launch.sh` or `init_all.sh` when kernel cmdline requests factory test | Controlled by `uenv` / U-Boot `bootargs` |
| `136–158` | Normal boot | Inserts `dtv_driver_adpt.ko`, `dtv_driver.ko`, runs `ins_eth_mod.sh` and `ins_wifi_mod.sh` (if `/etc/config/wifi`) | Initializes SoC AV/demux/tuner and Ethernet/Wi-Fi |
| **`161–180`** | **`/basic/bin/mtk_eep` & `/basic/mitm`** | **Probes EEPROM byte `0x2c20 == 0x01` or `0x2c25 == 0x01`** | **Factory In-Circuit Test Mode (`mitm`): mounts `/3rd`, `/3rd_rw`, `/perm`, clears `0x2c25`, launches `/basic/mitm` and halts normal boot!** |
| `181–190` | Normal boot (`USB_LAUNCH=no`, `MANUAL_LAUNCH=no`) | Runs `sh /basic/autorun.sh` (falls back to `/basic/dtvap &`) | Transfers control to primary application launcher |
| `195–199` | Post-`autorun.sh` | `if [ -f /3rd/run.sh ]; then sh /3rd/run.sh; fi` | **Only reached if `autorun.sh` exits (blocked normally by `/basic/tty_man`)** |

### 7.3.3 Stage 3 — Environment Setup & Process Launch (`basic/autorun.sh`)

Key functional lines (`76..155`) verified in `evidence/07_dmbht_and_boot_scripts_audit.txt` (lines 170–239):

```sh
L076: echo "1 0 0 1920 1080" > /tmp/am_view_port
L084-087: Ginga TBR sets full LD_LIBRARY_PATH (lines 86: ...:/basic:/basic/lib:/3rd/lib:/3rd/qt/lib:...)
L090: export HOME=/3rd_rw            (later overwritten to HOME=/3rd at L103 for Skype/QT)
L099: export LD_PRELOAD=/basic/lib/preloadable_libiconv.so
L108: export QWS_DISPLAY=directfb
L114-115: PATH+=/3rd_rw/nettv ; LD_LIBRARY_PATH+=:/3rd_rw/nettv:/3rd/qt/qt_lib
L119-121: OPERA_DIR=/usr/opera/opera_dir ; OPERA_HOME=/usr/opera/opera_home ; OPERA_FONTS=/usr/opera/fonts
L124: export LD_RRELOAD=/3rd/nettv/libuvabackend-tpvision.so   # vendor typo!
L147-155: /basic/dtv_svc -input_fifo & ; /basic/tty_man
```

---

## 7.4 Partition Mount Script Forensics (`dmsetup` vs `ubiattach`)

Inspecting `etc/scripts/` (`evidence/07_dmbht_and_boot_scripts_audit.txt`, lines 34–169) highlights the sharp operational separation between cryptographic `dm-verity` SquashFS volumes and unverified UBIFS mounts:

1. **Read-Only Authenticated Banks (`dmverity_mount_3rda.sh` & `dmverity_mount_3rdb.sh`, lines 77–95):**
   ```sh
   dmsetup -r -j 254 -m 1 create dm-1 --table "0 0 verity /dev/mtdblock9"   # (or mtdblock10 for 3rdb)
   mount -t squashfs /dev/mapper/dm-1 /3rd
   ```
   - Major `254`, minor `1` creates `/dev/mapper/dm-1` read-only (`-r`).
   - Passing dummy zero geometry `"0 0 verity ..."` deliberately triggers `populate_table_nfsb` (`0xc022449c`) in the kernel to load `NFSB`, verify RSA-1024 against `N @ 0xc0429370`, compute true sector length `190,136` sectors, and instantiate `dm-bht` block verification before SquashFS can read its superblock.
   - Immediately after mounting `/3rd`, lines 90–95 spawn `/3rd/skype/auto_detect_camera.sh &` in background.

2. **Persistent Unverified Read-Write Volume (`ubi_mount_3rd_rw.sh`, lines 82–108):**
   ```sh
   ubiattach /dev/ubi_ctrl -m 12 -d 4
   mount -t ubifs -o no_chk_data_crc -o bulk_read ubi4:3rd_rw /3rd_rw
   ```
   - Attaches raw NAND MTD partition `12` (`3rdw` in `cfig`) as UBI device `ubi4` and mounts UBIFS volume `3rd_rw` cleanly read-write at `/3rd_rw`.
   - Uses `-o no_chk_data_crc -o bulk_read` for read latency optimization and **passes through zero Device Mapper or `NFSB` signature hooks**.

3. **Key Storage & Calibration Volumes (`ubi_mount_perm.sh` & `ubi_mount_ro_data.sh`):**
   - `ubi_mount_perm.sh`: `ubiattach -m 11 -d 2` -> `mount -rw -t ubifs -o no_chk_data_crc -o bulk_read ubi2:perm /perm` (note: always `-rw`, even when `/etc/config/usig_recovery` exists, though application DRM writes go through `libsecurestorage` / `libmtkdrm`).
   - `ubi_mount_ro_data.sh`: `ubiattach -m 13 -d 3` -> `mount -r -t ubifs -o no_chk_data_crc -o bulk_read ubi3:ro_data /ro_data` — strictly mounted read-only (`-r`) to protect `/ro_data/key/TPV_MTK2K14PLF_*` from accidental mutation.
