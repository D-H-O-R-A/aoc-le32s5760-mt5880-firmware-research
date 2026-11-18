# Hardware Architecture (`AOC LE32S5760/20` — `MediaTek MT5880` Platform)

> **Scalar Diagram:** [diagrams/HARDWARE_ARCHITECTURE.svg](../diagrams/HARDWARE_ARCHITECTURE.svg) | **Component Matrix:** [HARDWARE_COMPONENT_INVENTORY.csv](HARDWARE_COMPONENT_INVENTORY.csv)

## 1. Epistemic Classification Framework

Because physical chassis teardown and external flash-programmer intervention were deliberately excluded ([HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md)), every hardware attribute is graded strictly across three tiers:

1. **CONFIRMED:** Proven via machine code, MMIO literal pools, `.ARM.attributes`, ELF `DT_RPATH`, DWARF `.data` sections, kernel paths, or `.modinfo` metadata.
2. **INFERRED:** Architectural parameters consistently bounded by software telemetry (e.g., total physical DRAM size implied above the confirmed `543.7 MiB` kernel window).
3. **UNKNOWN / UNVERIFIED:** Bare-metal PCB silkscreen codes (`715G7904M`), soldered DDR3/NAND/T-Con/tuner part numbers, and live UART timing logs unavailable without disassembly.

---

## 2. Core Silicon & Processing Complex

| Subsystem | Verified Micro-Architecture / Specification | Primary Binary Evidence | Confidence |
|---|---|---|---|
| **Primary SoC** | MediaTek `MT5880` (`MT53xx`/`MT58xx` DTV family) | `uenv` (`board/mt5880`), `vmlinux.bin` (`mt53xx_*`), `dtv_driver.ko` (`5880_driver`) | **CONFIRMED** |
| **Application CPU Complex** | **ARM Cortex-A9 SMP (`ARMv7-A`) w/ VFPv3**, Thumb-2, **No `SDIV`/`UDIV`**, `L2x0`/`PL310` L2 cache, ARM `GIC` + `PMU` (`met.ko`) | `SystemManager` & `netflix` `DT_RPATH` (`451_vfp_ca9` / `gnuarm-4.5.1_vfp_ca9`); `uenv` `.ARM.attributes` (`Tag_CPU_name: 7-A`, `Tag_DIV_use: Not allowed`); `arch/arm/mm/cache-l2x0.c` | **CONFIRMED** |
| **Standby / Power MCU** | Embedded `T8032` (`8051` core) inside `PDWNC` domain | Preloader `"Preloader T8032 ack !"`; `pdwnc_gpio6896.c`; `dtv_driver.ko` `pdwnc_hw.c` | **CONFIRMED** |
| **Audio DSP** | MediaTek Audio DSP (`adsp` + `aqda`, Dolby `MS10`) | `upgrade_loader.pkg#part:adsp` (`1,272,368` B) & `aqda` (`131,216` B); `etc/profile` `AUD_DOLBY_SUPPORT=MS10` | **CONFIRMED** |
| **Display & Compositor** | MediaTek `mt53xx_fb` (`mt53_fb.c`) + DirectFB 1.4.1 (`fusion.ko`); `/3rd/Img_Sgx/` exists **empty** (`pvrsrvctl` omitted) | `dtv_driver.ko` `mt53_fb.c` + empty `/3rd/Img_Sgx` check vs `ins_basic_mod.sh` | **CONFIRMED** |

---

## 3. Memory, Non-Volatile Storage & Security Blocks

| Subsystem | Observed Architecture | Primary Evidence | Confidence |
|---|---|---|---|
| **System DRAM** | Dual-Channel DDR (Ch A & Ch B DQS calibrated); kernel window `0x21fb9000` (`543.72 MiB`) -> total physical DDR `>= 768 MiB / 1 GiB` *(supersedes earlier `~512 MB` estimate)* | Preloader `DRAM Channel A/B Calibration`, `0xf00046xx..48xx` literals; `uenv` `.data` (`global_kernel_dram_size = 0x21fb9000`) | **CONFIRMED (`543.7 MiB` Kernel) / INFERRED (Total IC)** |
| **Primary Flash Controller** | Raw NAND (`NFI` controller w/ HW ECC & NAND AES, `mtd0..mtd30`); `10` compiled Hynix/Micron/Samsung/Toshiba flash IDs | `drivers/mtd/nand/mtk_nand.c`, `NAND_NFI_STA`, `cfig` table | **CONFIRMED (Bus) / UNKNOWN (Soldered PN)** |
| **Auxiliary EEPROM / NOR** | `/dev/eeprom_0`, `/dev/eeprom_3`, `/dev/eeprom_4` + `nor/eeprom_hw.c` | `dtv_driver.ko` source/device strings + `libmtkapp.so @ 0x40ae80` | **CONFIRMED** |
| **OTP eFuse & Crypto** | Hardware eFuse (`0xf0008664 & 0x100000`), HW-LZHS (`0xf00080b0`), `crypto/mtk_crypto.c`, `TRUSTZONE=enable` | Preloader Capstone disassembly (`evidence/02`), `vmlinux.bin`, `/etc/profile` | **CONFIRMED** |

---

## 4. Network, USB, Tuner & Debug Interfaces

- **Wired Ethernet (`eth0`):** `star_mac.ko` (`ins_eth_mod.sh`) — MAC confirmed, board PHY IC requires teardown.
- **USB Wi-Fi (`ra0`):** Only the `3`-module Ralink/MediaTek `rt5572sta` stack is shipped (`appfs1/basic/wifi_ko`, USB VID:PID aliases `148F:5572`, `043E:7A13`, `043E:7A32`, `2001:3C1A`).
- **USB Host Controllers:** `mtk_hcd.c`, `mtk_qmu.c`, `xhci-hcd.ko`, `usb-storage`, `usbhid`, `ntfs.ko`, `fuse.ko`.
- **Debug UART:** Built-in kernel console `console=ttyMT0,115200n1` (`vmlinux.bin`), with `/sbin/getty ttyMT0` commented out in `appfs1/etc/inittab`.
- **Unverified Physical PCB:** `715G7904M` yields **`0` matches** in firmware (`MAINBOARD_ANALYSIS.md`); awaits visual teardown photos.
