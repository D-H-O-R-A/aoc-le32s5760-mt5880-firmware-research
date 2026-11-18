# Kernel Source Comparison (`MT5880 Linux 3.0.13` vs. Upstream Mainline `Linux 3.0.13` & Public `MT53xx` Trees)

## 1. Comparison Scope & Epistemic Rule

Because OEM GPL source tarballs for `AOC LE32S5760/20` (`chiling` / `MT5880`) are not bundled inside `LE32S5760_V2.011_V0.2.zip`, comparisons below evaluate **confirmed file paths, symbol names, and disassembled functions extracted directly from `scratch/vmlinux.bin` and `dtv_driver.ko`** against the standard upstream `Linux 3.0.13` source tree structure and documented ChromiumOS `dm-verity` (`dm-bht`) architecture — never assuming uninspected C implementation details from file names alone.

---

## 2. Upstream Vanilla `Linux 3.0.13` Files vs. MediaTek/TPV Vendor Additions

### 2.1 Files Present in `vmlinux.bin` Absent from Vanilla Mainline `Linux 3.0.13`
The following paths compiled into `scratch/vmlinux.bin` do **not** exist in stock upstream `kernel.org` Linux `3.0.13` and constitute verifiable BSP additions:

| Compiled Path in `vmlinux.bin` | Functional Subsystem | Evidence Observed in Binary |
|---|---|---|
| `arch/arm/mach-mt53xx/gpio6896.c` | MT53xx/MT5880 GPIO controller | File path string + symbol family (`mt53xx_*`) |
| `arch/arm/mach-mt53xx/pdwnc_gpio6896.c` | Standby power-down (`PDWNC`) GPIOs (`T8032` domain) | Explicit path string + symbol `pdwnc_gpio6896` |
| `crypto/mtk_crypto.c` | SoC hardware cipher/digest acceleration | Compiled in alongside upstream `crypto/{api, algapi, blkcipher, scatterwalk}.c` |
| `drivers/md/dm-verity.c` | Block-level cryptographic verity target (upstream mainline added `dm-verity` only in Linux `3.4`!) | Path string + `populate_table_nfsb @ 0xc02243c4` + `nfsb_rsa_check @ 0xc0028df8` |
| `drivers/md/dm-bht.c` | ChromeOS Block Hash Tree (`dm_bht_*` API, backported before mainline `3.4`) | Path string + 20 `dm_bht_*` identifiers (`dm_bht_verify_block`, `dm_bht_root_hexdigest`, etc.) |
| `drivers/mtd/mtdsdm.c` | MediaTek Smart/SDM block partition wrapper (`PSDM` -> `/dev/sdm%d`) | Path string + matching `libmtkapp.so sub_404fbc` branch (`"sdm%d"`) |
| `drivers/mtd/mtk_mtdpart.c` | MediaTek NAND partition parser matching `cfig` (`mtd1..mtd30`) | Path string + `PMTD` lookup table |
| `drivers/mtd/nand/mtk_nand.c` | MTK NFI NAND controller driver with HW ECC & NAND AES | Path string + `10` `NAND_*` chip IDs + `NAND_AES_Encryption/Decryption/INIT` |
| `drivers/usb/host/mtk_hcd.c` & `mtk_qmu.c` | MediaTek USB host & Queue Management Unit controller | Compiled alongside upstream `drivers/usb/core/{hcd.c, hub.c}` |
| `init/do_mounts_dm.c` | Early rootfs `dm-verity` mount bypass of userspace `initrd` | Path string + `dm_mount_root_nfsb @ 0xc0009594` |

### 2.2 Key Vendor Deviations Proven by Disassembly (Beyond File Names)
1. **Backported ChromeOS `dm-verity`/`dm-bht` Modified for `NFSB` RSA-1024 (`v2`):**
   - Standard ChromeOS `dm-verity` relies on signed kernel command-line `verity` parameters (`root_hexdigest`) protected by a verified boot image/initramfs.
   - Instead, MediaTek backported `dm-bht.c` into Linux `3.0.13` and wrapped root/application SquashFS partitions in a proprietary **`231`-byte (`0xe7`) `NFSB` v2 header** authenticated inline by `nfsb_rsa_check` (`0xc0028df8`) using an **MD5-based** `dm-bht` tree (`12,514` blocks on `rfsA`, `23,767` blocks on `3rdA`) and an embedded **1024-bit `e=3` RSA modulus (`0xc0429370`)**.
   - Disassembly proves `mpuint_equal` enforces exact zero-padding equality ($S^3 \bmod N == 0^{96} \parallel \text{SHA-256}$), hardening raw `e=3` verification against Bleichenbacher padding truncation.
2. **Legacy `init/do_mounts_dm.c` Hook (`mtd6`/`mtd7` Direct Verity Root):**
   Mainline Linux `3.0.13` lacks `do_mounts_dm.c`; MediaTek/ChromiumOS early-boot hooks mount `/dev/mtdblock6` (`rfsA`) or `/dev/mtdblock7` (`rfsB`) transparently as `/` before BusyBox `/sbin/init` runs.
3. **Out-of-Tree `dtv_driver.ko` ODM Split (`TPV`):**
   While MediaTek `mach-mt53xx` handles low-level ARM/NAND/USB primitives in `vmlinux`, TPV board-specific PDWNC extensions (`Philips_2K13_ODM_pdwnc_ext.c`, `TPVision_2k13_d_custom.c`), EEPROM/NOR NVM (`nor/eeprom_hw.c`, `nor/storage.c`), IR decoding (`ir6896`), and framebuffer (`mt53_fb.c`) live cleanly separated inside the proprietary `dtv_driver.ko` module.
