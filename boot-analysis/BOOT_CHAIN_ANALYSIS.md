# Boot Chain Analysis (`MT5880` Mask BootROM -> `SystemManager`)

> **Visual Diagram:** [diagrams/BOOT_CHAIN.svg](../diagrams/BOOT_CHAIN.svg) | **Primary Trace Log:** [evidence/02_secure_boot_chain_disasm.txt](../evidence/02_secure_boot_chain_disasm.txt)

## 1. End-to-End Boot Stage Reconstruction

Every stage below documents the binary evidence, verified memory addresses/offsets, upstream dependencies, related files, and epistemic confidence.

| Stage | Subsystem | Binary Evidence & Addresses | Dependencies | Related Artifacts | Confidence |
|---|---|---|---|---|---|
| **1. Hardware Power-On & Standby Handshake** | T8032 8051 MCU + Mask BootROM (`NANDBOOT/V01.00`) | Preloader checks `T8032 ack!` / `T8032 NO ack!` & reads OTP eFuse MMIO `0xf0008664`; BootROM banner `"MTK/DTV/ROMCODE/NANDBOOT/V01.00"` | Power supply rails, crystal clock, OTP fuses | `extracted/uboot.bin[:0xa040]`, `dtv_driver.ko` (`pdwnc_hw.c`) | **CONFIRMED** |
| **2. Primary SRAM Preloader** | Thumb-2 SRAM init (`0xfb000000`) | Entry `Start Pmain` inside `uboot.bin[0x0000:0xa040]`; Extended NAND ID detection `ExNID=0x00001676/00000004/00000056` | Mask BootROM loading first NAND blocks into internal SRAM | `extracted/uboot.bin` | **CONFIRMED** |
| **3. DRAM Calibration & HW-LZHS Setup** | Dual-Channel DDR PHY Init | `DRAM Channel A/B Calibration`; configures HW-LZHS decoder block `0xf00080b0` | Preloader SRAM execution | `extracted/uboot.bin`, `extracted/uenv` (`global_kernel_dram_size`) | **CONFIRMED** |
| **4. Bootloader Authentication & Execution** | Secure-Boot U-Boot Verification + ARM32 U-Boot | `0xfb001450..0xfb00147e` checks eFuse bit 20 (`0xf0008664 & 0x100000`), SW flag `[0xfb0053bc] == 1`, calls BootROM RSA `0xfb0034f0` on `+0x6c4b0` trailer; U-Boot at `+0xa040` | Valid RSA-2048 signature matching OTP public key hash | `extracted/uboot.bin`, `evidence/02_secure_boot_chain_disasm.txt` | **CONFIRMED** |
| **5. Kernel Authentication & Loading** | U-Boot -> `kerA`/`kerB` (`mtd4`/`mtd5`) + HW-LZHS | U-Boot loads `uImage` (`IH_MAGIC=0x27051956`, `load=0x00007fc0`, `ep=0x00008000`); dual RSA-2048 trailers at `0x25152c` and `0x283f2c`; `vmlinux` VA `0xc0008000` | Bank flag in EEPROM/uenv (`nor/eeprom_hw.c`) | `upgrade_loader.pkg#kerA/kerB`, `scratch/vmlinux.bin` | **CONFIRMED** |
| **6. Root & Application Filesystem Mounts** | `dm_mount_root_nfsb` + `BusyBox` / `etc/scripts/*` | Kernel `0xc0009594` + `populate_table_nfsb @ 0xc02243c4` + `nfsb_rsa_check @ 0xc0028df8` verify `rfsA/B` (`mtd6/7`) & `3rdA/B` (`mtd9/10`) via RSA-1024 (`e=3`) + `dm-bht` MD5; `rc.local` mounts `ubi2:perm` (`mtd11`), `ubi3:ro_data` (`mtd13`), `ubi4:3rd_rw` (`mtd12`) | Valid RSA-1024 NFSB header + all `36,281` `dm-bht` blocks | `vmlinux.bin`, `appfs1/etc/scripts/{dmverity,ubi}_mount_*.sh`, `evidence/01` & `07` | **CONFIRMED** |
| **7. Driver & Service Initialization** | `/sbin/init` -> `/etc/init.d/rcS` -> `/etc/rc.d/rc.local` -> `dtv_svc` | `inittab` runs `rcS` + spawns `mnet_down.script`; `ins_drv.sh` / `ins_basic_mod.sh` load 12 `.ko` modules; `dtv_svc` (`4,255,100` B) initializes `/3rd_rw/nettv` preserving `customer_version` | Mounted `/basic`, `/3rd`, `/3rd_rw`, `/perm`, `/ro_data` | `appfs1/etc/inittab`, `etc/init.d/rcS`, `etc/rc.d/rc.local`, `basic/dtv_svc` | **CONFIRMED** |
| **8. TV UI & Browser Launch** | `SystemManager` (`Qt 4.8.3`) + `Opera Presto 6213` | `SystemManager` loads `HSMain.qml` (optional `SMConfig` `dynqml` gate at `0x1db58c`); `libnettv.so` (`_imnettv_copydata @ 0x1889a0`) merges `/3rd_rw/nettv/opera_new.ini` -> `/tmp/opera_home/opera.ini` | `dtv_svc` IPC (`librpc_ipc.so`), DirectFB `fusion.ko` | `rootfs1/bin/SystemManager`, `rootfs1/nettv/libnettv.so`, `evidence/06` | **CONFIRMED** |

---

## 2. Chain-of-Trust Failure Modes Observed

1. **Stage 4 Trap (`0xfb00052a..0xfb000530`):** Any mismatch in Preloader RSA-2048 validation jumps to `ldr r0, ="not secure loader\n"`, prints over UART, and spins indefinitely (`0xfb000520: b #0xfb000520`).
2. **Stage 5 Gate (`kerA`/`kerB`):** Unsigned kernel modification invalidates the dual 512-byte `[RSA-2048 sig + cert]` trailers before `vmlinux` decompression.
3. **Stage 6 Block I/O Error (`dm-bht`):** Modifying even 1 bit in any of the `23,767` blocks in `3rdA` (`97.7` MB) or `12,514` blocks in `rfsA` (`51.4` MB) breaks the 2-level MD5 Merkle root checked against $S^3 \bmod N \stackrel{!}{=} \texttt{0}^{96} \parallel \text{SHA-256}$, causing `dm-verity` to fail block reads at boot (`build/custom_upgrade_loader.pkg` counter-proof: `RSA_exact_match=False`).
4. **Live Hardware Gap:** Because UART `ttyMT0` is commented out in `/etc/inittab` and no physical UART adapter log was captured on the unit during cold boot, exact console millisecond timings between `T8032 ack!` and Qt startup remain **UNCAPTURED**.
