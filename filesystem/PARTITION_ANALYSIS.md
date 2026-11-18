# NAND Partition Analysis (`mtd0..mtd30` & Runtime Mount Mechanics)

> **Metadata Reference:** [firmware-forensics/FIRMWARE_METADATA.json](../firmware-forensics/FIRMWARE_METADATA.json) (`cfig` sequence)

## 1. Exact Factory Partition Table (`cfig` + `upgrade_loader.pkg`)

Combining the `237`-byte `cfig` sequence (`upgrade_loader.pkg @ 0x0bfec0c8`), `libmtkapp.so` `PMTD` string table, and runtime mount scripts (`appfs1/etc/scripts/*.sh`) produces the complete verified flash map:

| MTD Dev | `cfig` Token | PKG Chunk | PKG Payload Size | Bank Role | Format & Mount Target | Integrity Enforcement |
|---|---|---|---|---|---|---|
| `/dev/mtd0` | *(Pre-cfig)* | `load` | `1,314,592` B | **Single Boot** | Raw Preloader + LZHS U-Boot (not mounted in Linux) | eFuse `0xf0008664` + BootROM RSA-2048 |
| `/dev/mtd1` | `uenv` | `uenv` | `2,384` B | **Single** | U-Boot environment block (`fw_printenv`) | None in userspace; U-Boot checksum |
| `/dev/mtd4` | `kerA` | `kerA` | `2,638,124` B | **Bank A** | HW-LZHS `uImage` Linux `3.0.13` | Dual RSA-2048 trailers (`0x25152c`/`0x283f2c`) |
| `/dev/mtd5` | `kerB` | `kerB` | `2,638,124` B | **Bank B** | Bit-identical backup of `kerA` | Dual RSA-2048 trailers |
| `/dev/mtd6` | `rfsA` | `rfsA` | `51,466,240` B | **Bank A** | `NFSB` v2 + SquashFS -> `/` (`dm_mount_root_nfsb`) | RSA-1024 (`e=3`) + `12,514`-blk `dm-bht` MD5 |
| `/dev/mtd7` | `rfsB` | `rfsB` | `51,466,240` B | **Bank B** | Bit-identical backup of `rfsA` | RSA-1024 (`e=3`) + `12,514`-blk `dm-bht` MD5 |
| `/dev/mtd9` | `3rdA` | `3rdA` | `97,738,752` B | **Bank A** | `NFSB` v2 + SquashFS -> `/dev/mapper/dm-1` -> `/3rd` | RSA-1024 (`e=3`) + `23,767`-blk `dm-bht` MD5 |
| `/dev/mtd10` | `3rdB` | `3rdB` | `97,738,752` B | **Bank B** | Bit-identical backup of `3rdA` | RSA-1024 (`e=3`) + `23,767`-blk `dm-bht` MD5 |
| `/dev/mtd11` | `perm` | *(On-TV)* | Variable | **Single** | `ubiattach -m 11 -d 2` -> `ubi2:perm` -> `/perm` | UBI CRC headers only (`-rw -o no_chk_data_crc`) |
| `/dev/mtd12` | `3rdw` | *(On-TV)* | Variable | **Single** | `ubiattach -m 12 -d 4` -> `ubi4:3rd_rw` -> `/3rd_rw` | **None** (`-rw -o no_chk_data_crc`, no `NFSB`) |
| `/dev/mtd13` | `roda` | `roda` | `5,767,168` B | **Single** | `ubiattach -m 13 -d 3` -> `ubi3:ro_data` -> `/ro_data` | Mounted `-r` (read-only UBIFS) |
| `/dev/mtd14` | `game` | *(None)* | — | **Single** | Declared in `cfig`; no active mount script observed | Uninspected |
| `/dev/mtd17` | `pqda` | `pqda` | `11,534,336` B | **Single** | Panel timing & picture-quality tables | Raw/proprietary read via `dtv_svc` |
| `/dev/mtd18` | `aqda` | `aqda` | `131,216` B | **Single** | Audio equalizer tables | Raw/proprietary |
| `/dev/mtd26..30` | `ddb`, `chtC/D`, `adsp`, `Seur` | Partial (`chtC/D`, `adsp`) | `65KB` / `1.27MB` | Channel/DSP | `chtC`/`D` (`65,536` B), `adsp` (`1,272,368` B), `Seur` | Proprietary / Channel DB |

---

## 2. Cryptographic & Operational Separation Analysis

Notice two deliberate engineering separations in this partition scheme:
1. **Immutable Code vs. Mutable State:** Every executable OS binary (`/bin`, `/basic`, `/3rd/qt`, `/3rd/nettv`, `/3rd/netflix`) resides inside `NFSB`-signed SquashFS partitions (`mtd6`/`7` & `mtd9`/`10`), whereas writable application state (`/3rd_rw`, `/perm`) uses unencrypted UBI/UBIFS with `-o no_chk_data_crc` for fast NAND performance.
2. **`dmsetup` Hardcoded Major/Minor Dev Assignment:** Both `dmverity_mount_3rda.sh` and `dmverity_mount_3rdb.sh` run `dmsetup -r -j 254 -m 1 create dm-1 --table "0 0 verity /dev/mtdblock{9|10}"`, passing `"0 0"` dummy offsets because MediaTek's modified kernel `populate_table_nfsb` automatically reads sector counts and hashes from the `231`-byte `NFSB` header at byte `0` of the block device!
