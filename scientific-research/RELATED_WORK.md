# Related Work in Embedded & Smart TV Firmware Security

This study situates the `AOC LE32S5760/20` (`MediaTek MT5880` / `TPV MTK2K14PLF`) investigation within foundational embedded systems, Smart TV security, firmware re-hosting, and supply-chain vulnerability research:

## 1. Large-Scale Static Firmware Analysis
- **Costin, Zaddach, Francillon, and Balzarotti (USENIX Security 2014)** — *"A Large-Scale Analysis of the Security of Embedded Firmwares"* — analyzed `32,000` unpacked embedded firmware images (`1.7 million` files), establishing empirically that shared OEM SDKs, legacy OpenSSL/library versions, default accounts, and bundled key artifacts propagate systemically across ostensibly unrelated device brands. Our observation of `SYS_BRAND=Philips` / `SYS_ODM=TPV` / `Philips_2K13` driver trees and leaked `LT0_UPG_PriKey_Prod.pem` inside `LE32S5760` provides a longitudinal Smart TV case study corroborating their SDK code-reuse model.

## 2. Firmware Re-Hosting & Hardware Coupling Barriers
- **Chen, Woo, Brumley, and Egele (`Firmadyne`, NDSS 2016)** — *"Towards Automated Dynamic Analysis for Linux-based Embedded Firmware"* — pioneered automated kernel substitution and NVRAM stubbing for commodity MIPS/ARM Linux routers, yet documented steep drops in emulation success when binaries rely on proprietary peripheral IOCTLs or custom non-mainline SoC drivers.
- **Wright, Moeglein, Bagchi, Kulkarni, and Clements (*ACM Computing Surveys*, 2021)** — *"Challenges in Firmware Re-Hosting, Emulation, and Analysis"* — systematized the semantic gap between raw firmware images and general-purpose emulators (`QEMU`), identifying undocumented MMIO (`0xf0008664`, `0xf00080b0`), auxiliary co-processors (`T8032`), and monolithic closed-source kernel blobs (`dtv_driver.ko`) as core failure modes reproduced firsthand on `MT5880`.

## 3. Verified Boot, `dm-verity`, and Low-Exponent RSA Cryptography
- **Bleichenbacher (CRYPTO 2006 Rump Session) & Finney (2006)** established how lax PKCS#1 v1.5 ASN.1 verification with RSA exponent $e = 3$ allows pencil-and-paper signature forgery when trailing padding bytes go unchecked. We apply that analytical lens directly to MediaTek's kernel `nfsb_rsa_check` (`0xc0028df8`), demonstrating mathematically via ARM32 disassembly that full-width `1024`-bit `mpuint_equal` against `0^96 || SHA256` closes the classical trailing-garbage bypass.

## 4. Firmware Resilience, Testing Methodologies & Supply-Chain Governance
- **Regenscheid (NIST SP 800-193, May 2018)** defines platform firmware resiliency along three pillars: *Protect* (authenticated updates), *Detect* (cryptographic boot/runtime measurement), and *Recover* (rollback to intact flash bank). Our dissection of Preloader + `kerA`/`kerB` + `NFSB` shows strong *Detection* combined with a fragile single-point bootloader *Recovery* flaw (`load` lacks A/B redundancy) and a *Protection* failure in `3rdp` updates (`0x40ae80`) plus `roda` private key exposure (`SEC-02`).
- **Guzman (OWASP Firmware Security Testing Methodology — FSTM)** and **NIST SP 800-161 Rev. 1 (May 2022, Errata Nov 2024)** anchor our nine-stage extraction/disassembly workflow and `SPDX-2.3` / `CycloneDX 1.5` SBOM provenance audit.
