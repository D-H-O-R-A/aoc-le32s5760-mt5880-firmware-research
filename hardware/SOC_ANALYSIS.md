# SoC Micro-Architecture Analysis — MediaTek MT5880 (`ARM Cortex-A9 SMP`)

## 1. Silicon & CPU Core Identification (With Compiler & ELF Evidence)

Beyond generic `ARMv7-A` identification (`vermagic=3.0.13 SMP preempt mod_unload ARMv7`), cross-correlating `ELF DT_RPATH`, `.ARM.attributes`, `uenv` DWARF debug info, and `vmlinux.bin` strings pins down the exact CPU micro-architecture targeted by the OEM toolchain:

| Silicon Attribute | Empirically Verified Evidence | Exact Source Artifact | Confidence |
|---|---|---|---|
| **SoC Family / Part** | MediaTek `MT5880` (`arch/arm/mach-mt53xx`, `6896` PDWNC/GPIO register generation) | `vmlinux.bin`, `uenv` (`board/mt5880`), `dtv_driver.ko` (`5880_driver`) | **CONFIRMED** |
| **CPU Core Micro-Architecture** | **ARM Cortex-A9 SMP + VFP** (`ca9`, without ARMv7-A `SDIV`/`UDIV` integer divide hardware instructions) | `SystemManager` `DT_RPATH`: `/home/mtkvm/qtbuild/osslibrary/451_vfp_ca9/...`; `netflix` `DT_RPATH`: `.../gnuarm-4.5.1_vfp_ca9/...`; `uenv` `.ARM.attributes` `Tag_DIV_use: Not allowed` | **CONFIRMED** |
| **ABI & Instruction Set Mix** | `Version5 EABI`, ARM32 + Thumb-2 (`Tag_ARM_ISA_use: Yes`, `Tag_THUMB_ISA_use: Thumb-2`), IEEE 754 VFP (`Tag_ABI_FP_number_model: IEEE 754`), 8-byte stack alignment | `readelf -A uenv` + `readelf -h` across `17` ELF binaries (`Flags: 0x5000002`) | **CONFIRMED** |
| **L2 Cache Controller** | PrimeCell L2x0 / PL310-compatible outer cache | `vmlinux.bin`: `arch/arm/mm/cache-l2x0.c` | **CONFIRMED** |
| **Interrupt & Performance Hardware** | ARM Generic Interrupt Controller (`GIC`) & ARM PMU (`met.ko` `MET PMU Sampler`) | `vmlinux.bin`: `arch/arm/common/gic.c`, `arch/arm/kernel/pmu.c`, `met.ko` | **CONFIRMED** |
| **Standby MCU** | Embedded `T8032` (`8051` core) inside `PDWNC` (`pdwnc6896`) domain | Preloader `"Preloader T8032 ack !"`, `"T8032 NO ack!"`, `dtv_driver.ko` `pdwnc_hw.c` | **CONFIRMED** |
| **Display Compositor** | `mt53xx_fb` (`mt53_fb.c`) + DirectFB 1.4.1 (`fusion.ko` IPC); `/3rd/Img_Sgx/` directory is **empty** (`pvrsrvctl` absent) | `dtv_driver.ko` paths + empty dir verification | **CONFIRMED** |
| **Silicon Stepping (`IC Version`)** | Queried via SoC register helper `mt53xx_get_ic_version()` at runtime | Symbol compiled into `vmlinux.bin` (runtime value requires live shell/UART) | **UNKNOWN** |

---

## 2. Preloader-Exposed SoC MMIO Register Banks (`uboot.bin[:0xa040]`)

Extracting unique `32`-bit little-endian literal-pool MMIO addresses directly from the Thumb-2 Preloader (`0x0000..0xa040`) maps the low-level SoC register apertures active before Linux boots (`0xf0000000` peripheral window, `0xfb000000` SRAM execution window):

| MMIO Aperture Range | Observed Register Literals in Preloader | Identified Subsystem / Evidence |
|---|---|---|
| `0xf0002000 – 0xf0002c02` | `0xf0002000`, `0xf0002064`, `0xf0002201..0xf00022ff`, `0xf000280a`, `0xf0002c02` | Preloader early clock / NFI / NAND pinmux & bus init (**exact bit definitions in closed MTK datasheet**) |
| `0xf0004020 – 0xf00048f5` | `0xf0004620`, `0xf000466c`, `0xf000482c..0xf00048f5` | **Dual-Channel DDR3 PHY / DQS Calibration** (`"DRAM Channel A/B Calibration"`, `"DRAM Input DQS Calibration fail !"`) |
| `0xf0005224 – 0xf0007240` | `0xf0005224`, `0xf0005280`, `0xf0006101`, `0xf0007000`, `0xf0007240` | DDR Channel B / BIM system arbiter timing registers |
| **`0xf0008000 – 0xf00081d0`** | `0xf0008000..0xf0008078`, **`0xf00080b0`**, `0xf00080b4..0xf00081d0` | **BIM & HW-LZHS Hardware Decompression Engine** (`0xf00080b0` verified via Capstone trace) |
| **`0xf0008664` (`& 0x100000`)** | `0xf00084dc`, **`0xf0008664`**, `0xf0008670`, `0xf00087b0`, `0xf0008f00..0c` | **OTP Silicon eFuse & Secure-Boot Configuration** (`bit 20 == 1` enforces mandatory RSA check) |
| `0xf000b510 – 0xf000d094` | `0xf000b510`, `0xf000c000..0xf000c388`, `0xf000d000..0xf000d094` | Serial / PDWNC / T8032 mailbox (`UART0` `ttyMT0` @ `115200n1`) |

---

## 3. Cross-Kernel Hardware Interfaces Exported by `vmlinux.bin` & `dtv_driver.ko`

Inspection of `vmlinux.bin` identifies all **`7` explicit `mt53xx_*` BSP primitives**:
1. `mt53xx_bim_lock` — Bus Interface Module atomic spinlock arbiter across shared CPU/DSP/DMAs.
2. `mt53xx_get_ic_version` — Silicon mask revision query.
3. `mt53xx_get_reserved_area` — Carveout boundary locator separating Linux lowmem/highmem from A/V framebuffers & TrustZone memory.
4. `mt53xx_get_rodata_addr` & `mt53xx_get_rwdata_addr` — Memory-mapped lookup hooks locating factory read-only (`ro_data`) and persistent read-write metadata.
5. `mt53xx_timer_read` & `mt53xx_timer_read_ll` — High-resolution BIM hardware timer counters.

Meanwhile, `dtv_driver.ko` (`6,846,712` B) binds directly to `/dev/eeprom_0`, `/dev/eeprom_3`, and `/dev/eeprom_4` for I2C/SPI NVM access (`nor/eeprom_hw.c`, `nor/storage.c`), IR reception (`ir6896`), T8032 standby (`pdwnc6896`), and LCD panel scanout (`mt53_fb.c`). Note also MediaTek cross-product SDK reuse evidenced inside `appfs1/basic/lib/libcurl.so.4.2.0` (`DT_RPATH` pointing to Blu-ray Player build `/proj/mtk94073/.../BDP/OSS/BDP_V301/...`).
