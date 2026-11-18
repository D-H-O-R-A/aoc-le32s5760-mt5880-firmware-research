# Memory & Storage Architecture (`DRAM`, `NAND`, `NOR/EEPROM`)

## 1. Documentation Correction Record: Physical DRAM Sizing via `uenv` ELF `.data`

- **Initial Baseline Estimate (`v1.0.0` / Early Docs):** Inferred total board RAM at `~512 MB` based on legacy `Qt 4.8.3` / `Opera Presto 6213` ceiling heuristics.
- **Confirmed Empirical Refinement (`v2.0.0`):** Inspecting the unstripped DWARF ELF object inside `upgrade_loader.pkg#part:uenv` (`2,384` B, `chiling/uboot/board/mt5880/env.c`) recovered the exact initialized `.data` words at file offset `0x34`:
  ```text
  global_magic            = 0x53965368   (32-bit UINT32, offset 0x00 in .data)
  global_kernel_dram_size = 0x21fb9000   (570,134,528 bytes = 543.72 MiB!)
  ```
- **Architectural Deduction:** Because Linux itself receives **`543.72 MiB`** (`0x21fb9000` bytes) via `global_kernel_dram_size` *excluding* reserved MediaTek DMA/video codec carveouts (`mt53xx_get_reserved_area`) and TrustZone secure world memory (`TRUSTZONE=enable`), **total soldered physical Dual-Channel DDR3 capacity on this chassis must exceed `543.7 MiB`** (typically `768 MiB` asymmetric Channel A+B or `1 GiB` minus ~`224–480 MiB` media carveouts). Exact soldered DDR3 IC count/density remains **UNVERIFIED** without physical heatsink removal and chassis teardown ([HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md)).

---

## 2. Memory Tier Summary

| Memory Tier | Technology & Channel Layout | Primary Binary / ELF Evidence | Confidence |
|---|---|---|---|
| **Volatile System RAM** | Dual-Channel DDR SDRAM (Channels A & B calibrated independently for DQS timing) | Preloader strings `"DRAM Channel A Calibration."`, `"DRAM Channel B Calibration."`, `"DRAM Input DQS Calibration fail !"`; `uenv` `0x21fb9000` (`543.7 MiB` kernel window); Linux `highmem.c` + `mmu.c` | **CONFIRMED (`0x21fb9000` Window & Ch A/B) / INFERRED (Total IC MB)** |
| **Primary Mass Storage** | Raw NAND Flash (`mtd0..mtd30`, `NFI` controller w/ HW ECC & NAND AES) | `drivers/mtd/nand/mtk_nand.c`, `NAND_ECC_MODE`, `NAND_AES_INIT`, Preloader `ExNID`, `cfig` table (`30` slots) | **CONFIRMED (Bus & Controller) / UNKNOWN (Exact Soldered Chip PN)** |
| **Secondary / EEPROM / NOR NVM** | Device nodes `/dev/eeprom_0`, `/dev/eeprom_3`, `/dev/eeprom_4` + `nor/` driver layer | `dtv_driver.ko` `/dev/eeprom_*` strings & source paths `nor/eeprom_hw.c`, `nor/storage.c`; `libmtkapp.so @ 0x40ae80` | **CONFIRMED** |
| **eMMC Flash** | **ABSENT / UNUSED** | Zero `mmcblk` or `eMMC` mount points in `fstab`, `cfig`, or `etc/scripts/*` | **CONFIRMED ABSENT** |

---

## 3. Raw NAND Flash Controller (`mtk_nand.c`) & `cfig` Partition Layout

### 3.1 Supported Flash IC Table Compiled into `vmlinux.bin`
Static inspection reveals **`10` specific SLC/MLC NAND flash device IDs** registered inside `drivers/mtd/nand/mtk_nand.c`, alongside Preloader `ExNID` detection (`ExNID=0x00001676/00000004/00000056`):

| Manufacturer | Kernel `NAND_*` Identifiers |
|---|---|
| **SK Hynix** | `NAND_H27U8G8T2BTR`, `NAND_H27UAG8T2ATR`, `NAND_H27UAG8T2BTR`, `NAND_H27UAG8T2MTR` |
| **Micron** | `NAND_MT29F8G08ABA`, `NAND_MT29F16G08CBABA`, `NAND_MT29F16G08CBACA` |
| **Samsung** | `NAND_K9GAG08U0E` |
| **Toshiba** | `NAND_TC58NVG4D1DTG`, `NAND_TC58NVG4D2FTA00` |

### 3.2 Complete `cfig` NAND Layout (`mtd0..mtd30`)
Parsed verbatim from the `237`-byte `cfig` table (`upgrade_loader.pkg @ 0x0bfec0c8`):

| MTD | `cfig` Tag | PKG Size (Bytes) | Role & Verification Mode |
|---|---|---|---|
| `mtd0` | *(Pre-cfig `load`)* | `1,314,592` | Thumb-2 Preloader (`0..0xa040`) + LZHS U-Boot + RSA-2048 (`+0x6c4b0`) |
| `mtd1` | `uenv` | `2,384` | U-Boot environment block (`global_magic=0x53965368`, `global_kernel_dram_size=0x21fb9000`) |
| `mtd4` / `mtd5` | `kerA` / `kerB` | `2,638,124` each | HW-LZHS `uImage` Linux `3.0.13` + dual `512`-B RSA-2048 trailers (`0x25152c`, `0x283f2c`) |
| `mtd6` / `mtd7` | `rfsA` / `rfsB` | `51,466,240` each | `NFSB` v2 + SquashFS (`/`, RO) + `dm-bht` MD5 (`12,514` blocks) |
| `mtd9` / `mtd10` | `3rdA` / `3rdB` | `97,738,752` each | `NFSB` v2 + SquashFS (`/3rd`, RO via `dmsetup`) + `dm-bht` MD5 (`23,767` blocks) |
| `mtd11` | `perm` | *(Device UBI)* | `ubiattach -m 11 -d 2` -> `ubi2:perm` -> `/perm` (**RW UBIFS**, no `NFSB`) |
| `mtd12` | `3rdw` | *(Device UBI)* | `ubiattach -m 12 -d 4` -> `ubi4:3rd_rw` -> `/3rd_rw` (**RW UBIFS**, no `NFSB`) |
| `mtd13` | `roda` | `5,767,168` | `ubiattach -m 13 -d 3` -> `ubi3:ro_data` -> `/ro_data` (**RO UBIFS** `-r`) |
| `mtd14` / `mtd17` / `mtd18` | `game`, `pqda`, `aqda` | `—`, `11.5 MB`, `131 KB` | Game reservation; LCD Panel PQ LUT (`pqda`); Audio EQ (`aqda`) |
| `mtd26..mtd30` | `ddb`, `chtC/D`, `adsp`, `Seur` | `—`, `65 KB`, `1.27 MB`, `—` | Device DB; Channel Tables C/D; Audio DSP firmware; Secure data region |
