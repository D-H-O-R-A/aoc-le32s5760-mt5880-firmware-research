# Cryptographic Chain-of-Trust, Upgrade Pipeline Defects, and Defense-in-Depth Asymmetries in First-Generation Linux Smart Televisions: A Deep Static Monograph of the AOC `LE32S5760/20` (`MediaTek MT5880`)

**Author:** D-H-O-R-A Firmware Research (`aoc-le32s5760-mt5880-firmware-research`)  
**Target Platform:** AOC `LE32S5760/20` (`TPV_MTK2K14PLF` / MediaTek `MT5880` **ARM Cortex-A9 SMP** / Linux `3.0.13`)  
**Analyzed Distribution:** `LE32S5760_V2.011_V0.2.zip` (`285,061,005` B, `SHA-256: 014e235c...`) -> `upgrade_loader.pkg` (`323,840,461` B)  
**Companion Academic Sections:** [Abstract](ABSTRACT.md) · [Methodology](METHODOLOGY.md) · [Results](RESULTS.md) · [Discussion](DISCUSSION.md) · [Limitations](LIMITATIONS.md) · [Conclusion](CONCLUSION.md) · [References (`BibTeX`)](REFERENCES.bib)

---

## Abstract

Consumer Smart Televisions released between 2012 and 2016 expose an acute structural conflict between tamper-resistant DRM/boot chains and unmaintained application stacks. Motivated by an empirical upgrade failure observed on a retail **AOC `LE32S5760/20`** (`TPV MTK2K14PLF` / **MediaTek `MT5880`**)—where local USB flashing stalled at progress dialog `"..."` for `~8` seconds before aborting with `"REINICIAR OU TENTAR NOVAMENTE"`—we present an end-to-end forensic reconstruction spanning mask-ROM silicon interfaces, unstripped DWARF bootloader metadata, Linux `3.0.13` `dm-verity` (`NFSB` v2) block verification, userland upgrade parsers, binary exploit mitigation telemetry (`readelf`), X.509 trust store analysis (`186` CA certificates), and standards-compliant `SPDX-2.3` / `CycloneDX 1.5` SBOMs.

Across seven primary deterministic proof harnesses (`evidence/01..07`) and automated CI tests (`tests/test_research_suite.py`), we establish five core contributions:
1. **Silicon-to-Kernel Chain Reconstruction & Bleichenbacher `e=3` Immunity Proof:** Correcting a `64`-byte U-Boot `uImage` misalignment on decompressed `vmlinux.bin` (`0xc0008000`) resolves `e = 3` (`0xc04292f0`), `1024`-bit modulus `N` (`0xc0429370`), `dm_mount_root_nfsb` (`0xc0009594`), `populate_table_nfsb` (`0xc02243c4`), and `nfsb_rsa_check` (`0xc0028df8`). We prove mathematically across all `4` factory images (`3rdB`, `3rdA`, `rfsB`, `rfsA`) and all **`36,281` `4 KB` SquashFS blocks** (`12,514` + `23,767`) that `mpuint_equal` enforces full-width `1024`-bit equality $S^3 \bmod N == 0^{96} \parallel \text{SHA-256}(\text{hdr}[0:0\text{x}67])$, blocking low-exponent trailing-garbage forgeries (`custom_upgrade_loader.pkg` counter-proof: `False`). Meanwhile, Thumb-2 Preloader disassembly proves OTP eFuse `0xf0008664 & 0x100000` drives an infinite brick loop at `0xfb000520: b #0xfb000520` upon signature failure.
2. **Instruction-Level Diagnosis of the `8`-Second Abort & `#DH@FiRm` Key Quirk:** ARM32 disassembly of `libmtkapp.so` (`sub_404f28 @ 0x404f54`) proves `<METHOD>PART</METHOD>` formats invalid string `"/dev/nand_10"` (`-22 ENOENT`) while `_phm_upg_model_start_upgrade` (`0x40ae80`) skips A/B bank swapping on `3rdp` images. Disassembly of `libdtv_common.so` (`0x098b64`) recovers hardcoded AES `0x94102909 * 4`, zero-slot MD5, and `MD5()` derivation over **`33`-byte `\n`-terminated** `AES_Prod.key/.iv` files.
3. **DWARF `uenv` & `DT_RPATH` Micro-Architecture Refinements:** Inspecting `upgrade_loader.pkg#part:uenv` (`ET_REL` with intact `.debug_info`/`.ARM.attributes`) pins down GCC `4.5.1`, ARMv7-A without `SDIV`/`UDIV`, and **`global_kernel_dram_size = 0x21fb9000` (`543.72 MiB`)**—refuting prior `~512 MB` estimates—while `SystemManager` and `netflix` `DT_RPATH` strings verify **`451_vfp_ca9` (ARM Cortex-A9 w/ VFP)** alongside cross-product Blu-ray SDK (`BDP_V301`) `libcurl` reuse.
4. **Security & Trust-Store Empirical Telemetry (`SEC-01`–`SEC-10`):** Despite `libc-2.12.2.so` supporting mitigations, **`16/16` (`100%`) of audited application/OEM ELFs ship with `RELRO=NONE`, `Stack Canary=False`, `_FORTIFY_SOURCE=0`, and non-PIE fixed `EXEC` base addresses**, executing as UID `0` `root` without `/etc/shadow`. Simultaneously, `upgrade_loader.pkg#part:roda` leaks `LT0_UPG_PriKey_Prod.pem` (`SEC-02`), and Opera's `opcacrt6.pem` (`186` certs) contains `1` `MD2` (`1000b`), `7` `MD5`, `106` `SHA-1`, `18` RSA`<2048b`, `17` OpenSSL 3 parse failures, `9` roots expired in `2016`, and `57` expired prior to `2026`.
5. **Lock-Compliant Preservation Engineering & Strict Epistemic Honesty:** Confined persistence onto non-verity UBIFS `mtd12` (`/3rd_rw`) via `<TAG>smth</TAG><METHOD>FILE</METHOD>` avoids irreversible flash bricks without an external NAND programmer, while unverified physical PCB markings (`715G7904M`), unexecuted QEMU runs, and uncaptured live `pcap` traces are cleanly documented as explicit open boundaries.

