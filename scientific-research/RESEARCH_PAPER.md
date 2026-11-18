# Cryptographic Chain-of-Trust, Upgrade Container Defects, and Safe Preservation Boundaries in First-Generation Linux Smart Televisions: A Forensic Case Study of the AOC `LE32S5760/20` (`MediaTek MT5880`)

**Author:** D-H-O-R-A Firmware Research (`aoc-le32s5760-mt5880-firmware-research`)  
**Target Platform:** AOC `LE32S5760/20` (`TPV MTK2K14PLF` / MediaTek `MT5880` `ARMv7-A` / Linux `3.0.13`)  
**Analyzed Release:** `LE32S5760_V2.011_V0.2.zip` (`285,061,005` B, `SHA-256: 014e235c...`) -> `upgrade_loader.pkg` (`323,840,461` B)  

> Standalone academic sections: [Abstract](ABSTRACT.md) · [Methodology](METHODOLOGY.md) · [Results](RESULTS.md) · [Discussion](DISCUSSION.md) · [Limitations](LIMITATIONS.md) · [Conclusion](CONCLUSION.md) · [BibTeX References](REFERENCES.bib)

---

## 1. Introduction

Early-generation Linux Smart Televisions shipped between 2012 and 2016 present an illuminating tension between **hardware-enforced DRM/firmware integrity** and **rapid software stack obsolescence**. When retail owners attempt to update legacy browsers, restore streaming clients (Netflix, YouTube), or deploy custom root partitions onto aging devices, updates fail silently behind opaque UI progress dialogs—or risk permanent flash corruption when hardware recovery programmers are unavailable.

Motivated by a reproducible failure on the **AOC `LE32S5760/20`** (`TPV MTK2K14PLF` / `MT5880`) in which invoking `Home > Setup > Software Update > Local` against a repacked `Autorun.upg` hung on `"..."` for approximately `8` seconds before aborting with `"REINICIAR OU TENTAR NOVAMENTE"`, we conducted an end-to-end static binary investigation spanning the `uboot.bin` SRAM Preloader, the decompressed `Linux 3.0.13` kernel (`vmlinux.bin`), the userspace installer (`libmtkapp.so`, `libdtv_common.so`), and the `Qt 4.8.3` / `Opera Presto 6213` application layer.

This monograph synthesizes our complete methodology, cryptographic proofs (`36,281` Merkle-tree blocks verified), security & SBOM findings (`SEC-01`–`SEC-09`), and non-destructive `mtd12` preservation strategy while maintaining strict epistemic separation between binary-confirmed artifacts and unprobed hardware/wire properties.

---

## 2. Background & Related Literature

Our analysis extends four converging research threads (detailed in [RELATED_WORK.md](RELATED_WORK.md) and [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md)):
1. **Large-Scale Embedded Firmware Audits:** Costin et al. (2014) demonstrated how shared OEM SDKs propagate obsolete binaries and key-management mistakes across vendor brands. Inside this `2016` AOC build, embedded strings expose layered provenance spanning MediaTek's `chiling` BSP (`linux-3.0.13`), `TPV/Philips` `2K13/2K14` drivers (`SYS_BRAND=Philips`, `Philips_2K13_ODM_pdwnc_ext.c`), and Fundação CERTI's Brazilian ISDB-Tb `Ginga` middleware (`envision_middleware_clean`).
2. **Embedded Re-Hosting Barriers:** Chen et al. (`Firmadyne`, 2016) and Wright et al. (2021) formalized why hardware-coupled embedded images resist generic QEMU emulation. On `MT5880`, direct SRAM register polling (`0xf0008664`, `0xf00080b0`), 8051 standby handshakes (`T8032`), dual-channel DDR calibration, and a monolithic `6.84 MB` proprietary `dtv_driver.ko` prevent vanilla full-system emulation without custom MMIO stubs ([emulation/](../emulation/EMULATION_RESEARCH.md)).
3. **Low-Exponent RSA (`e=3`) Verification Pitfalls:** Bleichenbacher & Finney (2006) showed how permissive PKCS#1 v1.5 parsers allow cube-root signature forgery when trailing padding goes unchecked. We audit MediaTek's backported `dm-verity` `NFSB` checker (`nfsb_rsa_check`) directly against this attack class.
4. **Resiliency & Supply Chain Frameworks:** We align verification with **NIST SP 800-193** (*Protect*, *Detect*, *Recover*), **OWASP FSTM**, and **NIST SP 800-161 Rev. 1** (`SPDX-2.3` + `CycloneDX 1.5`).

