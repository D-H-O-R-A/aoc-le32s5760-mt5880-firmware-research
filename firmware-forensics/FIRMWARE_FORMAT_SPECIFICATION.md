# Binary Format Specifications (`PKG`, `NFSB v2 Struct`, `SquashFS 4.0`, `uImage`, `Autorun.upg`)

> **Verification Tools:** [scripts/inspect_pkg_and_nfsb.py](../scripts/inspect_pkg_and_nfsb.py) · [scripts/inspect_dmbht_and_boot_scripts.py](../scripts/inspect_dmbht_and_boot_scripts.py) · [scripts/verify_upg_container.py](../scripts/verify_upg_container.py)

---

## 1. MediaTek `upgrade_loader.pkg` Container Format

```text
Offset          Size        Field
0x00000000      0x98 (152B) Outer PKG header preamble
0x00000098      0x0C (12B)  Partition #1 descriptor: [char tag[4] | uint32_t flags (LE) | uint32_t size (LE)]
0x000000a4      <size>      Partition #1 raw payload (starts at 3rdB, 97,738,752 B)
...                         Repeated sequentially across all 16 chunks ending at chtC (0x134c69cd + 65,536 B = 323,840,461 B)
```

---

## 2. Kernel `uImage` + Dual RSA-2048 Trailer Format (`kerA` / `kerB`)

- **Total Image Size:** `2,638,124` bytes (`0x28402c`).
- **U-Boot Legacy `image_header` (`0x00..0x3F`, `64` B Big-Endian):**
  `ih_magic = 0x27051956`, `ih_size = 4,432,548` B decompressed payload, `ih_load = 0x00007fc0`, `ih_ep = 0x00008000` (meaning stripping `0x40` bytes from decompressed `vmlinux.bin` maps `.text` bit-accurately at ARM32 virtual base `0xc0008000`).
- **Compression & Signature Trailers:** MediaTek HW-LZHS stream (`0xf00080b0`) followed by dual `512`-byte `[256B RSA-2048 signature | 256B X.509/key certificate]` trailers observed at offsets `0x25152c` and `0x283f2c`.

---

## 3. Exact C Struct Reconstruction of `NFSB` v2 (`0xe7` = `231` Bytes) + `dm-bht`

Reconstructed directly from raw hex inspection (`rfsA`/`3rdA` offsets `0x00..0xe6`) paired with [scripts/inspect_dmbht_and_boot_scripts.py](../scripts/inspect_dmbht_and_boot_scripts.py) and kernel `nfsb_rsa_check` (`0xc0028df8`):

```c
#pragma pack(push, 1)
struct nfsb_header_v2 {
    char     magic[4];              /* +0x00: "NFSB" (0x4e465342) */
    uint8_t  version;               /* +0x04: 0x02 (NFSB v2) */
    uint32_t fs_offset_sectors_be;  /* +0x05: BE 512B sectors -> 0x00000008 (4,096 B) */
    uint32_t fs_size_sectors_be;    /* +0x09: BE 512B sectors -> rfsA: 0x00018710 (51,257,344 B),
                                                                3rdA: 0x0002e6b8 (97,349,632 B) */
    uint8_t  tree_depth;            /* +0x0d: 0x02 (2-level dm-bht Merkle tree) */
    char     hash_algo[16];         /* +0x0e: "md5\0..." (null-padded 16B) */
    uint32_t hash_tree_sectors_be;  /* +0x1e: BE 512B sectors -> rfsA: 0x00000190 (204,800 B),
                                                                3rdA: 0x000002f0 (385,024 B) */
    uint32_t block_sectors_be;      /* +0x22: BE 512B sectors -> 0x00000008 (4,096 B page) */
    char     root_hexdigest[64];    /* +0x26: ASCII MD5 root digest (32 chars + null pad) */
    uint8_t  pad_0x66;              /* +0x66: 0x00 (end of 0x67 = 103B signed payload) */
    uint8_t  rsa_sig_1024_be[128];  /* +0x67..0xe6: Big-Endian 1024-bit RSA Signature S */
};                                  /* sizeof == 231 bytes (0xe7) */
#pragma pack(pop)
```

### Verified Partition Geometry & Cryptographic Validation Values
| Partition | `fs_size` (`4KB` Blocks) | Merkle Layout (`4KB` Pages) | Signed `root_hexdigest` (`+0x26`) | RSA Verification Equation (`0xc0028df8`) |
|---|---|---|---|---|
| `rfsA` / `rfsB` | `12,514` (`51,257,344` B) | `50` pages (`1` Level-0 parent + `49` Level-1 leaf pages @ `256` MD5/page) | `6cc5d821e2e914aec01a1db58fcca389` | $S^3 \bmod N \stackrel{!}{=} 0^{96} \parallel \text{SHA-256}(\text{hdr}[0:0\text{x}67])$ |
| `3rdA` / `3rdB` | `23,767` (`97,349,632` B) | `94` pages (`1` Level-0 parent + `93` Level-1 leaf pages @ `256` MD5/page) | `666e1b26ae2e81a681c4f510bd98bfca` | Exact `1024`-bit `mpuint_equal` (`0xc0029000`) -> `36,281/36,281` blocks PASS |

---

## 4. `TPV_MTK2K14PLF` `Autorun.upg` Container Format (`#DH@FiRm`)

```text
+-----------------------------------------------------------------------+
| 0x000..0x07F (128 B): Unauthenticated filename prefix ("Autorun.upg") |
+-----------------------------------------------------------------------+
| 0x080..0x0EF (112 B): AES-128-CBC (K = 09291094*4, IV = 0x00*16)       |
|   vendor[4] | "#DH@FiRm"[8] | prod_id[60] | body_len(u32) | flags | model |
| 0x0F0..0x10F (32 B) : AES-128-CBC (K = 09291094*4, IV = 0x00*16)       |
|   Decrypted[0:16] == MD5(data[0x80:0xF0] || 0x00^32 || data[0x110:-256])|
+-----------------------------------------------------------------------+
| 0x110..end-256: Chunks = [tag:4B][flags:u32][len:u32]                  |
|   [16B AES_Prod("reserved mtk inc")] [32B AES_Prod(SHA256(payload))]   |
|   Where K_prod = MD5(33B AES_Prod.key), IV_prod = MD5(33B AES_Prod.iv) |
+-----------------------------------------------------------------------+
| end-256..end (256 B): RSA-2048 PKCS#1 v1.5 Sig over data[0x80:-256]    |
+-----------------------------------------------------------------------+
```
