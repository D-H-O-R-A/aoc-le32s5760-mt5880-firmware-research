# SoC Analysis — MediaTek MT5880 (`MT53xx` / `TPV MTK2K14PLF`)

## 1. Silicon Identification & Family Provenance

Static inspection across boot, kernel, and proprietary driver binaries establishes the target System-on-Chip as the **MediaTek `MT5880`** DTV SoC, built within MediaTek's unified `arch/arm/mach-mt53xx` Linux BSP lineage (`6896`/`5880` register & GPIO architecture):

| Indicator | Exact Artifact & String / Symbol | Interpretation | Confidence |
|---|---|---|---|
| Kernel Source Tree | `/share/Release_code_use/Roy/release/vm_linux/chiling/kernel/linux-3.0/arch/arm/mach-mt53xx/{gpio6896.c, pdwnc_gpio6896.c}` | MT53xx shared ARM machine layer paired with 6896/MT5880 GPIO & PDWNC blocks | **CONFIRMED** |
| Proprietary Driver | `/share/Release_code_use/Roy/release/vm_linux/chiling/driver/ko/mt5880/5880_driver/...` (`dtv_driver.ko`, `6,846,712` B) | Dedicated MT5880 kernel driver tree (`chiling` / `Roy`) | **CONFIRMED** |
| U-Boot Environment Object | `extracted/uenv` (`2,384` B unstripped ARM ELF `.o`, `chiling/uboot/board/mt5880/env.c`) | Board target literally named `mt5880` | **CONFIRMED** |
| Kernel Board APIs | `mt53xx_get_ic_version`, `mt53xx_get_reserved_area`, `mt53xx_get_rodata_addr`, `mt53xx_get_rwdata_addr`, `mt53xx_timer_read`, `mt53xx_bim_lock` | SoC hardware abstraction helpers in `vmlinux.bin` | **CONFIRMED** |
| Module `vermagic` | `3.0.13 SMP preempt mod_unload ARMv7` (all 12 `.ko` files) | Multi-core SMP ARMv7-A processor core | **CONFIRMED** |
| Exact Stepping (`IC Version`) | Returned dynamically by `mt53xx_get_ic_version()` at runtime | Not statically readable from offline flash dump alone | **UNKNOWN** |

---

## 2. Internal Core & Bus Architecture

```
+-----------------------------------------------------------------------------+
|                         MediaTek MT5880 DTV SoC                             |
|                                                                             |
|  +------------------------------+    +-----------------------------------+  |
|  | ARMv7-A SMP Application Core |    | On-Chip SRAM & BootROM            |  |
|  |  - ARM32 + Thumb-2 + VFPv3   |    |  - Mask BootROM (NANDBOOT/V01.00) |  |
|  |  - PL310 / L2x0 Cache Ctrl   |    |  - Preloader SRAM base 0xfb000000 |  |
|  |  - ARM GIC + PMU (met.ko)    |    |  - OTP eFuse MMIO @ 0xf0008664    |  |
|  +--------------+---------------+    +-----------------+-----------------+  |
|                 |                                      |                    |
|  +--------------v--------------------------------------v-----------------+  |
|  |        System Fabric / BIM Lock (mt53xx_bim_lock) & MMIO Bus          |  |
|  +--+------------+------------+------------+------------+------------+---+  |
|     |            |            |            |            |            |      |
|  +--v---+   +----v----+  +----v-----+ +----v----+  +----v----+  +----v---+  |
|  |T8032 |   |HW-LZHS  |  |mtk_crypto| |NFI NAND |  |Dual-Ch  |  |USB HCD |  |
|  |8051  |   |0xf00080 |  |TrustZone | |& NOR/EE |  |DRAM Ctrl|  |MTK_HCD |  |
|  |PDWNC |   |b0 Decod.|  |Engine    | |Ctrl     |  |Ch A & B |  |& xHCI  |  |
|  +------+   +---------+  +----------+ +---------+  +---------+  +--------+  |
+-----------------------------------------------------------------------------+
```

### 2.1 ARMv7-A Application Complex
- **SMP PREEMPT:** Compiled with `SMP`, `PREEMPT`, and `ARMv7` (`HIGHMEM` enabled per `arch/arm/mm/highmem.c` + `mmu.c`).
- **L2 Cache & Coprocessors:** `arch/arm/mm/cache-l2x0.c` confirms an external L2 cache controller (PL310-compatible `l2x0`); `arch/arm/vfp/vfpmodule.c` confirms hardware VFP floating-point support; `met.ko` (`MET PMU Sampler`) exposes ARM PMU hardware performance counters.
- **Note on `/3rd/Img_Sgx`:** While `/etc/scripts/ins_basic_mod.sh` retains a template hook probing `/3rd/Img_Sgx/pvrsrvctl --start`, `extracted/rootfs1/Img_Sgx/` is empty and no PowerVR SGX binaries ship in this SKU; display rendering uses MediaTek's proprietary framebuffer (`mt53_fb.c`) and DirectFB 1.4.1 (`fusion.ko`).

### 2.2 T8032 (8051) PDWNC Standby Microcontroller
- During cold boot, the Thumb-2 Preloader explicitly handshakes with an embedded 8051-class **T8032** microcontroller (`"Preloader T8032 ack !"`, `"T8032 NO ack!"`).
- Paired with kernel `pdwnc_gpio6896.c` and driver `pdwnc6896/pdwnc_hw.c` plus `ir6896/{irrc_if.c, irrx_if.c}`, the T8032 remains powered in deep standby to service infrared remote wakeups (`IRRX`), front-panel buttons, and power rails before lifting reset on the main ARMv7 complex.

### 2.3 Security, TrustZone & Hardware Acceleration Blocks
1. **OTP eFuse Security Register (`0xf0008664`):** Read directly by Preloader at VA `0xfb001450..0xfb00145a` (`tst.w r3, #0x100000`). Bit 20 permanently locks retail silicon to verified boot.
2. **Hardware LZHS Engine (`0xf00080b0`):** Dedicated decompression IP core invoked by the Preloader (`uboot.bin`) to expand LZHS-compressed U-Boot and Linux kernel payloads.
3. **ARM TrustZone & `mtk_crypto`:** `/etc/profile` sets `export TRUSTZONE=enable`, `vmlinux.bin` embeds `crypto/mtk_crypto.c`, and rootfs ships `/lib/libmtk_hw_decrypt.so` (`36,492` B) supporting hardware-backed key ladder / PlayReady / Widevine operations. Note: Specific Secure World SMC call numbers inside TZ OS reside in OTP/BootROM/encrypted TZ memory not exported cleanly as an unstripped ELF.

### 2.4 Integrated I/O & Peripheral Controllers
- **Audio DSP (`adsp` / `aqda`):** Dedicated `adsp` (`1,272,368` B) and `aqda` (`131,216` B) partitions confirm an offloaded DSP handling multichannel decode and Dolby `MS10` (`AUD_DOLBY_SUPPORT=MS10`).
- **MediaTek Star MAC (`star_mac.ko`):** Integrated Ethernet MAC controller exposed as `eth0`.
- **USB 2.0/3.0 Host Controllers (`mtk_hcd.c`, `mtk_qmu.c`, `xhci-hcd.ko`):** USB host fabric with Queue Management Unit (`QMU`) servicing external storage (`usb-storage.ko`) and Wi-Fi dongles (`rt5572sta.ko`).
- **NAND Flash Interface (`mtk_nand.c`, `NAND_NFI_STA`):** Dedicated NFI block with hardware ECC (`NAND_ECC_MODE`) and inline NAND AES hooks (`NAND_AES_INIT`).
