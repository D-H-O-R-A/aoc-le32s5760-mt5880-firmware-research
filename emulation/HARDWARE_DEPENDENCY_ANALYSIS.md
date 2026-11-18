# Hardware Dependency Analysis for Firmware Re-Hosting

## 1. Classification of Firmware-to-Silicon Dependencies

To predict precisely which binaries fail outside physical `MT5880` silicon, observed components are grouped by their hardware coupling depth:

### Tier A — Absolute Silicon Locks (Hard Failure in Vanilla Emulation)
1. **`uboot.bin` Preloader (`0xfb000000`):**
   - Directly accesses physical SoC MMIO registers absent in generic ARM QEMU boards:
     - `0xf0008664` (`OTP eFuse` secure-boot lock word)
     - `0xf00080b0` (`HW-LZHS` compression accelerator registers)
     - `T8032` PDWNC SRAM/mailbox (`Preloader T8032 ack !`)
     - Dual-Channel DDR PHY registers (`DRAM Channel A/B Calibration`)
2. **`dtv_driver.ko` (`6,846,712` B) & `mtk_mmap.ko` (`3,220` B):**
   - Compiled against `vmlinux` `3.0.13` `mt53xx_*` exported symbols (`mt53xx_get_ic_version`, `mt53xx_get_reserved_area`, `mt53xx_bim_lock`).
   - Encapsulates direct register access (`mt53_fb.c`, `pdwnc_hw.c`, `irrc_if.c`, `nor/eeprom_hw.c`) and MediaTek BIM interrupt hardware.
3. **`vmlinux.bin` `dm_mount_root_nfsb` & `mtk_nand.c`:**
   - Expects specific NFI NAND controller IDs (`ExNID`) and raw `NFSB`-prefixed `/dev/mtdblock6` at early mount.

### Tier B — Conditional / Stubbable Dependencies (Recoverable With `LD_PRELOAD` or Config)
1. **`dtv_svc` (`4.25 MB`) & `libmtkapp.so` (`32.8 MB`):**
   - Requires `/dev/fb*` (DirectFB), `fusion.ko` (`/dev/fusion/*` IPC), `mtk_mmap`, and `dtv_driver.ko` RPC endpoints (`librpc_ipc.so`). However, standalone helper functions (`sub_404f28` path formatting, `dlm` container decryption in `libdtv_common.so`) do not touch MMIO if invoked directly via harness under `qemu-arm-static`.
2. **`SystemManager` (`Qt 4.8.3`):**
   - Depends on DirectFB `libdirectfb-1.4.so.0` + `libqtedkcommon.so` (`dtv_svc` IPC) and `/3rd/qt/AEDK/SystemManager` QML resources (`HSMain.qml`). QML syntax/layout evaluation can be isolated using stock Qt 4.8 QML viewers if OEM C++ plugin bindings are mocked.

### Tier C — Hardware-Independent Pure Userland Targets
- `busybox` (`v1.15.3`), `openssl`, `libxml2 2.7.8`, `expat 2.0.1`, `sqlite 3.7.2`, `libpng`, `zlib`, `dialserver` (network HTTP logic only), and static browser assets (`opera_new.ini`, `user.js`, `urlfilter.ini`).
