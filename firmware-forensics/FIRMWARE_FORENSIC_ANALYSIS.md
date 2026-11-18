# Firmware Forensic Analysis (`LE32S5760_V2.011_V0.2.zip` -> `upgrade_loader.pkg`)

> **Hash Manifest:** [FIRMWARE_HASH_MANIFEST.txt](FIRMWARE_HASH_MANIFEST.txt) | **Metadata JSON:** [FIRMWARE_METADATA.json](FIRMWARE_METADATA.json) | **Binary CSV:** [FIRMWARE_BINARY_INVENTORY.csv](FIRMWARE_BINARY_INVENTORY.csv)

## 1. Master Identification Summary

| Property | Exact Observed Value |
|---|---|
| **Distribution Zip** | `LE32S5760_V2.011_V0.2.zip` (`285,061,005` bytes) |
| **Zip SHA-256** | `014e235cb9406be9d8d61cc780093d3d5196b8748f72a088b43641dc99d0d1ff` |
| **Inner Firmware Image** | `upgrade_loader.pkg` (`323,840,461` bytes; ZIP entry CRC32 `0x195275a4`; Modified `2016-08-03 14:26:04`) |
| **PKG SHA-256** | `219de76d6dea7f62fe3648392f6262031e230cc33380c2b173c22fc667089b83` |
| **Internal Software Tags** | `SYS_VERSION=IDTV0801_002223_9_001_23_001_224`, `TPV_VERSION=000.001.205.145`, `SYS_BRAND=Philips`, `SYS_ODM=TPV` |
| **Kernel Banner** | `Linux version 3.0.13 (roylo@TWCLS066) (gcc version 4.5.1 (GCC) ) #1 SMP PREEMPT Thu Aug 4 00:06:04 CST 2016` |
| **Total Extracted Files Tracked** | `appfs1`: `416` files / `190` symlinks / `94` dirs; `rootfs1`: `2,919` files / `157` symlinks / `228` dirs (`FILESYSTEM_INVENTORY.csv`) |

---

## 2. Structural Comparison: Official Archive vs. Extracted Disk Images

During reverse engineering, `upgrade_loader.pkg` unpacks cleanly into distinct functional layers whose relationship differs structurally between the raw flashable package and mounted Linux filesystems:

| Package Tag | Offset (`upgrade_loader.pkg`) | Size (Bytes) | Format & Cryptography in PKG | Extracted Form in Workspace | Fidelity & Transformations Applied |
|---|---|---|---|---|---|
| `3rdB` / `3rdA` | `0x000000a4` / `0x05d360b0` | `97,738,752` | `NFSB` v2 (`0xe7` B header, RSA-1024 `e=3` sig) + SquashFS (LZMA/XZ/zlib blocks) + 2-level `dm-bht` MD5 tree (`23,767` blocks) | `extracted/rootfs1` (`2,919` regular files) | NFSB + Merkle tree stripped upon unpack (`unsquashfs` extracts content; symlinks preserved) |
| `rfsB` / `rfsA` | `0x0cd8452d` / `0x0fe99539` | `51,466,240` | `NFSB` v2 (`0xe7` B header, RSA-1024 `e=3` sig) + SquashFS + `dm-bht` MD5 tree (`12,514` blocks) | `extracted/appfs1` (`416` files, `190` symlinks, 1 FIFO `/dev/initctl`) | NFSB + Merkle tree stripped upon unpack |
| `kerB` / `kerA` | `0x12fae545` / `0x1323267d` | `2,638,124` | HW-LZHS compressed `uImage` + dual RSA-2048 `(256B sig + 256B cert)` trailers at `0x25152c` and `0x283f2c` | `scratch/vmlinux.bin` (`4,432,612` B) | Decompressed from HW-LZHS (`64B` U-Boot `uImage` header + `4,432,548` B raw kernel image) |
| `load` | `0x0bfec1c1` | `1,314,592` | `0x0000..0xa040` Thumb-2 Preloader + HW-LZHS U-Boot + RSA-2048 trailer (`+0x6c4b0`) | `extracted/uboot.bin` (`1,314,592` B) | Exact byte copy of `load` partition (`SHA256: 88bfd15c...`) |
| `roda` | `0x0ba6c0bc` | `5,767,168` | UBI image (`UBI#` headers) carrying `ubi3:ro_data` (`/ro_data`) | `extracted/ro_data_keys/*.pem/.key/.iv` | Selective key extraction (`*.pem`/`*.key`/`*.iv` strictly excluded from Git) |
| `uenv` | `0x0c12d0ed` | `2,384` | Unstripped ARM32 relocatable ELF `.o` (`env.c`, `board/mt5880`) | `extracted/uenv` (`2,384` B) | Exact byte copy (`SHA256: baa332db...`) |
| `adsp`, `aqda`, `pqda`, `chtC`, `chtD`, `usig`, `cfig` | See `FIRMWARE_METADATA.json` | Various | Proprietary DSP code, calibration binary tables, channel tables, `512`-B `usig` block, `237`-B `cfig` text | Audited inline via `FIRMWARE_METADATA.json` | Remain packed; non-Linux DSP/LUT blobs classified explicitly without guesswork |

