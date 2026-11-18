# Kernel Source Comparison (`MT5880 Linux 3.0.13` vs. Upstream Mainline `Linux 3.0.13`)

## 1. Comparison Scope & Evidentiary Discipline

Because complete OEM Linux GPL source tarballs for `AOC LE32S5760/20` (`V2.011_V0.2`) were not included in `LE32S5760_V2.011_V0.2.zip`, comparisons rely strictly on:
- All **`381` compiled C/header path literals** embedded in `scratch/vmlinux.bin` (`/share/Release_code_use/Roy/release/vm_linux/chiling/kernel/linux-3.0/...`),
- All **`8` source path literals** inside proprietary `dtv_driver.ko` (`/share/.../driver/ko/mt5880/...`),
- Exact symbol names (`mt53xx_*`, `dm_bht_*`, `nfsb`), console strings (`"<3>nfsb: ..."`, `console=ttyMT0,115200n1`), and disassembled ARM32 functions (`0xc0009594`, `0xc0028df8`, `0xc02243c4`).

---

## 2. Subsystem Diff: Mainline `Linux 3.0.13` (Dec 2011) vs. MediaTek/TPV BSP (`Aug 2016`)

| Subsystem | Upstream `kernel.org` `3.0.13` State | Target `MT5880` (`chiling`) Deviation & File Proof | Technical & Security Consequence |
|---|---|---|---|
| **ARM Machine Port (`arch/arm/mach-*`)** | Upstream Linux `3.0.13` has **no** `mach-mt53xx` directory (`DTV` SoCs absent from mainline). | Introduces `arch/arm/mach-mt53xx/gpio6896.c`, `pdwnc_gpio6896.c`, plus `mt53xx_{bim_lock, get_ic_version, get_reserved_area, get_rodata_addr, get_rwdata_addr, timer_read, timer_read_ll}`. | Tightly binds boot, standby `T8032`, and reserved DMA memory layout to proprietary MediaTek BSP headers. |
| **Verified Boot / Block Integrity (`drivers/md/`)** | Vanilla `3.0.13` contains `dm.c`, `dm-ioctl.c`, `dm-stripe.c`, `dm-table.c`, `dm-target.c`, `dm-io.c`, `dm-kcopyd.c` — **does NOT contain `dm-verity` (`added in Linux 3.4`) or `dm-bht`**. | Backports ChromeOS `drivers/md/dm-bht.c` (`20` `dm_bht_*` functions) + `drivers/md/dm-verity.c` + `init/do_mounts_dm.c` (`absent in mainline`), modified with custom **`NFSB` v2 (`populate_table_nfsb` @ `0xc02243c4`, `nfsb_rsa_check` @ `0xc0028df8`)**. | Enforces kernel-level RSA-1024 (`e=3`) + 2-level MD5 Merkle checks at mount time (`<3>nfsb: header verification failed`), blocking unsigned SquashFS replacement. |
| **MTD & Raw NAND (`drivers/mtd/`)** | Mainline ships generic `mtdcore.c`, `mtdpart.c`, `mtdblock.c`, `nand_base.c`, `nand_bbt.c`, `ubi/{scan.c, wl.c}`. | Adds `drivers/mtd/mtk_mtdpart.c`, `drivers/mtd/mtdsdm.c` (`/dev/sdm*`), and `drivers/mtd/nand/mtk_nand.c` (`10` flash IDs + `NAND_AES_INIT`/ECC hardware modes). | Enables MediaTek `cfig` (`mtd1..mtd30`) partition map, `PSDM` block access, and inline NFI NAND cryptography. |
| **Kernel Crypto (`crypto/`)** | Generic software algorithms (`ablkcipher.c`, `aead.c`, `algapi.c`, `blkcipher.c`, `chainiv.c`). | Injects `crypto/mtk_crypto.c`. | Bridges hardware SoC cipher/hash block into Linux CryptoAPI (`crypto_hash_*` invoked by `nfsb_rsa_check`). |
| **USB Host (`drivers/usb/host/`)** | EHCI / OHCI / xHCI upstream drivers. | Injects `drivers/usb/host/mtk_hcd.c` & `drivers/usb/host/mtk_qmu.c` for MediaTek USB PHY and Queue Management Unit DMA. | Non-standard USB host silicon; mainline QEMU kernels lack `mtk_qmu` models. |
| **OEM Board Drivers (Out-of-Tree `.ko`)** | Not part of mainline kernel tree. | `dtv_driver.ko` (`6.84 MB`, `Proprietary`) compiles `TPV/Philips_2K13_ODM_pdwnc_ext.c`, `TPVision_2k13_d_custom.c`, `ir6896/{irrc,irrx}_if.c`, `nor/{eeprom_hw,storage}.c` (`/dev/eeprom_{0,3,4}`), `pdwnc6896/pdwnc_hw.c`, `mt53xx_fb/mt53_fb.c`. | Prevents swapping `vmlinux` cleanly for an upstream mainline ARM kernel even aside from RSA boot signatures. |

---

## 3. Cross-SDK Artifact Contamination Observed in Userland (`DT_RPATH`)

Complementing kernel inheritance analysis, `readelf -d` exposes direct multi-product SDK cross-pollination in userspace shared objects:
- `appfs1/basic/lib/libcurl.so.4.2.0` carries hardcoded builder `RPATH` `/proj/mtk94073/ws_mtk94073_1st/BDP/OSS/BDP_V301/BDP_Linux/...` (**MediaTek Blu-ray Disc Player SDK `BDP_V301`**).
- `rootfs1/ginga/lib/libcurl.so.4.2.0` carries CERTI Brazil `envision_middleware_clean` (`arm_mtk451`) build paths linking independently against `openssl-1.0.0d`.
- `rootfs1/netflix/nrd-app/netflix` stamps exact TPV Perforce workspace `20150420_194932/TPV_linux_REL_PHILIPS_2K14` (`gnuarm-4.5.1_vfp_ca9`), confirming the multi-brand `Philips 2K14` -> `AOC 2016` inheritance hierarchy.
