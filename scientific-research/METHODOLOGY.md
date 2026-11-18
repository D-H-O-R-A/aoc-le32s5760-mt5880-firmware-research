# Methodology

Our reverse-engineering workflow integrates phases 1–5 of the **OWASP Firmware Security Testing Methodology (`FSTM`)**, firmware resiliency verification axes from **NIST SP 800-193**, and supply-chain inventory guidelines from **NIST SP 800-161 Rev. 1** (`SPDX-2.3` + `CycloneDX 1.5`):

## 1. Acquisition & Deterministic Hash Custody
- Source image `LE32S5760_V2.011_V0.2.zip` (`285,061,005` B) unpacked cleanly to `upgrade_loader.pkg` (`323,840,461` B).
- [scripts/firmware_inventory.py](../scripts/firmware_inventory.py) parses the sequential `12`-byte MediaTek PKG descriptor chain starting at `0x98`, hashing every virtual partition stream (`3rdB`..`chtC`), `47` core binaries/modules, and all `4,004` filesystem entries across `appfs1` and `rootfs1` (with POSIX `stat.S_ISREG` checks avoiding `/dev/initctl` FIFO blocking).

## 2. Cryptographic & Structural Extraction (`uImage` Alignment + `NFSB`/`dm-bht`)
- Decompressing `kerA`/`kerB` yields `vmlinux.bin` (`4,432,612` B). Stripping its leading `64`-byte U-Boot `image_header` (`IH_MAGIC=0x27051956`) anchors machine code at ARM32 virtual base `0xc0008000`.
- [scripts/inspect_pkg_and_nfsb.py](../scripts/inspect_pkg_and_nfsb.py) extracts big-endian `e=3` (`0xc04292f0`) and `1024`-bit `N` (`0xc0429370`) directly from `vmlinux.bin`, executing `pow(sig, e, N)` against every `NFSB` header (`rfsA`, `rfsB`, `3rdA`, `3rdB`) plus custom counter-proof `custom_upgrade_loader.pkg`.
- [scripts/inspect_dmbht_and_boot_scripts.py](../scripts/inspect_dmbht_and_boot_scripts.py) walks every `4,096`-byte page of `rfsA` (`12,514` blocks) and `3rdA` (`23,767` blocks), recomputing the two-level `dm-bht` MD5 Merkle root digests.

## 3. Multi-Architecture Machine Code Disassembly (`ARMv7-A` & `Thumb-2`)
- Automated Python harnesses built over **Capstone** ([scripts/disasm_secure_boot_chain.py](../scripts/disasm_secure_boot_chain.py), [disasm_upg_installer.py](../scripts/disasm_upg_installer.py), [disasm_systemmanager_and_nettv.py](../scripts/disasm_systemmanager_and_nettv.py)) disassemble verified function ranges (`0xfb001450`, `0xc0028df8`, `0x098b64`, `0x404f28`, `0x40ae80`, `0x036190`, `0x1889a0`, `0x1db58c`), anchoring claims in reproducible instruction addresses.

## 4. Container & SBOM Synthesis (`UPG` Roundtrip, `SPDX`, `CycloneDX`, Endpoint Audit)
- [scripts/build_safe_rw_upg.py](../scripts/build_safe_rw_upg.py) & [verify_upg_container.py](../scripts/verify_upg_container.py) reconstruct and verify `Autorun.upg` containers (`#DH@FiRm` AES + `MD5(33B)` + SHA-256 + RSA-2048); CI tests replicate the entire roundtrip using ephemeral temp RSA-2048 keys cleanly without proprietary OEM secrets.
- [scripts/metadata_extraction.py](../scripts/metadata_extraction.py) and [sbom_generation.py](../scripts/sbom_generation.py) apply O(N) string/ELF scanning and `openssl x509` inspection across `opcacrt6.pem` (`186` certs) to produce verified endpoint CSVs (`291` URLs), `KERNEL_MODULE_INVENTORY.csv` (`12` `.ko`), `SPDX-2.3`, and `CycloneDX 1.5` manifests.

## 5. Strict Epistemic Tagging Rules
Every analytical statement throughout the repository separates **CONFIRMED** binary facts, **INFERRED** constraints, and **UNKNOWN / UNOBSERVED** runtime/teardown domains ([RESEARCH_SCOPE.md](../RESEARCH_SCOPE.md)).
