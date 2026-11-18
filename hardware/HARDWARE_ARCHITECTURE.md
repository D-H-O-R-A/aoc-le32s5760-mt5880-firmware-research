# Hardware Architecture (`AOC LE32S5760/20` — `MediaTek MT5880` Platform)

> **Reference Diagram:** [diagrams/HARDWARE_ARCHITECTURE.svg](../diagrams/HARDWARE_ARCHITECTURE.svg) | **Component Matrix:** [HARDWARE_COMPONENT_INVENTORY.csv](HARDWARE_COMPONENT_INVENTORY.csv)

## 1. Epistemic Framework

Because this investigation proceeded strictly via static firmware analysis without invasive chassis teardown or external flash-programmer intervention (documented in [HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md)), hardware observations are classified strictly into three verification tiers:

1. **CONFIRMED:** Directly demonstrated by machine code, MMIO register constants, kernel driver paths, `.modinfo` metadata, or bootloader strings inside the official image (`LE32S5760_V2.011_V0.2.zip`).
2. **INFERRED:** Architectural parameters consistently deduced from driver capability tables, environment variables, or screen resolution assets without direct physical die inspection.
3. **UNKNOWN / UNVERIFIED:** Physical PCB silkscreen codes, exact soldered passive/IC part numbers, and board-level bus probing results unavailable without opening the chassis.

---

## 2. Core Silicon & Processing Complex

| Subsystem | Technical Specification | Evidence Anchor | Confidence |
|---|---|---|---|
| **Primary SoC** | MediaTek `MT5880` (`MT53xx`/`MT58xx` DTV family) | `extracted/uenv` (`board/mt5880`), `vmlinux.bin` (`mt5880`, `mt53xx_get_ic_version`), `dtv_driver.ko` paths | **CONFIRMED** |
| **Application CPU Architecture** | `ARMv7-A` SMP (`PREEMPT`), ARM32 + Thumb-2, VFPv3, `cache-l2x0` L2 controller, ARM GIC + PMU | Kernel `vermagic=3.0.13 SMP preempt mod_unload ARMv7`, `arch/arm/mm/cache-l2x0.c`, `arch/arm/common/gic.c`, `arch/arm/vfp/vfpmodule.c` | **CONFIRMED** |
| **Standby / Power Co-Processor** | Embedded `T8032` (8051 core) under PDWNC (`pdwnc_gpio6896.c`, `pdwnc_hw.c`) | Preloader strings `"Preloader T8032 ack !"`, `"T8032 NO ack!"`; `dtv_driver.ko` `pdwnc6896` | **CONFIRMED** |
| **Audio Signal Processor** | MediaTek Audio DSP (`adsp`) paired with `aqda` audio calibration tables | PKG chunks `adsp` (`1,272,368` B) & `aqda` (`131,216` B); `cfig` `nand 29`, `nand 18` | **CONFIRMED** |
| **Display & 2D/3D Subsystem** | MediaTek `mt53xx_fb` framebuffer (`mt53_fb.c`) + DirectFB 1.4.1 (`fusion.ko` IPC); `/3rd/Img_Sgx` directory exists **empty** (`pvrsrvctl` not shipped) | `dtv_driver.ko` path `mt53_fb.c`; `etc/scripts/ins_basic_mod.sh` template hook vs empty `extracted/rootfs1/Img_Sgx` | **CONFIRMED** |
| **Exact SoC Mask / Package Revision** | Package ballout & silicon stepping (`ES`/`MP`) | `mt53xx_get_ic_version` queried only at runtime | **UNKNOWN** |

---

## 3. Memory, Non-Volatile Storage & Cryptographic Engines

