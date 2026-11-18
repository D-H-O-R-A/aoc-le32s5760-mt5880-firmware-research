# Research Scope and Epistemic Boundaries

## 1. Subject System Under Test (SUT)

| Attribute | Value | Verification Status | Source Artifact |
|---|---|---|---|
| **Commercial Model** | `AOC LE32S5760/20` | Confirmed | Official firmware package metadata & Opera/UI identifiers |
| **OEM / ODM Platform** | `TPV MTK2K14PLF` (`SYS_BRAND=Philips`, `SYS_ODM=TPV`) | Confirmed | `extracted/appfs1/etc/profile`, `extracted/ro_data_keys/*` |
| **System-on-Chip (SoC)** | **MediaTek MT5880** (**`ARM Cortex-A9 SMP + VFPv3`** `451_vfp_ca9`, Thumb-2, `Tag_DIV_use: Not allowed`, `T8032` standby MCU) | Confirmed | `SystemManager` / `netflix` `DT_RPATH`, `uenv` `.ARM.attributes` / `.debug_info`, `vmlinux.bin`, `uboot.bin` |
| **Kernel DRAM Allocation** | **`0x21fb9000` (`570,134,528` B = `543.72 MiB`)** -> soldered DDR3 `> 543.7 MiB` *(superseding earlier `~512 MB` approximation)* | Confirmed | `upgrade_loader.pkg#part:uenv` `.data` symbol `global_kernel_dram_size` (`env.c`) + Ch A/B DQS calibration |
| **Official Firmware Archive** | `LE32S5760_V2.011_V0.2.zip` (`285,061,005` bytes) -> `upgrade_loader.pkg` (`323,840,461` bytes, `2016-08-03`) | Confirmed | Local archive SHA-256 & zip central directory |
| **Linux Kernel Release** | `Linux version 3.0.13` (`roylo@TWCLS066`, `gcc version 4.5.1`, `#1 SMP PREEMPT Thu Aug 4 00:06:04 CST 2016`) | Confirmed | `scratch/vmlinux.bin` banner string (`stripped uImage 0x40` header) |
| **Internal Version Tags** | `SYS_VERSION=IDTV0801_002223_9_001_23_001_224`, `TPV_VERSION=000.001.205.145` | Confirmed | `extracted/appfs1/etc/profile` |
| **Mainboard PCB Marking** | Hypothesized `715G7904M` family (unconfirmed on physical unit) | **UNKNOWN / UNVERIFIED** | `0` matches across extracted firmware & binaries; requires visual board inspection |

## 2. In-Scope Research Questions

1. **Hardware & SoC Architecture:** Which CPU cores (`ARM Cortex-A9 SMP + VFPv3`), co-processors (`T8032`, `adsp`, `aqda`), `/3rd/Img_Sgx` absence, `uenv` DRAM carveout (`0x21fb9000`), NAND flash IDs, and EEPROM/peripheral buses (`/dev/eeprom_{0,3,4}`) are evidenced strictly inside bootloader, kernel, and ELF binaries?
2. **Firmware Forensics & Boot Chain:** How does `LE32S5760_V2.011_V0.2.zip` unpack into MTK partition tags (`3rdB`, `3rdA`, `roda`, `cfig`, `load`, `uenv`, `adsp`, `aqda`, `pqda`, `rfsB`, `rfsA`, `kerB`, `kerA`, `usig`, `chtD`, `chtC`), and how is cryptographic integrity enforced (`eFuse 0xf0008664`, dual RSA-2048 kernel trailers, packed `231`-byte `struct nfsb_header_v2` `e=3` + `36,281`-block `dm-bht`)?
3. **Update Failure Post-Mortem:** Why did local USB upgrade experiments stall at `...` for `~8` seconds before showing `"REINICIAR OU TENTAR NOVAMENTE"` (`libmtkapp.so` `"/dev/nand_10"` `-22 ENOENT` + disabled `3rdp` failover)?
4. **Application Compatibility Limits:** Why can modern YouTube (`yt_lbl.swf`), Netflix (`OpenSSL 1.0.0d` / NRD 2015), and modern TLS `1.2`/`1.3` web apps not run natively on Presto `6213` / Qt `4.8.3`?
5. **Security, Compiler Hardening, Privacy & SBOM (`SEC-01`–`SEC-10`):** What attack surface, UID `0` execution model, `0/16` ELF mitigation compliance (`RELRO`/`Canary`/`PIE`/`FORTIFY`), `roda` private-key leak, `opcacrt6.pem` cryptographic decay (`MD2`/`MD5`/`SHA-1`/`<2048b`), external endpoints, and legacy CVEs exist in the stock filesystem?

## 3. Explicitly Out-of-Scope & Unobserved Domains

- **Physical Teardown / Silicon Decapping:** No physical chassis disassembly, high-resolution PCB photographs, JTAG/UART oscilloscope captures, or eFuse dump via hardware glitching were performed on this unit.
- **Full-System Dynamic Re-Hosting / Live Packet Capture:** Neither `qemu-arm` runtime execution of full SoC peripherals (due to proprietary `dtv_driver.ko` MMIO dependencies and missing `0xf000xxxx`/`T8032` hardware emulation) nor controlled MITM packet capture on physical TV hardware was executed. All dynamic/network behaviors reported here strictly separate **static binary configuration analysis** from **unobserved runtime telemetry**.
- **Multi-Version Binary Diffing:** Only a single stock firmware release (`V2.011_V0.2` / `upgrade_loader.pkg`) was available in the workspace; longitudinal version-to-version binary patching (`comparative-analysis/`) is therefore scoped to comparing internal mirrored banks (`kerA` vs `kerB`, `rfsA` vs `rfsB`, `3rdA` vs `3rdB`) and stock vs. laboratory custom payloads (`upgrade_loader.pkg` vs `custom_upgrade_loader.pkg`, `rootfs1` vs `staging_rootfs`).