---

## 3. Methodology Overview

Full reproducible procedures appear in [METHODOLOGY.md](METHODOLOGY.md) and [EXPERIMENTAL_PROCEDURES.md](EXPERIMENTAL_PROCEDURES.md):
- **Deterministic Extraction & Inventory:** Unpacking `LE32S5760_V2.011_V0.2.zip` and parsing `16` tagged partitions (`0x98+`) yielded exact SHA-256 digests (`103` workspace/repo items tracked in `FIRMWARE_HASH_MANIFEST.txt`) and `4,004` filesystem records across `appfs1` and `rootfs1`.
- **`uImage` Virtual Base Realignment (`0x40` Shift):** Stripping the leading `64`-byte U-Boot header (`0x27051956`, `ep=0x8000`) from decompressed `vmlinux.bin` aligned ARM32 virtual addresses at `0xc0008000`, resolving every `nfsb_rsa_check` symbol and literal pointer.
- **Automated Capstone & OpenSSL Proofs:** Seven standalone proof scripts ([scripts/run_all_proofs.sh](../scripts/run_all_proofs.sh)) generate deterministic evidence logs (`evidence/01..07`) audited alongside CI `unittest` roundtrips.

---

## 4. Empirical Architecture & Cryptographic Results

### 4.1 Multi-Stage Chain of Trust (`uboot.bin` -> `vmlinux.bin` -> `dm-bht`)
1. **BootROM / Preloader OTP Trap:** Capstone Thumb-2 disassembly (`0xfb001450..0xfb000530`) proves Preloader inspects hardware OTP eFuse `0xf0008664 & 0x100000` and `[0xfb0053bc] == 1`, invoking BootROM RSA-2048 (`0xfb0034f0` on `+0x6c4b0`). Mismatch outputs `"not secure loader\n"` and enters an unrecoverable infinite loop (`0xfb000520: b #0xfb000520`).
2. **Kernel `uImage` Protection:** `kerA` and `kerB` (`2,638,124` B, `100%` identical SHA-256) embed dual `512`-byte RSA-2048 signature/certificate trailers (`0x25152c`, `0x283f2c`) preventing custom kernels from removing `dm-verity`.
3. **`NFSB` v2 + Exact `e=3` RSA-1024 + `36,281`-Block Merkle Proof:**
   Stripping `0x40` bytes reveals `e = 3` (`0xc04292f0`) and `1024`-bit `N` (`0xc0429370`). In `nfsb_rsa_check` (`0xc0028df8`), MediaTek hashes the first `0x67` bytes of each `NFSB` header with SHA-256 and enforces **full `1024`-bit equality** (`mpuint_equal @ 0xc0029000`):
   $$S^{3} \bmod N \stackrel{!}{=} \texttt{0x00}^{96} \parallel \text{SHA-256}(\text{hdr}[0\text{x}00:0\text{x}67])$$
   Because trailing garbage bytes cannot sit above bit `256` without failing `mpuint_equal`, Bleichenbacher cube-root forgery is mathematically blocked. Offline evaluation confirms `4/4` factory partitions (`3rdB`, `3rdA`, `rfsB`, `rfsA`) pass RSA verification and match every `4 KB` block across the 2-level `dm-bht` MD5 tree (`12,514` blocks in `rfsA` + `23,767` in `3rdA` = `36,281/36,281`), whereas `build/custom_upgrade_loader.pkg` fails deterministically (`RSA_exact_match=False`).

