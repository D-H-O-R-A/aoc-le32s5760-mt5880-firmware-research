# Cryptographic Implementation & Key Management Analysis

> **Cryptographic Proofs:** [evidence/01_pkg_and_nfsb_proof.txt](../evidence/01_pkg_and_nfsb_proof.txt) | [evidence/04_upg_container_crypto_proof.txt](../evidence/04_upg_container_crypto_proof.txt)

## 1. Inventory of Cryptographic Primitives Across Firmware Layers

| Layer | Algorithm & Parameters | Key Source / Custody | Strength / Weaknesses |
|---|---|---|---|
| **Preloader -> U-Boot** | **RSA-2048** (BootROM routine `0xfb0034f0`), Hardware eFuse gating (`0xf0008664 & 0x100000`) | Public key hash fused in OTP hardware silicon | **STRONG** — No software workaround; invalid signature triggers infinite loop at `0xfb000520` |
| **U-Boot -> `kerA`/`kerB`** | **Dual RSA-2048** signatures + certificates (`0x25152c`, `0x283f2c`) | Embedded U-Boot key vs trailer cert | **STRONG** — Blocks modified Linux kernels (`dm-verity` removal attempts fail) |
| **Kernel `nfsb_rsa_check`** | **Raw Textbook RSA-1024 (`e = 3`)** + **SHA-256** (`hdr[0x00:0x67]`) + **2-level `dm-bht` MD5 Merkle Tree** | `128`-B BE Modulus `N @ 0xc0429370`, `e=3 @ 0xc04292f0` | **STRONG against Bleichenbacher padding forgery** (`mpuint_equal` compares full 1024 bits against `0^96 || SHA256`); **Legacy Note:** `1024`-bit RSA & `MD5` tree reflect 2011–2013 ChromeOS `dm-verity` era |
| **`Autorun.upg` Envelope (`libdtv_common.so`)** | **AES-128-CBC (`nopad`)** outer (`0x94102909 * 4`, `IV=0`) + inner (`MD5(33B key)`, `MD5(33B iv)`) + **Body MD5** + **Per-Chunk SHA-256** | Outer key hardcoded via `movw/movt` (`0x098b64`); inner AES + `PriKey_Prod.pem` shipped inside `upgrade_loader.pkg#roda`! | **WEAK KEY CUSTODY** — Outer AES key in `.text`; `33`-byte `\n`-inclusive MD5 quirk; distributing `LT0_UPG_PriKey_Prod.pem` in public PKG exposes LATAM update signing (`SEC-02`) |
| **Internet / App TLS (`libssl.so.1.0.0`)** | **OpenSSL 1.0.0d** (`SSLv3` / `TLSv1.0` / partial `1.1` max, NO TLS 1.2 / 1.3!) | `opcacrt6.pem` (`186` CAs), Netflix `ui_ca.pem` (`4`) & `siab_ca.pem` (`2`), `ginga/lib/security/cacerts` | **SEVERELY OUTDATED** — Missing TLS 1.2+ SHA-256/AEAD suites; `9/186` CAs expired at 2016 release; `57/186` expired <2026 |
| **DRM / Hardware Crypto** | **PlayReady**, **Widevine**, **Marlin**, **HDCP 2.x**, `crypto/mtk_crypto.c`, `libmtk_hw_decrypt.so` | TrustZone (`TRUSTZONE=enable`) + NAND/TEE provisioning | Proprietary DRM internals outside authorized scope of extraction |

---

## 2. Detailed Evaluation of `nfsb_rsa_check` Against Bleichenbacher `e = 3` (2006)

Because `nfsb_rsa_check` uses small public exponent **$e = 3$** and `1024`-bit modulus $N$ without Randomized OAEP/PSS padding, classic audit doctrine asks whether Bleichenbacher's Crypto 2006 low-exponent cube-root forgery applies (see Hal Finney's 2006 formulation).

**Disassembly Verdict ([evidence/02](../evidence/02_secure_boot_chain_disasm.txt)) — IMMUNE:**
Unlike broken ASN.1 DER parsers that stopped after finding `SHA-256` and ignored trailing bytes up to byte 127:
- `0xc0028f8c` computes $out = S^3 \bmod N$ (`128` bytes big-endian).
- `0xc0029000` invokes `mpuint_equal(out_mpi, sha256_mpi)`, comparing **every bit** of the `1024`-bit buffer against $\texttt{0x00}^{96} \parallel \text{SHA-256}$.
- Consequently, all upper `768` bits **must equal zero** after modular exponentiation — trailing non-zero garbage bytes (`\neq 0`) cause immediate mismatch (`mvneq r4, #0 -> -1`). Forging a signature without factoring the `1024`-bit RSA modulus $N$ would require computing a full-width exact cube root modulo $N$ with $768$ leading zero bits, which remains computationally infeasible for arbitrary digests.

---

## 3. Hardcoded Key & `33`-Byte MD5 Quirk (`libdtv_common.so`)

1. **Hardcoded Symmetric Envelope Key:** At `0x098b64..0x098b78` in `libdtv_common.so`, `movw r3, #0x2909` + `movt r3, #0x9410` synthesizes the 32-bit little-endian repeating word `09 29 10 94` (`09291094092910940929109409291094`) paired with zero IV (`00*16`) to unwrap `#DH@FiRm` headers. Because any device owner or analyst holding `libdtv_common.so` recovers this constant deterministically, the outer DLM envelope provides format obscurity rather than confidentiality.
2. **ASCII Hex + Trailing Newline (`\n`) Hash Quirk:** Instead of decoding the 32 hex characters in `TPV_MTK2K14PLF_LT0_UPG_AES_Prod.key/.iv` directly to 16 raw bytes, `libdtv_common.so` hashes all **`33` ASCII bytes (including trailing `0x0a`)** via `MD5()` to derive the runtime AES-128 key and IV (`verified deterministically against both stock key files and custom Autorun.upg` in `evidence/04`).