---

## I. Introduction & Problem Formulation

Early embedded Smart Televisions occupied an architectural inflection point: semiconductor vendors (MediaTek) and ODMs (TPV Technology) transplanted desktop/mobile web engines (`Opera Presto`, `Qt 4.8.3`, `Adobe AIR` Flash Lite) and multi-DRM middleware (`PlayReady`, `Widevine`, `Marlin`) onto fixed-footprint Linux `3.0.13` BSPs secured by cryptographic root-of-trust mechanisms originally designed to satisfy conditional-access and streaming certification contracts. Over a `5–10`-year consumer lifespan, however, cryptographic deprecation (TLS `1.0` retirement, CA root expiration, SHA-1 distrust) collides irreversibly with immutable signed SquashFS partitions.

When owners attempt local firmware modifications—ranging from replacing `/3rd` browser configurations to rebuilding Squid/SquashFS application partitions—two fatal outcomes emerge: opaque upgrade rejections (the `8`-second `"REINICIAR OU TENTAR NOVAMENTE"` loop studied here) or unrecoverable bricking when writing unsigned bootloader or kernel blocks in the absence of a hardware NAND chip programmer. This work resolves every stage of that stack cleanly into mathematically reproducible, verifiable engineering proofs.

---

## II. Literature Context & Methodology

Our analytical pipeline operationalizes **OWASP Firmware Security Testing Methodology (`FSTM`)** stages 1–5 (`[guzman_owasp_fstm]`), maps firmware resilience against **NIST SP 800-193** *Protect/Detect/Recover* criteria (`[regenscheid2018nist800193]`), and builds machine-readable software inventories compliant with **NIST SP 800-161 Rev. 1** (`[nist2022sp800161r1]`). Methodologically:
- Our empirical supply-chain findings (`SYS_BRAND=Philips`, `Philips_2K13_ODM_pdwnc_ext.c`, `BDP_V301` Blu-ray `libcurl`, `CERTI` Ginga `arm_mtk451`, leaked `LT0` signing keys) provide a detailed single-platform confirmation of the multi-vendor SDK vulnerability propagation model demonstrated at scale by Costin et al. (`[costin2014large]`).
- Our hardware coupling inventory (`0xf0008664` eFuse, `0xf00080b0` HW-LZHS, `T8032` standby lockstep, `dtv_driver.ko`) concretizes the MMIO and co-processor re-hosting barriers systematized by Chen et al. (`Firmadyne`, `[chen2016firmadyne]`) and Wright et al. (`[wright2021challenges]`).
- Our `nfsb_rsa_check` analysis directly tests the low-exponent RSA padding class analyzed by Bleichenbacher and Finney (`[finney2006bleichenbacher]`).

