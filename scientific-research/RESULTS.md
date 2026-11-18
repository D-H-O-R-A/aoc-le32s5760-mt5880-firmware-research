# Empirical Results Summary

> **Verification Ledger:** [VALIDATION_RESULTS.csv](VALIDATION_RESULTS.csv) | **Comparison Metrics:** [comparative-analysis/comparison_metrics.json](../comparative-analysis/comparison_metrics.json)

| Category | Verified Measurement / Finding | Verification Script / Command |
|---|---|---|
| **Factory Archive & PKG Table** | `LE32S5760_V2.011_V0.2.zip` (`285,061,005` B, `SHA256: 014e235c...`) -> `upgrade_loader.pkg` (`323,840,461` B, `16` partitions, `cfig` MTD slots `1..30`) | `scripts/firmware_inventory.py`, `evidence/01` |
| **A/B Bank Factory Mirror Parity** | `kerA==kerB` (`2.63 MB`), `rfsA==rfsB` (`51.46 MB`), `3rdA==3rdB` (`97.73 MB`), `chtC==chtD` (`65 KB`) — `100%` bit-identical SHA-256 | `scripts/firmware_comparison.py` |
| **SoC CPU & DRAM Empirical Proof** | **ARM Cortex-A9 SMP (`451_vfp_ca9`, no `SDIV`)**; `uenv` `.data`: `global_magic=0x53965368`, **`global_kernel_dram_size=0x21fb9000` (`543.72 MiB`)** -> total physical DDR `> 543.7 MiB` | `readelf -h -d -A -s` on `SystemManager`, `netflix`, `uenv` |
| **Preloader & Kernel RSA-1024 / Merkle** | OTP trap `0xf0008664 & 0x100000 -> 0xfb000520`; `vmlinux` aligned (`-0x40` `uImage`) -> `4/4` `NFSB` headers PASS + **`36,281 / 36,281`** `4 KB` `dm-bht` blocks PASS (`custom_upgrade_loader.pkg` = `False`) | `scripts/inspect_pkg_and_nfsb.py`, `inspect_dmbht_and_boot_scripts.py`, `evidence/01`, `02`, `07` |
| **8-Second Update Abort (`sub_404f28`)** | `<METHOD>PART</METHOD>` (`r6==0 @ 0x404f54`) formats `"/dev/nand_10"` (`-22 ENOENT`); `_phm_upg_model_start_upgrade` (`0x40ae80`) skips bank toggle for `3rdp` | `scripts/disasm_upg_installer.py`, `evidence/03` |
| **`Autorun.upg` Crypto & RW Delivery** | Hardcoded outer key `09291094*4`, zeroed MD5, `33`-B `\n`-hashed `AES_Prod`, `"reserved mtk inc"`, SHA-256, RSA-2048 (`cmp r8, #0x20`); `19,905`-B `smth` `.upg` targets `mtd12` (`/3rd_rw`) cleanly | `scripts/build_safe_rw_upg.py`, `verify_upg_container.py`, `evidence/04` |
| **ELF Binary Hardening (`17` ELFs)** | **`0/16` OEM/app ELFs** enable `RELRO`, `Canary`, `FORTIFY`, or executable `PIE` (only `NX RW` enabled; `libc-2.12.2.so` has `PARTIAL RELRO` + `Canary` + `75` `_chk`) | `LC_ALL=C readelf -h -l -d --dyn-syms` (`SECURITY_ASSESSMENT.md`) |
| **X.509 Trust Store (`opcacrt6.pem`)** | `186` certs: **`17`** OpenSSL 3 parse errors, **`1`** `MD2` (`1000b`), **`7`** `MD5`, **`106`** `SHA-1`, **`18`** RSA`<2048b`, **`9`** expired `<=2016`, **`57`** expired `<2026` | `openssl x509 -noout -text` (`CRYPTOGRAPHIC_ANALYSIS.md`) |
| **Kernel, Modules, FS, Endpoints, SBOM** | `Linux 3.0.13` (`console=ttyMT0,115200n1`, `381` kernel paths, `8` `dtv_driver.ko` paths, `12` `.ko`); `4,004` FS rows; `291` static URLs; `SPDX-2.3` (`27` pkgs) + `CycloneDX 1.5` (`26` comps) | `metadata_extraction.py`, `sbom_generation.py` |
| **Automated CI & Hash Integrity** | `10 / 10` `unittest` cases PASS (`0.650s`); `58/58` CI repo hashes & `105/105` workspace hashes PASS; GitHub Actions CI `✓` | `tests/test_research_suite.py`, `hash_verification.py` |
