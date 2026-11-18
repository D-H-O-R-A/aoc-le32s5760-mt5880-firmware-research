# Firmware Provenance & Chain of Custody

## 1. Origin and Release Metadata

| Field | Value | Source |
|---|---|---|
| **Distribution File** | `LE32S5760_V2.011_V0.2.zip` | Official consumer/service software package for AOC `LE32S5760/20` |
| **Distribution File Size / SHA-256** | `285,061,005` bytes / `014e235cb9406be9d8d61cc780093d3d5196b8748f72a088b43641dc99d0d1ff` | Verified via [scripts/firmware_inventory.py](../scripts/firmware_inventory.py) |
| **Compressed Payload Entry** | `upgrade_loader.pkg` (`323,840,461` bytes uncompressed; `285,060,819` bytes deflate stream; CRC32 `0x195275a4`) | Zip central directory header |
| **Internal Build Timestamp** | `2016-08-03 14:26:04` (PKG timestamp) / `Thu Aug 4 00:06:04 CST 2016` (Kernel build) | Zip entry timestamp & `vmlinux.bin` banner |
| **Build Host & Builder Identity** | `roylo@TWCLS066` (`gcc version 4.5.1`, source tree `/share/Release_code_use/Roy/release/vm_linux/chiling/...`) | Embedded kernel banner & `.rodata` `__FILE__` paths |
| **ODM Software Lineages** | `SYS_BRAND=Philips`, `SYS_ODM=TPV`, `SYS_VERSION=IDTV0801_002223_9_001_23_001_224`, `TPV_VERSION=000.001.205.145` | `extracted/appfs1/etc/profile` |
| **Third-Party Middleware Provenance** | CERTI Brazil Ginga SBTVD tree (`/home/local/CERTI/vtz/Projects/envision_middleware_clean/...`) | Embedded path string inside `libcurl.so.4.2.0` (`ginga/lib`) |

---

## 2. Independent Reproduction & Custody Verification

Because proprietary OEM images (`LE32S5760_V2.011_V0.2.zip`, `upgrade_loader.pkg`) are excluded from public Git distribution by [DATA_HANDLING_POLICY.md](../DATA_HANDLING_POLICY.md) and [.gitignore](../.gitignore), another researcher verifies they hold **the exact same byte-for-byte artifacts** via a three-step cryptographic check:

1. **Verify Distribution ZIP & Extracted PKG:**
   ```sh
   sha256sum original_firmware/LE32S5760_V2.011_V0.2.zip
   # Expected: 014e235cb9406be9d8d61cc780093d3d5196b8748f72a088b43641dc99d0d1ff
   ```
2. **Run Full Workspace Manifest Check:**
   ```sh
   python3 scripts/hash_verification.py --workspace ..
   ```
   This deterministically recomputes SHA-256 over the outer `.zip`, `upgrade_loader.pkg`, all `16` virtual PKG partition streams (`3rdB`..`chtC`), `uboot.bin`, `uenv`, `vmlinux.bin`, all `12` `.ko` modules, key core ELFs, and all tracked repo scripts (`103` total manifest entries in local validation).
3. **Run Cryptographic Counter-Proof Suite:**
   ```sh
   sh scripts/run_all_proofs.sh ..
   ```
   Verifies NFSB RSA-1024 modulus extraction at VA `0xc0429370`, all `36,281` `dm-bht` 4 KB SquashFS blocks, DLM container crypto, and Capstone disassembly offsets (`evidence/01..07`).

---

## 3. Supply Chain Provenance Findings

Inspecting embedded build paths exposes a layered OEM software supply chain rather than a monolithic AOC codebase:
- **Silicon BSP (`MediaTek` / `chiling`):** Kernel `linux-3.0.13`, Preloader/U-Boot `mt5880`, and `dtv_driver.ko` compiled on build machine `TWCLS066` under engineer tag `Roy` (`chiling` project tree).
- **ODM Chassis & Smart TV Stack (`TPV` / `Philips 2K13/2K14`):** `TPV_MTK2K14PLF` inherits `SYS_BRAND=Philips` and `Philips_2K13_ODM_pdwnc_ext.c` / `TPVision_2k13_d_custom.c`, adapted with AOC branding assets (`offline_demo_AOC`).
- **Regional SBTVD Middleware (`CERTI` / `Envision`):** Brazilian digital TV Ginga engine cross-compiled under `arm_mtk451` alongside standalone `curl-7.21.7` / `openssl-1.0.0d`.
- **Historical Version Context:** No earlier (`V1.x`) or later (`V2.012+`) stock firmware images are present in this workspace; provenance reflects a single verified golden snapshot (`V2.011_V0.2`).