Extraction procedures ([FIRMWARE_EXTRACTION_METHODOLOGY.md](../firmware-forensics/FIRMWARE_EXTRACTION_METHODOLOGY.md)) demultiplex all `16` tagged partitions from `LE32S5760_V2.011_V0.2.zip` -> `upgrade_loader.pkg`, track `105` SHA-256 digests (`FIRMWARE_HASH_MANIFEST.txt`) and `4,004` extracted filesystem nodes (`FILESYSTEM_INVENTORY.csv`, avoiding blocking on the `dev/initctl` FIFO via `stat.S_ISREG` checks), strip the `0x40`-byte `uImage` prefix from `vmlinux.bin`, verify `36,281` `dm-bht` blocks in Python, and disassemble ARM32/Thumb-2 code paths using **Capstone 5.0.7**.

---

## III. Silicon Micro-Architecture & Memory Subsystems (`MT5880`)

Cross-referencing bootloader literals, `.ARM.attributes`, DWARF `.debug_info`, and userland `DT_RPATH` traces establishes the hardware boundary ([hardware/SOC_ANALYSIS.md](../hardware/SOC_ANALYSIS.md), [MEMORY_ARCHITECTURE.md](../hardware/MEMORY_ARCHITECTURE.md)):

1. **Application Processor (`ARM Cortex-A9 SMP + VFPv3`):** Both `SystemManager` (`451_vfp_ca9/qt-4.8.3-dfb1.4.1`) and `netflix` (`gnuarm-4.5.1_vfp_ca9`) specify Cortex-A9 VFP toolchains; `uenv` `.ARM.attributes` specifies `ARMv7-A`, `Thumb-2`, `-Os` size optimization, and `Tag_DIV_use: Not allowed` (absence of ARM hardware `SDIV`/`UDIV`, matching Cortex-A9). `vmlinux.bin` links `cache-l2x0.c`, `gic.c`, `pmu.c`, and `vfpmodule.c`, built with `CONFIG_SMP=y`, `CONFIG_PREEMPT=y`, and `CONFIG_HIGHMEM=y`.
2. **Embedded Co-Processors & I/O Silicon:** Preloader verifies a live 8051 standby controller handshake (`"Preloader T8032 ack !"` / `"T8032 NO ack!"`, `pdwnc6896/pdwnc_hw.c`); PKG ships `adsp` (`1,272,368` B) & `aqda` (`131,216` B) Audio DSP payloads; `/3rd/Img_Sgx` is **empty** (`pvrsrvctl` omitted; `mt53_fb.c` + DirectFB `1.4.1` drive scanout); `star_mac.ko` and `rt5572sta.ko` (`148F:5572`, `043E:7A13/32`, `2001:3C1A`) service LAN and USB WLAN.
3. **`uenv` `.data` Memory Refutation & Dual-Channel DDR3:** DWARF inspection of `upgrade_loader.pkg#part:uenv` (`env.c`, `2,384` B) recovers `global_magic = 0x53965368` and **`global_kernel_dram_size = 0x21fb9000` (`543.72 MiB`)** allocated directly to Linux. Combined with `DRAM Channel A/B Calibration` (`0xf00046xx..48xx`) and `mt53xx_get_reserved_area` (DMA/video/TrustZone carveouts), soldered dual-channel DDR3 exceeds `543.7 MiB` (likely `768 MiB` or `1 GiB` physical DDR), refuting earlier `512 MB` approximations.
4. **Raw NAND (`cfig` `mtd0..mtd30`) vs. Auxiliary EEPROM (`/dev/eeprom_{0,3,4}`):** Kernel `mtk_nand.c` registers `10` candidate flash IDs (Hynix/Micron/Samsung/Toshiba) alongside hardware ECC and `NAND_AES_INIT`, while `dtv_driver.ko` registers `nor/eeprom_hw.c` (`/dev/eeprom_{0,3,4}`) for persistent NVM/bank flags. Because no teardown was performed (`HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/`), the hypothesized PCB silkscreen `715G7904M` (`0` firmware occurrences) and exact soldered chip markings remain explicitly **UNVERIFIED**.

---

## IV. Boot Chain, `NFSB` v2 Struct & Bleichenbacher `e = 3` Proof

The `MT5880` chain of trust enforces deterministic verification across three non-bypassable stages (`diagrams/BOOT_CHAIN.svg`):

