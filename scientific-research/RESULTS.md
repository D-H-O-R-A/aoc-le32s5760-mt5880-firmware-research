# Empirical Results Summary

> **Machine-Readable Ledger:** [VALIDATION_RESULTS.csv](VALIDATION_RESULTS.csv) | **Comparison Metrics:** [comparative-analysis/comparison_metrics.json](../comparative-analysis/comparison_metrics.json)

## 1. Quantitative Forensic & Cryptographic Findings

| Metric / Artifact | Measured Result | Verification Script / Source |
|---|---|---|
| **Distribution Zip / PKG Sizes** | `285,061,005` B (`LE32S5760_V2.011_V0.2.zip`) -> `323,840,461` B (`upgrade_loader.pkg`, `16` partitions) | `firmware_inventory.py`, `FIRMWARE_HASH_MANIFEST.txt` |
| **Bank A/B Factory Mirror Parity** | `100%` bit-identical (`kerA==kerB` `2,638,124` B; `rfsA==rfsB` `51,466,240` B; `3rdA==3rdB` `97,738,752` B; `chtC==chtD` `65,536` B) | `firmware_comparison.py`, `comparison_metrics.json` |
| **RSA-1024 `NFSB` Signature Verification** | `4/4` stock partitions PASS (`3rdB`, `3rdA`, `rfsB`, `rfsA`); modified `custom_upgrade_loader.pkg` FAILS (`RSA_exact_match=False`) | `inspect_pkg_and_nfsb.py`, `evidence/01` |
| **Complete `dm-bht` MD5 Merkle Tree Blocks** | `36,281 / 36,281` `4 KB` blocks verified (`23,767` in `3rdA`, `12,514` in `rfsA`; `0` mismatches) | `inspect_dmbht_and_boot_scripts.py`, `evidence/07` |
| **Preloader Gate & Infinite Trap Verified** | OTP fuse check `0xf0008664 & 0x100000` -> `bl 0xfb0034f0` -> `"not secure loader\n"` -> infinite halt `0xfb000520` | `disasm_secure_boot_chain.py`, `evidence/02` |
| **8-Second Upgrade Failure (`sub_404f28`)** | `<METHOD>PART</METHOD>` (`r6==0`) builds `"/dev/nand_10"` -> `-22 ENOENT`; `3rdp` skips A/B switch (`0x40ae80`) | `disasm_upg_installer.py`, `evidence/03` |
| **Safe RW UPG Container Verification** | `19,905`-B `<TAG>smth</TAG><METHOD>FILE</METHOD>` `Autorun.upg` verified across RSA-2048, dual AES, Body MD5, `"reserved mtk inc"`, SHA-256 | `verify_upg_container.py`, `evidence/04` |
| **Kernel Metadata & Module Audit** | `Linux 3.0.13` (`gcc 4.5.1`), `CONFIG_IKCONFIG=n`, `381` kernel source paths, `8` `dtv_driver.ko` paths, `12` `.ko` modules (`vermagic` uniform) | `metadata_extraction.py`, `KERNEL_MODULE_INVENTORY.csv` |
| **Filesystem, SBOM, Endpoint & CA Audits** | `4,004` filesystem rows (`416`+`2,919` regular files); `27` SPDX / `26` CycloneDX components; `291` static URLs; `186` Opera CAs (`9` exp <=`2016`, `57` exp <`2026`) | `FIRMWARE_METADATA.json`, `SBOM.*.json`, `FILESYSTEM_INVENTORY.csv` |
| **Laboratory Overlay Patch Audit** | `21` added + `4` modified files (`staging_rootfs` vs `rootfs1`), audited for ES5 syntax, `BusyBox v1.15.3`, & `QtQuick 1.1` compatibility | `firmware_comparison.py`, `inspect_runtime_engines.py`, `evidence/05` |
