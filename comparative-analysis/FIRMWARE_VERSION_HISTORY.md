# Firmware Version History (`AOC LE32S5760/20`)

> **Scope Limitation:** Only one official factory distribution archive (`LE32S5760_V2.011_V0.2.zip`) was available inside the workspace during this research cycle. Neither earlier historical firmware (`V1.x` / `V2.00x`) nor subsequent vendor patches (`V2.012+`) were acquired. Consequently, inter-release longitudinal regression tracking is explicitly scoped as **UNAVAILABLE** rather than extrapolated from external rumors.

---

## 1. Confirmed Version Identifiers Embedded Inside `V2.011_V0.2`

| Version Layer | Exact Identifier String | Build Timestamp | Evidence File |
|---|---|---|---|
| **Commercial Package** | `LE32S5760_V2.011_V0.2` (`upgrade_loader.pkg`) | `2016-08-03 14:26:04` | Zip central directory |
| **Platform System Tag** | `SYS_VERSION=IDTV0801_002223_9_001_23_001_224` | — | `extracted/appfs1/etc/profile` |
| **TPV ODM Release Tag** | `TPV_VERSION=000.001.205.145` (`SYS_ODM=TPV`, `SYS_BRAND=Philips`) | — | `extracted/appfs1/etc/profile` |
| **Linux Kernel** | `Linux version 3.0.13` (`roylo@TWCLS066`, `gcc 4.5.1`, `#1 SMP PREEMPT`) | `Thu Aug 4 00:06:04 CST 2016` | `scratch/vmlinux.bin` |
| **BusyBox Userland** | `BusyBox v1.15.3` | `2012-06-06 18:54:15 CST` | `extracted/appfs1/bin/busybox` |
| **Legacy Reference Traces** | `GCC for MediaTek 4.4.2-20100324` (`libz.so.1.2.3`), `/lib/modules/2.6.27` check (`rm_usb_mod.sh`), `Philips_2K13_ODM_pdwnc_ext.c` | `2010–2013` SDK strata | Compiled `.rodata` & driver paths |

---

## 2. Intra-Release Variants Studied Instead

To achieve concrete comparative evidence within the verified dataset (`comparison_metrics.json`), comparative binary analysis examines:
1. **A/B Active-Standby Factory Mirrors:** `kerA` vs `kerB`, `rfsA` vs `rfsB`, `3rdA` vs `3rdB`, and `chtC` vs `chtD` inside `upgrade_loader.pkg`.
2. **Stock `upgrade_loader.pkg` vs. Laboratory `custom_upgrade_loader.pkg`:** Quantifying exact partition-level diffs that fail `nfsb_rsa_check`.
3. **Stock `rootfs1` vs. Laboratory `staging_rootfs` / `custom_payload`:** Auditing the `21` added + `4` modified UI/browser files (`mtd12` overlay target).