### 4.2 Root Cause of the 8-Second `Autorun.upg` Abort & Key Quirk Recovery
Disassembly of `libdtv_common.so` (`dlm_locate_codefile_hdr @ 0x098b64`) and `libmtkapp.so` (`sub_404f28`, `_phm_upg_model_start_upgrade`) explains both the `.upg` cryptosystem and empirical flash failure:
- **Outer `#DH@FiRm` Layer:** AES-128-CBC using hardcoded `0x94102909 * 4` (`IV=0`), zeroed-slot body MD5 (`0xF0`), per-chunk `AES_Prod` derived by `MD5()` over **`33`-byte `\n`-inclusive key/IV strings**, `"reserved mtk inc"`, chunk SHA-256, and outer `256`-byte RSA-2048 (`cmp r8, #0x20`).
- **The `-22 ENOENT` Defect (`sub_404f28`):** Choosing `<METHOD>PART</METHOD>` (`r6 == 0` @ `0x404f54`) formats `"/dev/nand_10"` instead of `"/dev/mtd10"`, causing `c_fm_erase_flash_part` to abort with `-22 ENOENT` after ~`8` seconds (`"REINICIAR OU TENTAR NOVAMENTE"`). Even switching to `<METHOD>PMTD</METHOD>` triggers `0x40ae80`, which skips A/B bank toggling on standalone `3rdp` flashes.

### 4.3 Security, Trust Store & SBOM Posture (`SEC-01`–`SEC-09`)
Full findings appear in [security/SECURITY_FINDINGS.md](../security/SECURITY_FINDINGS.md) and [sbom/KNOWN_VULNERABILITIES.md](../sbom/KNOWN_VULNERABILITIES.md):
- **Privileges (`SEC-01`):** Single `root:x:0:0` entry in `/etc/passwd`, zero `/etc/shadow`, zero MAC, `ttyUSB0` conditional auto-root script.
- **Public-Archive Private Key Exposure (`SEC-02`):** `upgrade_loader.pkg#part:roda` includes `LT0_UPG_PriKey_Prod.pem` and `COM_UPG_PriKey_Devt.pem` alongside public keys (mitigated only on boot by absent BootROM/`ker`/`NFSB` keys).
- **TLS & CA Decay (`SEC-03`, `SEC-04`):** `OpenSSL 1.0.0d` + `libcurl 7.21.7` limit HTTPS to TLS 1.0/1.1; Opera `opcacrt6.pem` (`186` certs) contains `9` anchors already expired in `2016` and `57` expired prior to `2026` alongside `WoSign`, omitting modern `ISRG Root X1` / `Global Root G2`.
- **Legacy Dependency Ceiling:** `Linux 3.0.13`, `BusyBox 1.15.3`, `glibc 2.12.2` (`GCC 4.5.1`), `Qt 4.8.3`, Opera `Presto 6213`, Flash `stagecraft`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`.

---

## 5. Safe Customization Boundary (`mtd12` `/3rd_rw`) & Limitations

Rather than risking unrecoverable NAND corruption on `load`/`ker`/`rfs`/`3rd` without a chip programmer, [scripts/build_safe_rw_upg.py](../scripts/build_safe_rw_upg.py) packages lock-compliant `19,905`-byte `<TAG>smth</TAG><METHOD>FILE</METHOD>` containers extracting purely onto writable UBIFS `mtd12` (`/3rd_rw`), interacting cleanly with `dtv_svc` (`customer_version` sentinel @ `0x036190`), `libnettv.so` (`_imnettv_copydata @ 0x1889a0`), and `SystemManager` (`dynqml @ 0x1db58c`). Within `/3rd_rw`, our audited `custom_payload/` replaces `HSMain.qml` and hardens Opera `urlfilter.ini` / ES5 `user.js` safely—while proving natively why TLS 1.3 and Chromium porting exceed platform limits.

All key physical and runtime boundaries—unverified `715G7904M` PCB silkscreen (`0` firmware hits), missing teardown photography, unexecuted `qemu-arm` emulation, and uncaptured live `tcpdump` telemetry—are preserved transparently in [LIMITATIONS.md](LIMITATIONS.md) so subsequent researchers can extend rather than re-verify every finding.