---

## 3. Classification of Non-Linux & Undecoded Binary Payloads

To uphold scientific rigor and avoid misclassifying opaque blobs:
- **`adsp` (`1,272,368` B, `SHA256: ea72302e...`):** Identified as Audio DSP firmware by tag and `cfig` (`nand 29`); internal proprietary DSP ISA instruction set not disassembled in this study (**CONFIRMED ROLE / UNDECODED ISA**).
- **`aqda` (`131,216` B) & `pqda` (`11,534,336` B):** Audio Quality and Picture Quality LUT tables mapped to `nand 18` and `nand 17`; panel-specific register curves not parsed structurally (**CONFIRMED ROLE / OPAQUE TABLES**).
- **`usig` (`512` B, `SHA256: 62c2ecd3...`):** `512`-byte package-level signature block referenced in `mount_perm.sh` (`/etc/config/usig_recovery`); exact RSA verification routine for standalone `usig` was not traced in `uboot.bin` disassembly (**OBSERVED ARTIFACT / PARTIALLY UNCHARACTERIZED**).
- **`chtC` / `chtD` (`65,536` B each, `SHA256: 1cbb642b...`):** Identical factory channel map placeholders (`nand 27` / `nand 28`).
- **`3rd_rw` (`mtd12`):** Absent from `upgrade_loader.pkg` as a blob despite appearing in `cfig` (`3rdw nand 12`), because the production UBIFS volume is initialized cleanly on the device and populated incrementally via `smth` updates or first-boot initialization.

---

## 4. Packaging, Compression & Cryptographic Controls Detected

1. **PKG Outer Layer:** Unencrypted container intended for USB rescue/factory flashing (`upgrade_loader.pkg`), protected internally by stage-specific hardware signatures (`load`, `kerA`/`kerB`, `rfsA`/`rfsB`, `3rdA`/`3rdB`).
2. **`Autorun.upg` User Upgrade Layer:** Dual-AES (`09291094*4` + 33-byte `\n`-hashed `ro_data` key/IV) + Body MD5 + Chunk SHA-256 + RSA-2048 (`TPV_MTK2K14PLF_LT0_UPG_*`) over XML manifest (`ixml`) and tagged payload chunks ([UPDATE_PACKAGE_FORMAT.md](../update-analysis/UPDATE_PACKAGE_FORMAT.md)).
3. **Runtime Kernel/Block Layer:** Proprietary MediaTek **HW-LZHS** on `uboot`/`kerA` + **SquashFS** with **2-level `dm-bht` MD5 Merkle tree** + **raw RSA-1024 (`e=3`)** header on `rfsA`/`rfsB`/`3rdA`/`3rdB`.
