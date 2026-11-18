# Memory & Storage Architecture (`DRAM`, `NAND`, `NOR/EEPROM`)

## 1. Overview & Verification Status

| Memory Tier | Technology | Confirmed Evidence | Inferred / Unknown Attributes |
|---|---|---|---|
| **Volatile System RAM** | Dual-Channel DDR SDRAM (Ch A + Ch B) | Preloader `DRAM Channel A/B Calibration` routines; `uenv` `global_kernel_dram_size`; Linux `highmem.c` | Exact total MiB (`~512 MB` inferred for kernel/UI/Opera ceiling) & DDR3 chip part numbers |
| **Primary Mass Storage** | Raw NAND Flash (`mtd0..mtd30`, UBI + SquashFS) | `drivers/mtd/nand/mtk_nand.c`, `NAND_ECC_MODE`, `NAND_AES_INIT`, `cfig` table (`30` regions), `dm-verity` `NFSB` | Exact mounted chip PN (kernel recognizes 10 candidate Hynix/Micron/Samsung/Toshiba IDs) |
| **Auxiliary NVM / Boot Env** | EEPROM / NOR driver (`nor/eeprom_hw.c`, `nor/storage.c`) | `dtv_driver.ko` source paths; `fw_printenv` & `uenv` env object; dual-bank boot toggle logic | Exact I2C address / SPI flash part number without PCB probe |
| **SPI/eMMC Presence** | **eMMC NOT USED** in shipped firmware config | Zero `mmcblk`/`eMMC` mount entries in `fstab`/`etc/scripts`/`cfig`; all mounts use `mtdblock*` & `ubi*` | `u-boot`/SoC silicon support irrelevant to this NAND-configured unit |

---

## 2. Volatile DRAM Architecture

1. **Dual-Channel Calibration in Preloader (`uboot.bin`):**
   Static string & code inspection of the first `0xa040` bytes of `extracted/uboot.bin` confirms sequential hardware initialization for `DRAM Channel A` and `DRAM Channel B` before jumping to main U-Boot (`0x0000a040+`).
2. **Kernel HighMem & Reserved Carveouts:**
   Presence of `arch/arm/mm/highmem.c`, `arch/arm/mm/dma-mapping.c`, and `mt53xx_get_reserved_area` in `scratch/vmlinux.bin` confirms that MediaTek partitions physical DRAM into:
   - **Linux Lowmem / Kernel Space** (managed via `mm/memblock.c`, `slub.c`)
   - **DMA / A/V Framebuffer & Codec Carveouts** (`mt53xx_get_reserved_area`, `mtk_mmap.ko`)
   - **TrustZone Secure World Memory** (paired with `TRUSTZONE=enable`)
   This explains why `Qt 4.8.3` (`SystemManager`), `Opera Presto`, and `Netflix NRD` face tight out-of-memory constraints despite total board DRAM typically totaling ~`512 MB` on MT5880 TVs (runtime `/proc/meminfo` exact byte split remains uncaptured).

---

## 3. Non-Volatile NAND Flash Architecture (`cfig` + Kernel Driver)

### 3.1 Supported NAND Flash ID Table in `vmlinux.bin`
Static string extraction from `scratch/vmlinux.bin` ([firmware-forensics/FIRMWARE_METADATA.json](../firmware-forensics/FIRMWARE_METADATA.json)) identifies `10` explicit raw NAND IC identifiers compiled into `drivers/mtd/nand/mtk_nand.c`:

| Vendor | Compiled NAND ID String | Typical Organization |
|---|---|---|
| **SK Hynix** | `NAND_H27U8G8T2BTR`, `NAND_H27UAG8T2ATR`, `NAND_H27UAG8T2BTR`, `NAND_H27UAG8T2MTR` | 1 GB – 2 GB SLC/MLC NAND |
| **Micron** | `NAND_MT29F8G08ABA`, `NAND_MT29F16G08CBABA`, `NAND_MT29F16G08CBACA` | 1 GB – 2 GB MLC/SLC NAND |
| **Samsung** | `NAND_K9GAG08U0E` | 2 GB MLC NAND |
| **Toshiba** | `NAND_TC58NVG4D1DTG`, `NAND_TC58NVG4D2FTA00` | 2 GB MLC NAND |