```text
[Mask BootROM: NANDBOOT/V01.00]
  │ Loads 41 KB Thumb-2 Preloader @ 0xfb000000
  ▼
[Stage 1 — Preloader eFuse & BootROM RSA-2048]
  ├── Reads OTP eFuse MMIO: 0xf0008664 & 0x100000 (bit 20 == 1) + [0xfb0053bc] == 1
  ├── Checks RSA-2048 signature (+0x6c4b0) via BootROM call (bl #0xfb0034f0)
  └── FAIL -> Prints "not secure loader\n" @ 0xfb00052a -> HALT: b #0xfb000520 (Brick!)
  │ PASS -> HW-LZHS decompress (0xf00080b0) U-Boot -> verifies EEPROM bank
  ▼
[Stage 2 — U-Boot -> Kernel kerA/kerB (2,638,124 B, mtd4/mtd5)]
  ├── Checks dual 512B [RSA-2048 Sig + Cert] trailers @ 0x25152c & 0x283f2c
  └── HW-LZHS decompresses uImage -> ARM32 Linux 3.0.13 (VA 0xc0008000)
  ▼
[Stage 3 — Kernel dm_mount_root_nfsb (0xc0009594) -> nfsb_rsa_check (0xc0028df8)]
  ├── Strips/reads 231B (0xe7) struct nfsb_header_v2 on mtd6/7 (rfsA/B) & mtd9/10 (3rdA/B)
  └── Computes out = S^3 mod N (N @ 0xc0429370); mpuint_equal(out, 0^96 || SHA256(hdr[0:0x67]))
```

### `struct nfsb_header_v2` Verified Geometry & Merkle Tree Equivalence
Decoded identically across `rfsA` (`51,466,240` B, `12,514` `4KB` blocks -> Level-0 root `6cc5d821e2e914aec01a1db58fcca389`) and `3rdA` (`97,738,752` B, `23,767` `4KB` blocks -> Level-0 root `666e1b26ae2e81a681c4f510bd98bfca`), all **`36,281` `4 KB` data pages** verify cleanly against the RSA-signed root digest ([FIRMWARE_FORMAT_SPECIFICATION.md](../firmware-forensics/FIRMWARE_FORMAT_SPECIFICATION.md)), while modified `build/custom_upgrade_loader.pkg` fails deterministically (`RSA_exact_match=False`). Critically, because `mpuint_equal` (`0xc0029000`) compares all `1024` bits against $0^{96} \parallel \text{SHA-256}$, Bleichenbacher's `e=3` trailing-garbage cube-root attack cannot forge arbitrary signatures (`SECURITY`: **IMMUNE**).

---

## V. Update Cryptosystem (`Autorun.upg`) & Root-Cause Post-Mortem of the `8`-Second Abort

Inspecting `libdtv_common.so` (`dlm_locate_codefile_hdr`, `x_dlm_download_by_tag`) and `libmtkapp.so` (`_phm_upg_model_start_upgrade`, `sub_404f28`) resolves every anomaly observed on hardware:
1. **`#DH@FiRm` Cryptosystem:** Outer `128` B filename (`[0x00:0x80]`) sits outside the signature; bytes `[0x80:0xF0]` encrypt metadata using hardcoded key `0x94102909 * 4` (`IV=0`); `[0xF0:0x110]` holds the Body MD5 computed with `[0xF0:0x110]` zeroed; `[0x110:end-256]` holds sequential chunks authenticated by AES-128-CBC (`"reserved mtk inc"` + chunk `SHA-256`) using `MD5(33B AES_Prod.key)` and `MD5(33B AES_Prod.iv)` (`\n`-inclusive quirk!); and `[end-256:end]` carries RSA-2048 PKCS#1 v1.5 over `[0x80:end-256]` (`cmp r8, #0x20`).
2. **Exact Cause of the `8`-Second `"REINICIAR OU TENTAR NOVAMENTE"` Failure:** Passing `<METHOD>PART</METHOD>` selects `r6 == 0` in `libmtkapp.so` (`sub_404f28 @ 0x404f54`), formatting device path `"/dev/nand_%d"` (e.g., `"/dev/nand_10"`) instead of `"/dev/mtd10"`. `c_fm_erase_flash_part` returns **`-22 ENOENT`**, aborting the UI progress bar cleanly after ~8 seconds. Furthermore, `0x40ae80..0x40ae9c` explicitly skips EEPROM dual-bank failover for standalone `3rdp` updates.

---

## VI. Security Findings (`SEC-01`–`SEC-10`), Binary Hardening & PKI/SBOM Posture

