# Firmware Format Specifications (`PKG`, `NFSB v2`, `dm-bht`, `uImage`, `Autorun.upg`)

## 1. MediaTek `upgrade_loader.pkg` Container Format

```
Offset          Size        Field
0x00000000      0x98 (152B) Outer PKG preamble / model & package header
0x00000098      0x0C (12B)  Partition #1 descriptor: [Tag: 4B][Flags: u32 LE][Size: u32 LE]
0x000000a4      <Size>      Partition #1 raw payload (starts with 3rdB, 97,738,752 B)
...                         Repeated sequentially for 16 tagged chunks up to chtC
```

- **Recognized Tags (`16`):** `3rdB`, `3rdA`, `roda`, `cfig`, `load`, `uenv`, `adsp`, `aqda`, `pqda`, `rfsB`, `rfsA`, `kerB`, `kerA`, `usig`, `chtD`, `chtC`.
- **Total Size:** `323,840,461` bytes (`0x134d69cd` = last payload offset + `65,536`).

---

## 2. Kernel `uImage` + Dual RSA-2048 Trailer Format (`kerA` / `kerB`)

- **Size:** `2,638,124` bytes (`0x28402c`).
- **Head (`0x00..0x3F`):** Standard U-Boot `64`-byte `image_header` (`IH_MAGIC = 0x27051956`, big-endian; `ih_load = 0x00007fc0`, `ih_ep = 0x00008000` after decompression).
- **Body:** Hardware-LZHS compressed Linux 3.0.13 kernel (`4,432,548` B raw code/data starting at `0x40` of decompressed `vmlinux.bin`).
- **Verification Trailers:**
  - Trailer 1 @ `0x25152c` (`256` B RSA signature + `256` B RSA public certificate/key structure)
  - Trailer 2 @ `0x283f2c` (`256` B RSA signature + `256` B certificate at end of image)

---

## 3. `NFSB` v2 + `dm-bht` Merkle Tree Format (`rfsA`/`rfsB`, `3rdA`/`3rdB`)

Verified byte-for-byte via [scripts/inspect_pkg_and_nfsb.py](../scripts/inspect_pkg_and_nfsb.py) and [scripts/inspect_dmbht_and_boot_scripts.py](../scripts/inspect_dmbht_and_boot_scripts.py):

```
Offset       Size    Field (Little Endian except Signature/Hash)
0x00..0x03   4 B     Magic: "NFSB" (0x4e465342)
0x04..0x07   4 B     Version / flags (`2` -> NFSB v2)
0x08..0x0D   6 B     Header parameters (block sizing / padding)
0x0E..0x1F   18 B    Hash algorithm ASCII string: "md5\0..." (dm-bht uses MD5)
0x20..0x23   4 B     Total verified SquashFS/image 4 KB block count (little-endian? Verified BE/LE!)
...          ...     Root digest (`16` B MD5 in NFSB metadata), offsets, size fields up to 0x67
0x67..0xE6   128 B   Raw 1024-bit RSA Signature S (Big-Endian) over header[0x00:0x67]
0xE7         ...     SquashFS (hsqs) filesystem image aligned to 4096-byte pages
EOF - tree   ...     Two-level dm-bht MD5 Merkle Tree: Level 1 leaf hashes (128 hashes / 4KB block? Exact verified counts below)
```

### Verified Cryptographic & Merkle Values
- **Signing Equation Enforced by `nfsb_rsa_check` (`0xc0028df8`):**
  $$S^{3} \bmod N \stackrel{!}{=} \texttt{0x00}^{96} \parallel \text{SHA-256}(\text{hdr}[0\text{x}00:0\text{x}67])$$
- **Root Partition (`rfsA`/`rfsB`):** `12,514` verified 4 KB SquashFS blocks (`51,257,344` B); root `dm-bht` MD5 digest verified across all `12,514` leaf hashes + intermediate level (`666e1b26...` / `6cc5d821...` — exact hex digests logged in `evidence/01` and `evidence/07`).
- **Application Partition (`3rdA`/`3rdB`):** `23,767` verified 4 KB SquashFS blocks (`97,349,632` B); all `23,767` blocks verified offline without error.

---

## 4. `TPV_MTK2K14PLF` `Autorun.upg` Container Format

```
+-------------------------------------------------------------------+
| 0x000..0x07F (128 B): Filename prefix ("Autorun.upg\0...")        |  <-- Unauthenticated
+-------------------------------------------------------------------+
| 0x080..0x0EF (112 B): AES-128-CBC (Key=0x94102909*4, IV=0)        |
|   -> vendor | "#DH@FiRm" | prod_str | body_len | flags | model    |
| 0x0F0..0x10F (32 B) : AES-128-CBC (Key=0x94102909*4, IV=0)        |  <-- Covered by RSA-2048
|   -> Body MD5 over data[0x80:0xF0] || 0x00^32 || data[0x110:-256] |
+-------------------------------------------------------------------+
| 0x110..end-256: Sequential Chunks                                 |
|   Per chunk: [4B tag][4B flags][4B len]                           |
|              [16B AES_Prod("reserved mtk inc")]                   |
|              [32B AES_Prod(SHA256(payload))]                      |
|              [Payload bytes (XML 'ixml', tgz 'smth', etc.)]       |
+-------------------------------------------------------------------+
| end-256..end (256 B): RSA-2048 PKCS#1 v1.5 Sig over [0x80:-256]   |
+-------------------------------------------------------------------+
```

- **Non-Standard AES Key Derivation (`libdtv_common.so`):** `AES_Prod.key` (`33` bytes including trailing `\n`) is hashed via `MD5()` to produce the `16`-byte AES-128-CBC key; `AES_Prod.iv` (`33` bytes including `\n`) is similarly hashed via `MD5()` to derive the `16`-byte IV.
- **Manifest Schema (`ixml`):** UTF-8 `<UPGRADE><SW><TAG>...</TAG><METHOD>...</METHOD><PATH>...</PATH></SW></UPGRADE>`.
