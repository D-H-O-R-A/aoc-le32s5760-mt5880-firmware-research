# Literature Review: Smart TV & Embedded Linux Security Foundations

> **BibTeX Database:** [REFERENCES.bib](REFERENCES.bib)

## 1. Synthesis Across Core Research Axis

| Research Axis | Key Literature Benchmark | How the `LE32S5760 / MT5880` Case Study Extends Existing Knowledge |
|---|---|---|
| **Static Embedded Corpus Auditing** | Costin et al. (2014) | Quantifies exact multi-vendor SDK stratification (`MediaTek chiling BSP` + `TPV/Philips 2K13/2K14` + `CERTI Ginga`) inside a single retail Brazilian Smart TV image (`2016`), including exact OpenSSL/libcurl/libxml2 CVE timelines and `186`-CA trust store decay (`opcacrt6.pem`). |
| **Embedded Re-Hosting & SoC Virtualization** | Chen et al. (2016); Wright et al. (2021) | Maps concrete silicon barriers (`OTP eFuse 0xf0008664`, `HW-LZHS 0xf00080b0`, `T8032 8051` co-processor, `6.84 MB` proprietary `dtv_driver.ko`) explaining why automated router emulators cannot natively boot commercial DTV SoCs without peripheral stubbing. |
| **Cryptographic Boot & Verity Implementation Bugs** | Bleichenbacher / Finney (2006); Regenscheid (NIST SP 800-193, 2018) | Combines silicon-level disassembly (`uboot.bin`, `vmlinux.bin`) with an offline `36,281`-block `dm-bht` verifier (`scripts/inspect_dmbht_and_boot_scripts.py`), contrasting textbook RSA `e=3` hardening against fatal updater parser bugs (`libmtkapp.so sub_404f28` `"/dev/nand_10"` `-22 ENOENT`). |
| **Structured Security Methodologies & SBOM** | Guzman (OWASP FSTM); NIST SP 800-161 Rev. 1 (2022) | Operationalizes FSTM Phases 1–5 & cryptographic audit alongside deterministic `SPDX-2.3` and `CycloneDX 1.5` machine-readable SBOMs, explicitly separating confirmed static evidence from unexecuted dynamic claims. |

## 2. Historical Relevance to First/Early-Generation Smart TV Preservation

Early Linux Smart TVs (`2012–2016`) occupied a transitional moment prior to standardized Android TV (`Project Treble`, A/B seamless updates with verified boot 2.0 `AVB`) and WebOS/Tizen container sandboxes. Studying the `MT5880` reveals the exact technical causes of **early consumer electronics obsolescence ("smart TV bit-rot")**:
1. Immutable `NFSB`/`dm-verity` SquashFS locks coupled to legacy `GCC 4.5.1` / `glibc 2.12.2` / `OpenSSL 1.0.0d` prevented third-party community TLS/browser maintenance even after vendors halted updates.
2. Application runtimes (`Opera Presto 6213`, `Adobe AIR Stagecraft 2.5.1` Flash Lite, early `Qt 4.8.3`) hardcoded cloud portal URLs (`ecdinterface.philips.com`, `uiboot.netflix.com`, `youtube.com/tv`) that aged out cleanly at DNS/TLS handshake level within 5–10 years.