| Subsystem | Observed Architecture | Evidence Anchor | Confidence |
|---|---|---|---|
| **Main DRAM Bus** | Dual-channel DRAM controller (Channels A & B calibrated independently at cold boot) | Preloader `DRAM Channel A/B Calibration` routines; `uenv` symbol `global_kernel_dram_size` | **CONFIRMED** |
| **Installed DRAM Capacity** | ~`512 MB` unified main + A/V memory budget (typical for MT5880; unconfirmed via `/proc/meminfo` live shell) | `SystemManager` QML/Presto ceiling ([docs/04](../docs/04_systemmanager_qt_opera_presto_and_legacy_apps.md)); `global_kernel_dram_size` | **INFERRED** |
| **Primary Flash Controller** | Raw NAND Controller (`NFI`) with hardware AES & ECC (`mtk_nand.c`, `NAND_NFI_STA`, `NAND_AES_INIT`, `NAND_ECC_MODE`) | `vmlinux.bin` strings & paths `drivers/mtd/nand/mtk_nand.c` | **CONFIRMED** |
| **Secondary / EEPROM Driver** | `nor/eeprom_hw.c` and `nor/storage.c` present in `dtv_driver.ko` (manages boot bank metadata / TV NVM variables) | `dtv_driver.ko` embedded source paths; `libmtkapp.so` `_phm_upg_model_start_upgrade` | **CONFIRMED** |
| **Hardware Crypto & LZHS** | OTP eFuse MMIO (`0xf0008664 & 0x100000`), HW-LZHS block (`0xf00080b0`), kernel `crypto/mtk_crypto.c`, `libmtk_hw_decrypt.so` | Disassembly traces in `evidence/02_secure_boot_chain_disasm.txt` & `vmlinux.bin` | **CONFIRMED** |

---

## 4. Wired, Wireless, USB & Broadcast Peripherals

| Interface | Hardware / Driver Evidence | Notes & Limitations | Confidence |
|---|---|---|---|
| **10/100 Wired Ethernet** | `star_mac.ko` (`eth0`) loaded via `etc/scripts/ins_eth_mod.sh`; wake-on-LAN / net control via `mnet_down.script` | PHY IC model on PCB unverified without teardown | **CONFIRMED (MAC) / UNKNOWN (PHY IC)** |
| **Internal/USB Wi-Fi** | Ralink/MediaTek `rt5572sta.ko` + `rtnet5572sta.ko` + `rtutil5572sta.ko` (USB VID:PID aliases `148F:5572`, `043E:7A13`, `043E:7A32`, `2001:3C1A`) | Only the RT5572 3-module set is actually shipped under `appfs1/basic/wifi_ko` | **CONFIRMED** |
| **USB Host Controllers** | MTK USB HCD (`drivers/usb/host/mtk_hcd.c`, `mtk_qmu.c`, `mtk-hcd.ko`) + `xhci-hcd.ko`, `usb-storage.ko`, `usbhid.ko`, `usbserial.ko`, `pl2303.ko` | Physical port count requires visual chassis inspection | **CONFIRMED** |
| **IR Remote & Front Keys** | `ir6896/irrc_if.c` & `irrx_if.c` (`dtv_driver.ko`) + `gpio6896.c` / `pdwnc_gpio6896.c` | Controlled via T8032 standby domain for cold power-on | **CONFIRMED** |
| **DTV Demodulator / Tuner** | Brazilian ISDB-Tb (`Ginga` SBTVD middleware) + `dtv_driver.ko` `Philips_2K13_ODM_pdwnc_ext.c` | Specific silicon tuner IC part number not observable statically | **INFERRED (Region) / UNKNOWN (IC)** |
| **Debug Serial UART** | `ttyMT0` (`115200 8N1`), commented out in `etc/inittab`; `ttyUSB0` conditional script `usb_console.sh` | Physical header test-pad pinout unphotographed | **CONFIRMED (SW) / UNKNOWN (PCB Pads)** |

---

## 5. Summary of Physical Hardware Gaps

To promote the remaining `INFERRED` and `UNKNOWN` entries (`715G7904M` PCB silkscreen, exact mounted NAND IC among the 10 kernel-supported IDs, exact DRAM chip configuration, panel LVDS timing IC, and tuner IC) to `CONFIRMED`, visual photography and chip-marking capture per [HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md) are required.
