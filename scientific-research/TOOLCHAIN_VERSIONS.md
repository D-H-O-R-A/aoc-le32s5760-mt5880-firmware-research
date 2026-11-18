# Toolchain Versions Comparison (`Target Firmware Build` vs. `Analysis Workstation`)

## 1. Target Firmware Build Toolchains (`2010 – 2016` Embedded ARMv7-A)

| Component | Target Toolchain / Version Observed | Evidence Artifact |
|---|---|---|
| **Kernel & Primary `glibc` Compiler** | `gcc version 4.5.1 (GCC)` (`roylo@TWCLS066`, `Thu Aug 4 2016`) | `scratch/vmlinux.bin`, `extracted/appfs1/lib/libc-2.12.2.so`, `extracted/uenv` |
| **Legacy Prebuilt `zlib 1.2.3` Compiler** | `GCC for MediaTek 4.4.2-20100324` (`4.4.2`) | `.comment` strings in `extracted/appfs1/lib/libz.so.1.2.3` |
| **Target C Runtime / Linker** | GNU C Library (`glibc`) `2.12.2` (`ld-2.12.2.so`, `libstdc++.so.6.0.14`) | `extracted/appfs1/lib/` |
| **CERTI `Ginga` Middleware Cross-Prefix** | `arm_mtk451` (`/home/local/CERTI/vtz/Projects/envision_middleware_clean/...`) | Embedded string in `rootfs1/ginga/lib/libcurl.so.4.2.0` |

## 2. Analysis Host Toolchain (`2026` Workstation)

| Tool | Exact Version Observed | Purpose in Research Pipeline |
|---|---|---|
| `Python` | `3.12.3` | PKG/NFSB/UPG/Merkle parsers, SBOM generator, test runner |
| `Capstone` | `5.0.7` | ARM32 (`CS_ARCH_ARM`, `CS_MODE_ARM`) & Thumb-2 (`CS_MODE_THUMB`) disassembly |
| `OpenSSL CLI` | `3.0.13` | X.509 CA expiration audit (`opcacrt6.pem`), AES-128-CBC & RSA-2048 checks |
| `Node.js` | `v18.19.1` | Static syntax verification of custom ES5 `user.js` (`inspect_runtime_engines.py`) |
| `GNU Binutils` (`readelf`) | `2.42` | ARM EABI ELF section & dynamic symbol cross-checks |
| `Git` | `2.43.0` | Reproducible commit history & tag (`v1.0.0`, `v2.0.0`) management |