Additionally, the Preloader carries Extended NAND ID (`ExNID`) probing (`ExNID=0x00001676/00000004/00000056`), hardware ECC (`NAND_ECC_MODE`), and `NAND_AES_INIT` / `NAND_AES_Encryption` / `NAND_AES_Decryption`. **Because the unit was never opened**, which single chip out of these 10 supported parts is physically soldered on the study board cannot be asserted without tearing down the TV.

### 3.2 Complete `cfig` NAND Partition Table (`mtd1..mtd30`)
Decoded directly from the `237`-byte `cfig` chunk inside `upgrade_loader.pkg` (`offset 0x0bfec0c8`):

| MTD Index | `cfig` Tag | PKG Blob Present? | PKG Payload Size | Runtime Filesystem & Verification |
|---|---|---|---|---|
| `mtd0` | *(Pre-cfig / `load` boot area)* | Yes (`load`) | `1,314,592` B | Raw Preloader + U-Boot + RSA-2048 signature (`+0x6c4b0`) |
| `mtd1` | `uenv` | Yes (`uenv`) | `2,384` B | U-Boot environment (unstripped ELF `.o` in PKG) |
| `mtd4` | `kerA` | Yes (`kerA`) | `2,638,124` B | Bank A HW-LZHS `uImage` + dual RSA-2048 trailers (`0x25152c`, `0x283f2c`) |
| `mtd5` | `kerB` | Yes (`kerB`) | `2,638,124` B | Bank B kernel mirror (bit-identical to `kerA`) |
| `mtd6` | `rfsA` | Yes (`rfsA`) | `51,466,240` B | Bank A SquashFS rootfs wrapped in `NFSB` v2 + `dm-bht` MD5 (`12,514` blocks) |
| `mtd7` | `rfsB` | Yes (`rfsB`) | `51,466,240` B | Bank B rootfs mirror (bit-identical to `rfsA`) |
| `mtd9` | `3rdA` | Yes (`3rdA`) | `97,738,752` B | Bank A `/3rd` SquashFS wrapped in `NFSB` v2 + `dm-bht` MD5 (`23,767` blocks) |
| `mtd10` | `3rdB` | Yes (`3rdB`) | `97,738,752` B | Bank B `/3rd` mirror (bit-identical to `3rdA`) |
| `mtd11` | `perm` | No (initialized on-TV) | — | `ubiattach -m 11 -d 2` -> `ubi2:perm` UBIFS mounted `-rw` at `/perm` |
| `mtd12` | `3rdw` | No (initialized on-TV) | — | `ubiattach -m 12 -d 4` -> `ubi4:3rd_rw` UBIFS mounted `-rw` at `/3rd_rw` (**No NFSB**) |
| `mtd13` | `roda` | Yes (`roda`) | `5,767,168` B | `ubiattach -m 13 -d 3` -> `ubi3:ro_data` UBIFS mounted `-r` at `/ro_data` |
| `mtd14` | `game` | No | — | Declared in `cfig`; unused/unmounted in observed startup scripts |
| `mtd17` | `pqda` | Yes (`pqda`) | `11,534,336` B | Picture quality / panel LUT calibration data |
| `mtd18` | `aqda` | Yes (`aqda`) | `131,216` B | Audio quality equalizer calibration data |
| `mtd26` | `ddb` | No | — | Declared in `cfig` (device/channel database) |
| `mtd27` | `chtC` | Yes (`chtC`) | `65,536` B | Channel table bank C |
| `mtd28` | `chtD` | Yes (`chtD`) | `65,536` B | Channel table bank D (identical SHA-256 to `chtC`) |
| `mtd29` | `adsp` | Yes (`adsp`) | `1,272,368` B | Audio DSP binary image |
| `mtd30` | `Seur` | No | — | Declared in `cfig` (Secure / user data slot) |

*(Gaps such as `mtd2`, `mtd3`, `mtd8`, `mtd15`..`mtd25` correspond to unmapped/reserved NAND layout slots or factory-allocated regions outside the PKG upgrade manifest.)*

---

## 4. Auxiliary EEPROM / NOR Driver Evidence

Inside `dtv_driver.ko` (and kernel `drivers/mtd/mtk_mtdpart.c`), the explicit compile paths:
- `.../5880_driver/nor/eeprom_hw.c`
- `.../5880_driver/nor/storage.c`
demonstrate low-level support for EEPROM / NOR parameter storage used to persist TV factory settings, HDCP/CI+ flags, and active A/B bank selection flags read at boot by U-Boot and modified via `libmtkapp.so` (`_phm_upg_model_start_upgrade`).
