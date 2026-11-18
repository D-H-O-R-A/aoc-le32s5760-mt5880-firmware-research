# Historical Platform Strata & Changelog Forensics

## 1. Evidence-Based Archaeological Timeline Within `V2.011_V0.2`

In the absence of official AOC release notes or prior `.pkg` builds, build metadata embedded directly in binaries traces how TPV and MediaTek assembled this `2016` release incrementally atop multi-year SDK layers:

| Era / Build Stratum | Direct Forensic Artifact | Architectural Observation |
|---|---|---|
| **2005 – 2010 (Upstream Open-Source Base)** | `zlib 1.2.3` (`GCC for MediaTek 4.4.2-20100324`), `expat 2.0.1`, `glibc 2.12.2`, `BusyBox 1.15.3` (`2012-06-06`), `OpenSSL 1.0.0d` (`Feb 2011`), `curl 7.21.7` | Core C toolchain and TLS/parser libraries frozen in `2010–2012` |
| **~2009 Legacy Script Residual** | `appfs1/etc/scripts/rm_usb_mod.sh` checking `/lib/modules/2.6.27` | Reveals shell scripts copied forward from earlier Linux `2.6.27` MediaTek DTV SDKs |
| **2013 – 2014 (TPV `MTK2K14PLF` / Philips Lineage)** | `dtv_driver.ko` paths (`Philips_2K13_ODM_pdwnc_ext.c`, `TPVision_2k13_d_custom.c`); `SYS_BRAND=Philips`; `SYS_ODM=TPV`; `QT 4.8.3` / `Netflix NRD`; `Opera Presto 6213` | Philips 2K13/2K14 chassis codebase adapted as `TPV_MTK2K14PLF` (`LT0` Latin America SBTVD `Ginga` CERTI build) |
| **August 2016 (Target Release Compilation)** | `LE32S5760_V2.011_V0.2.zip` (`upgrade_loader.pkg` `2016-08-03 14:26:04`); `vmlinux` `#1 SMP PREEMPT Thu Aug 4 00:06:04 CST 2016` (`roylo@TWCLS066`) | Kernel & packaging rebuilt for `LE32S5760/20` while keeping frozen `2010–2014` userland middleware and `opcacrt6.pem` roots (`9` certs already expired by Aug 2016!) |

---

## 2. Structural Evolution Insights vs. Later Platform Generations

- This codebase clearly bridges **first/early Linux Smart TVs** (pre-WebEngine Presto + Flash Lite + QML 1.1) and early cryptographically verified boots (`dm-verity` `dm-bht` backported from ChromeOS into Linux `3.0.13` alongside BootROM OTP fuses).
- Retaining hardcoded pre-release QA URLs (`mvc102qa.netflix.com`, `sp-test1-origin.portal.nettvservices.com`, `drmtests.farncombe.eu`) alongside `Philips` brand environment exports demonstrates ODM firmware rebasing prioritized rapid SKU turnaround over deep platform modernization.
