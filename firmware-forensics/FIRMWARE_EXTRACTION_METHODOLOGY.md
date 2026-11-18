# Firmware Extraction Methodology & Limitations

## 1. Pipeline Overview

Static extraction of the `AOC LE32S5760/20` firmware required handling custom MediaTek wrappers rather than standard out-of-the-box `binwalk` signatures alone. The reproducible extraction pipeline comprises five stages:

```
LE32S5760_V2.011_V0.2.zip
   └── [1. ZIP Deflate Unpack] ──> upgrade_loader.pkg (323,840,461 B)
         └── [2. PKG Tag Parser (0x98+)] ──> 16 Raw Partitions (3rdA..chtC)
               ├── kerA/kerB ──> [3. HW-LZHS Stream Decode] ──> scratch/vmlinux.bin
               ├── rfsA/rfsB ──> [4. Skip 0xe7 B NFSB Header -> unsquashfs] ──> extracted/appfs1/
               ├── 3rdA/3rdB ──> [4. Skip 0xe7 B NFSB Header -> unsquashfs] ──> extracted/rootfs1/
               └── roda      ──> [5. UBI Reader Extract] ──> ro_data_keys/*
```

---

## 2. Detailed Stage Mechanics

1. **Stage 1 — Archive Extraction:** Standard `unzip` decompresses `upgrade_loader.pkg` (`CRC32 0x195275a4`).
2. **Stage 2 — MTK PKG Partition Demultiplexing ([scripts/inspect_pkg_and_nfsb.py](../scripts/inspect_pkg_and_nfsb.py)):**
   Starting after the `152`-byte (`0x98`) outer PKG header, partitions follow sequential `12`-byte descriptors (`<4sII`: 4-byte ASCII tag in `KNOWN_PARTS`, 4-byte flag/metadata word, 4-byte little-endian payload length).
3. **Stage 3 — `kerA`/`kerB` Kernel Decompression & Header Alignment:**
   - The raw `kerA` blob begins with a `64`-byte U-Boot `uImage` header (`IH_MAGIC = 0x27051956`) followed by HW-LZHS compressed chunks and dual RSA-2048 signature/certificate trailers at `0x25152c` and `0x283f2c`.
   - Crucially, decompressed `scratch/vmlinux.bin` (`4,432,612` B) retains the `64`-byte (`0x40`) `uImage` header (`load = 0x00007fc0`, `ep = 0x00008000`). Stripping `0x40` bytes anchors the raw kernel binary cleanly at virtual base address `0xc0008000`, verified bit-for-bit against all ARM branch targets and `.rodata` string pointers.
4. **Stage 4 — `NFSB` Stripping & SquashFS Extraction:**
   Both `rfsA`/`B` (`mtd6`/`7`) and `3rdA`/`B` (`mtd9`/`10`) prepend a `231`-byte (`0xe7`) `NFSB` header ahead of a valid little-endian SquashFS (`hsqs`) superblock, with the `dm-bht` MD5 Merkle hash tree appended after the SquashFS data blocks (`data_blocks` at `NFSB + 0x24`, `total_blocks` at `NFSB + 0x20`). Slicing at offset `+0xe7` exposes the clean SquashFS filesystem for extraction while keeping the full `NFSB` + `dm-bht` image intact for offline Merkle proof verification.
5. **Stage 5 — UBI `roda` Extraction:** `roda` (`5,767,168` B) contains a raw UBI image extracted into `/ro_data` key/certificate files.

---

## 3. Observed Tooling Pitfalls & Methodological Limitations

- **FIFO Blocking Trap (`extracted/appfs1/dev/initctl`):** Unpacking `appfs1` reproduces a named pipe (`FIFO`) at `/dev/initctl`. Naive file walkers calling `.read_bytes()` without checking `stat.S_ISREG(st.st_mode)` hang indefinitely waiting for a pipe writer. All repository automation ([scripts/firmware_inventory.py](../scripts/firmware_inventory.py), [scripts/metadata_extraction.py](../scripts/metadata_extraction.py)) enforces `stat.S_ISREG` guards.
- **Unextracted Device-Initialized Partitions:** Partitions absent as images from `upgrade_loader.pkg` (`perm`, `3rd_rw`, `ddb`, `game`, `Seur`) and runtime NAND bad-block/wear-leveling state exist only on live flashed hardware and are **not** captured in static PKG extraction.
- **Encrypted / Non-Linux Blobs:** `adsp`, `aqda`, `pqda`, and masked BootROM/TrustZone firmware outside `load`/`kerA` cannot be extracted to C/ARM userland equivalents from `upgrade_loader.pkg` alone.
- **Laboratory Custom Comparison Scope:** `build/custom_upgrade_loader.pkg` (`323,840,461` B) and `build/staging_rootfs` record offline container repacking experiments (`custom_payload/`) preserved in Git only as source diffs/scripts, never as binary blobs.
