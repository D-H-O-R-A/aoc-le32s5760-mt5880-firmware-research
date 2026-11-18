# Kernel Version, Toolchain & Build Provenance

## 1. Exact Build Metadata

| Attribute | Extracted Fact | Evidence Source |
|---|---|---|
| **Kernel Version** | `3.0.13` (`Linux 3.0.13`) | `scratch/vmlinux.bin` + all `12` `.ko` `vermagic` strings |
| **Compile Number & Preemption** | `#1 SMP PREEMPT` | Kernel banner string |
| **Build Timestamp** | `Thu Aug 4 00:06:04 CST 2016` (Asia/Taipei or China Standard Time `UTC+8`, ~9.5 hours after `upgrade_loader.pkg` archive time or same release window) | `scratch/vmlinux.bin` banner |
| **Build Host & User** | `roylo@TWCLS066` (`TW` = Taiwan engineering cluster) | `scratch/vmlinux.bin` banner |
| **Compiler** | `gcc version 4.5.1 (GCC)` | Banner & `libc-2.12.2.so` (`Compiled by GNU CC version 4.5.1`) |
| **Workspace Source Path** | `/share/Release_code_use/Roy/release/vm_linux/chiling/kernel/linux-3.0/` | `381` embedded `__FILE__` strings |
| **Legacy Prebuilt Artifact Toolchain** | `GCC for MediaTek 4.4.2-20100324` | Observed in `extracted/appfs1/lib/libz.so.1.2.3` |

---

## 2. Historical & Maintenance Gap Assessment

Upstream mainline Linux `3.0` was released in **July 2011**, and the `3.0.13` stable point release dates back to **December 2011**. Yet this firmware was compiled in **August 2016** — nearly five years after `3.0.13` left upstream maintenance (`3.0.x` LTS itself reached EOL in October 2013).

### Root Cause of BSP Freezing in 2014–2016 Smart TVs
1. **Binary Driver Coupling (`dtv_driver.ko`):** MediaTek's monolithic `6.84 MB` DTV/hardware driver targets internal `3.0.13` kernel ABI structures; forward-porting to Linux `3.4`/`3.10`/`4.x` requires porting thousands of hardware abstractions and re-validating DRM/TrustZone timings.
2. **TPV Cross-Brand Reuse:** `Philips_2K13_ODM_pdwnc_ext.c`, `TPVision_2k13_d_custom.c`, and `SYS_VERSION=IDTV0801_...` indicate AOC `LE32S5760/20` (`2016`) inherited an already mature 2013–2014 `MT5880` (`chiling`) BSP branch rather than receiving a new kernel rebase.
