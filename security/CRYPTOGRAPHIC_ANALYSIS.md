# Cryptographic Implementation, PKI & Key-Management Analysis

> **Primary Proofs:** [evidence/01_pkg_and_nfsb_proof.txt](../evidence/01_pkg_and_nfsb_proof.txt) · [evidence/04_upg_container_crypto_proof.txt](../evidence/04_upg_container_crypto_proof.txt) · [evidence/07_dmbht_and_boot_scripts_audit.txt](../evidence/07_dmbht_and_boot_scripts_audit.txt)

## 1. End-to-End Cryptographic Architecture Across Layers

| Layer | Primitives & Key Lengths | Key Storage / Custody | Mathematical Verdict & Vulnerability Notes |
|---|---|---|---|
| **Preloader -> U-Boot** | **RSA-2048** (BootROM `0xfb0034f0`), Hardware OTP Fuse (`0xf0008664 & 0x100000`) | OTP public key hash fused in MT5880 silicon | **STRONG:** Blocks boot before DRAM/USB on mismatch (`0xfb000520` spin halt). |
| **U-Boot -> `kerA`/`kerB`** | **Dual RSA-2048** trailers (`256B` sig + `256B` cert @ `0x25152c`, `0x283f2c`) | U-Boot embedded public key | **STRONG:** Prevents flashing patched kernels (`dm-verity` removal). |
| **`NFSB` v2 + `dm-bht` (`vmlinux`)** | **Raw RSA-1024 (`e=3`)** over `SHA-256(hdr[0:0x67])` + **2-level MD5 Merkle Tree** (`36,281` `4KB` blocks) | `e @ 0xc04292f0`, `N @ 0xc0429370` in read-only kernel `.rodata` | **IMMUNE to Bleichenbacher `e=3` Forgery** (`mpuint_equal` full `1024`-bit check). *Legacy note:* `1024`-bit RSA & `MD5` tree reflect 2011–2013 CE design limits. |
| **`Autorun.upg` (`libdtv_common`)** | **AES-128-CBC (`nopad`)** outer (`0x94102909*4`, `IV=0`) + inner (`MD5(33B AES_Prod)`) + Body MD5 + Chunk SHA-256 + **RSA-2048 PKCS#1 v1.5** (`cmp r8, #0x20`) | Hardcoded `.text` outer AES + `/ro_data` (`roda` partition!) | **WEAK KEY CUSTODY (`SEC-02`/`SEC-07`):** Publicly distributed `roda` image leaks `LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`, and `AES_Prod.key/.iv`. |
| **TLS & Web PKI (`OpenSSL` / `Opera`)** | **`OpenSSL 1.0.0d`** (TLS 1.0/1.1 ceiling) + `opcacrt6.pem` (`186` CAs) | Static SquashFS libs & PEM/DAT stores | **CRITICALLY OBSOLETE (`SEC-03`/`SEC-04`):** Zero TLS 1.2/1.3; trusts `MD2` (`1000b`), `MD5`, `SHA-1`, `<2048b` RSA & expired roots. |

---

## 2. Bleichenbacher `e = 3` (2006) Immunity Proof in `nfsb_rsa_check`

In Crypto 2006 (documented by Hal Finney, 2006), RSA signatures using small exponent $e = 3$ fall to pencil-and-paper cube-root forgery if a verifier inspects ASN.1 `00 01 FF...FF 00 ASN1 HASH` without checking trailing bytes up to modulus bit width (constructing $S = \lfloor \sqrt[3]{M_{\text{prefix}} \parallel \text{garbage}} \rfloor$).

Disassembling `nfsb_rsa_check` (`0xc0028df8` in `vmlinux.bin`) proves MediaTek bypassed DER length parsing entirely via **exact fixed-width big-integer equality (`mpuint_equal @ 0xc0029000`)**:
$$\text{Compute } \text{out} = S^3 \bmod N \quad (\text{via } \texttt{mpuint\_modexp @ 0xc0189f2c})$$
$$\text{Require } \text{out} \stackrel{?}{=} \texttt{0x00}^{96} \parallel \text{SHA-256}(\text{hdr}[0\text{x}00:0\text{x}67])$$

Because the upper **`768` bits MUST equal strictly `0x00`**, no arbitrary trailing garbage bytes can exist anywhere inside $\text{out}$, making $\sqrt[3]{\texttt{0x00}^{96} \parallel H \pmod N}$ as hard as inverting raw textbook RSA for arbitrary target $H$ modulo the $1024$-bit $N$.

---

## 3. Complete Cryptographic Audit of `opcacrt6.pem` (`186` Root Certificates)

Running `OpenSSL 3.0.13` `x509 -noout -text` sequentially over all `186` PEM certificates inside `extracted/rootfs1/nettv/opera/opera_dir/opcacrt6.pem` yields the exact empirical algorithm and key-strength distribution below:

| Audit Metric | Count | Forensic Highlights & Affected Issuers |
|---|---|---|
| **Total PEM Certificate Blocks** | `186` | `298,013` B bundle (`opcacrt6.dat` binary mirror `235,280` B) |
| **OpenSSL 3.0 Parse Errors** | **`17`** | Obsolete/malformed X.509 structures rejected outright by modern OpenSSL 3 |
| **`md2WithRSAEncryption` Roots** | **`1`** | `RSA Data Security, Inc.` (expired `Jan 7 2010`), **`1000`-bit RSA key** |
| **`md5WithRSAEncryption` Roots** | **`7`** | `BBC FMT Greenhouse` (`2048b`, exp `2028`), `Equifax Secure eBusiness` & `Global eBusiness CA-1` (`1024b`), `GTE CyberTrust` (`1024b`), `NetLock` (`1024b`/`2048b`) |
| **`sha1WithRSAEncryption` Roots** | **`106`** | **`62.7%`** of all `169` parsed roots sign using collision-weakened `SHA-1` |
| **`sha256` / `sha384` RSA & ECDSA** | `43` SHA-256 RSA · `4` SHA-384 RSA · `8` ECDSA | Only modern minority (`32.5%` of parsed subset) |
| **RSA Key Modulus `< 2048` bits** | **`18`** | `17` x **`1024`-bit** (`VeriSign Class 1/2/3`, `Entrust`, `Equifax`, `DSTCA`, `Google Internet Authority` exp `2013`, `Thawte`, `ValiCert`) + `1` x **`1000`-bit** |
| **Temporal Expiration Decay** | **`9` `<= 2016`** · **`57` `< 2026`** | `9` roots (`A-Trust-nQual-03`, `Juur-SK`, etc.) shipped **already expired in Aug 2016**; `57` expired pre-`2026`; `WoSign` retained; `ISRG Root X1` absent |
