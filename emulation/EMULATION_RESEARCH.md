# Firmware Emulation & Re-Hosting Research (`MediaTek MT5880`)

> **Honest Scope Disclosure:** In strict compliance with scientific reporting standards, no simulated or fabricated QEMU runtime traces are presented. Neither user-mode `qemu-arm-static` nor full-system `qemu-system-arm` execution of `LE32S5760_V2.011_V0.2` was performed in this offline workspace (and `qemu-arm` is absent from the sandbox environment). This study analyzes **architectural re-hosting barriers** grounded directly in the target binaries and Wright et al. (*ACM CSUR*, 2021) / Chen et al. (`Firmadyne`, *NDSS*, 2016).

---

## 1. Taxonomy of Re-Hosting Barriers on `MT5880`

Comparing `LE32S5760_V2.011_V0.2` against standard router/Linux embedded targets highlights why naive generic re-hosting (`Firmadyne` / vanilla `qemu-system-arm -M versatilepb`) fails immediately across three boundaries:

| Layer | Re-Hosting Blocker | Concrete Evidence in Target Binaries | Feasibility Assessment |
|---|---|---|---|
| **Preloader / U-Boot (`load`)** | **SoC-Specific MMIO Polling & Co-Processor Lockstep:** Reads hardware OTP eFuse `0xf0008664`, polls HW-LZHS engine `0xf00080b0`, waits for 8051 co-processor `"Preloader T8032 ack !"`, runs proprietary DRAM Channel A/B calibration (`0xfb000000`) | `extracted/uboot.bin`, `evidence/02_secure_boot_chain_disasm.txt` | **Full-System Unfeasible Without Custom SoC Machine Model** (QEMU lacks MT5880 NFI/LZHS/T8032/eFuse peripherals) |
| **Linux Kernel (`vmlinux.bin`)** | **Custom `mach-mt53xx` Machine ID & In-Kernel `NFSB` Verity Root:** Requires MediaTek machine type, custom `mtk_nand.c`, `mtk_crypto.c`, and expects `NFSB`-signed `dm_mount_root_nfsb` blocks on `/dev/mtdblock6` | `scratch/vmlinux.bin` (`381` paths, `0xc0009594`) | **Blocked Under Generic Kernel Substitution Unless Custom Kernel Rebuilt** (`v3.0.13` ARM EABI) |
| **Core Middleware (`dtv_svc`, `libmtkapp.so`)** | **Monolithic `dtv_driver.ko` IOCTL & `mt53_fb` Dependency:** `6.84 MB` `Proprietary` `.ko` + `mtk_mmap.ko` + `fusion.ko` (`/dev/fb*`, `/dev/fusion*`, NFI/PDWNC registers) | `dtv_driver.ko`, `KERNEL_MODULE_INVENTORY.csv` | **Requires Peripheral Stubbing (`LD_PRELOAD` / Kernel Proxy)** |
| **Isolated CLI Userland Tools (`busybox`, `libdtv_common.so` Leaf Functions)** | Standard `glibc 2.12.2` / ARMv7 EABI syscalls only (aside from `/ro_data` & `/dev/mtd*` opens) | `ld-2.12.2.so`, `libc-2.12.2.so`, `gcc 4.5.1` | **Feasible via User-Mode Chroot (`qemu-arm-static` + fake `/ro_data` & `/dev/mtd*` files)** |

---

## 2. Recommended Future Hybrid Re-Hosting Strategy

1. **Tier 1 (High ROI — User-Mode `qemu-arm-static` + `LD_PRELOAD`):** Target isolated binaries (`libdtv_common.so` DLM routines, `dialserver`, `opera` parser harnesses) under a standard ARMv7 EABI `qemu-arm-static -L extracted/appfs1` sysroot with mocked `/ro_data` and `ioctl()` return stubs.
2. **Tier 2 (Partial System Kernel Substitution):** Boot a generic ARMv7 mainline-compatible `3.x` QEMU kernel (`vexpress-a9`) mounting the **stripped SquashFS rootfs** (`rfsA`/`3rdA` after `0xe7` `NFSB` header removal) strictly for shell-script, `init`, and non-MMIO IPC inspection — recognizing `dtv_svc` and DirectFB `SystemManager` will abort when probing missing `dtv_driver.ko` hardware devices (see [HARDWARE_DEPENDENCY_ANALYSIS.md](HARDWARE_DEPENDENCY_ANALYSIS.md)).