Extending prior audits (`v1.0.0`), static `readelf` and X.509 measurements expose critical runtime weaknesses juxtaposed against locked boot silicon ([SECURITY_ASSESSMENT.md](../security/SECURITY_ASSESSMENT.md), [SECURITY_FINDINGS.md](../security/SECURITY_FINDINGS.md)):
- **`SEC-10` — `0%` Application Exploit Mitigation Adoption:** Across **`16/16` OEM and third-party binaries** (`dtv_svc`, `busybox`, `SystemManager`, `browser.out`, `netflix`, `dialserver`, `libmtkapp.so`, `libdtv_common.so`, `libnettv.so`, `libssl.so.1.0.0`, `libxml2.so.2.7.8`), **RELRO is `NONE`**, **Stack Canaries are `False`**, **`_FORTIFY_SOURCE` is `0`**, and all standalone executables use **non-PIE fixed addresses**—despite `libc-2.12.2.so` (`PARTIAL RELRO`, `Canary=True`, `75` `_chk` imports) proving full toolchain support.
- **`SEC-01` & `SEC-06` — UID `0` Execution & LAN Surfaces:** `/etc/passwd` defines solely `root:x:0:0` without `/etc/shadow` or LSM MAC (`usb_console.sh` gated only on signed `ttyUSB` cmdline). Unauthenticated LAN daemons (`dialserver`, `libqtdlna.so`, `mDNSResponder`) operate without active `iptables` filtering rules.
- **`SEC-02` — Private Key Leakage in `roda`:** `upgrade_loader.pkg#part:roda` bundles `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem` and `COM_UPG_PriKey_Devt.pem` alongside public PEMs (compromising `LT0` `.upg` exclusivity without breaching BootROM/`ker`/`NFSB`).
- **`SEC-03`, `SEC-04`, `SEC-05` — Obsolete TLS, CA Decay & SBOM Debt:** `OpenSSL 1.0.0d` + `libcurl 7.21.7` limit TLS to `1.0/1.1`; auditing `186` certs in `opcacrt6.pem` finds **`17` OpenSSL-3 parse failures, `1` `MD2` (`1000`-bit), `7` `MD5`, `106` (`62.7%`) `SHA-1`, `18` `<2048`-bit RSA keys, `9` expired `<=2016`, `57` expired `<2026`, `WoSign`, and missing modern roots**; `SPDX-2.3` (`27` pkgs) and `CycloneDX 1.5` (`26` comps) map legacy CVEs across `Linux 3.0.13`, `glibc 2.12.2`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`, and `BusyBox 1.15.3`.

---

## VII. Privacy, Network Reachability & Re-Hosting Constraints

Static string scanning catalogs **`291` unique URL entries** ([EXTERNAL_ENDPOINT_INVENTORY.csv](../privacy/EXTERNAL_ENDPOINT_INVENTORY.csv)) spanning Philips/Corio NetTV portals (`ecdinterface.philips.com`), HTTP speedtest/PDS probes (`speedtest.oui-0x00199d.com/st.jpg`, `pds.philips.com`), Netflix NRD `4.0` (`nrdp.nccp.netflix.com`), and staging test leftovers (`mvc102qa.netflix.com`, `certification.nettvservices.com`). Because zero wire packet captures (`tcpdump`/MITM) were performed, runtime beacon frequency and PII payloads are marked strictly **UNOBSERVED** pending controlled VLAN capture ([PRIVACY_ASSESSMENT.md](../privacy/PRIVACY_ASSESSMENT.md)). Similarly, `qemu-arm` hardware re-hosting remains a documented architectural blueprint rather than a simulated claim ([emulation/](../emulation/EMULATION_RESEARCH.md)).

---

## VIII. Constructive Safe Preservation (`mtd12` `/3rd_rw` Overlay)

Accepting the irreversible cryptographic boundary on `mtd0..mtd10` without hardware flashers, [scripts/build_safe_rw_upg.py](../scripts/build_safe_rw_upg.py) constructs compliant `<TAG>smth</TAG><METHOD>FILE</METHOD>` packages (`19,905` B verified locally; `10,285` B in hermetic CI tests) targeting unverified UBIFS `mtd12` (`/3rd_rw`). Disassembly proves `dtv_svc @ 0x036190` preserves `/3rd_rw/nettv` via `/3rd_rw/upgrade/customer_version`, `libnettv.so @ 0x1889a0` applies `opera_new.ini`/`urlfilter.ini`/ES5 `user.js`, and `SystemManager @ 0x1db58c` honors `SMConfig` `dynqml`—yielding safe, non-destructive preservation (`21` added + `4` modified files audited across `custom_payload/`).

---

## IX. Limitations & Conclusion

Six explicit gaps bound this study ([LIMITATIONS.md](LIMITATIONS.md)): absent physical board teardown photos (`715G7904M` unverified), absent external NAND programmer, uncaptured live UART/QEMU runs, uncaptured `pcap` wire traffic, single factory archive (`V2.011_V0.2`), and absent OEM GPL tarballs. Within those exact empirical boundaries, all primary cryptographic proofs (`7/7`), SHA-256 manifests (`105/105` workspace / `58/58` CI), and automated regression tests (`10/10`) execute reproducibly from open scripts without proprietary artifact redistribution.
