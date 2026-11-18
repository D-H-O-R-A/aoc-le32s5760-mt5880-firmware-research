# Update Integrity Analysis

## 1. Multi-Layer Hash Verification Pipeline

Every `.upg` container passes through three independent hash/integrity layers before payload extraction reaches flash:

1. **DLM Body Zero-Slot MD5 (`0xF0..0x10F`):**
   - Covers bytes `[0x80 : end-256]` with the `32`-byte MD5 container slot itself zeroed (`0x00 * 32`).
   - Verified via `build_safe_rw_upg.py` / `verify_upg_container.py` against both decrypted slot and recomputed digest.
2. **Per-Chunk Authenticator & `SHA-256` (`+12..+60` inside every chunk):**
   - Bytes `[+12:+28]` decrypt under `AES-128-CBC(K=MD5(33B AES_Prod.key), IV=MD5(33B AES_Prod.iv))` to `"reserved mtk inc"` (`16` bytes exact ASCII check).
   - Bytes `[+28:+60]` decrypt under the same product AES key/IV to the exact `32`-byte `SHA-256(payload)` digest.
   - Any byte corruption inside `ixml` or payload chunks aborts installation before flash erase begins.
3. **Whole-Body `SHA-256` Covered by RSA-2048 (`[0x80 : end-256]`):**
   - Signed end-to-end by the `256`-byte RSA trailer (`end-256 : end`), preventing chunk reordering, XML substitution, or length manipulation without a matching private key.

---

## 2. Post-Install Runtime Integrity Gap (`/3rd_rw` vs `rfsA`/`3rdA`)

- **During Flash:** `Autorun.upg` integrity protects transfer from USB to NAND.
- **After Flash (`MTD` Runtime):**
  - If an update writes to `rfsA`/`B` or `3rdA`/`B` (`mtd6`/`7`/`9`/`10`), Linux **continues enforcing `NFSB` RSA-1024 + `dm-bht` MD5 on every `4 KB` block read** (`nfsb_rsa_check`), causing corrupt/unofficial SquashFS images to fail even if flashed successfully.
  - Conversely, `mtd12` (`/3rd_rw`) uses **UBIFS (`-o no_chk_data_crc`) without `dm-verity`**, trusting whatever `<TAG>smth</TAG><METHOD>FILE</METHOD>` placed inside `/3rd_rw` on every future reboot.
