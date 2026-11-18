# Discussion: Architectural Trade-Offs, Empirical Surprise & Preservation Engineering

## 1. The Asymmetric Security Investment Model of Early Smart TVs

Combining Preloader/Kernel cryptographic verification ([evidence/02](../evidence/02_secure_boot_chain_disasm.txt), [evidence/07](../evidence/07_dmbht_and_boot_scripts_audit.txt)) with binary hardening telemetry ([SECURITY_ASSESSMENT.md](../security/SECURITY_ASSESSMENT.md)) exposes an unmistakable engineering priority in 2012–2016 consumer television platforms:
- **Maximum Investment in Boot & DRM Perimeter Integrity:** Hardware eFuses (`0xf0008664`), BootROM RSA-2048, dual kernel RSA-2048 trailers, non-trivial full-width `mpuint_equal` against `e=3` RSA-1024 (`dm-bht` Merkle verification across `36,281` pages), stripped `kallsyms`/`IKCONFIG`, and disabled `ttyMT0` login prompts all successfully lock out casual or automated persistent custom firmware modification.
- **Minimal Investment in Post-Boot Memory Defense, Key Hygiene, and Lifecycle Patching:** Remarkably, **none (`0/16`) of the audited OEM or application binaries compiled with GCC `4.5.1` enable RELRO, Stack Canaries (`-fstack-protector`), PIE, or `_FORTIFY_SOURCE`**, despite `libc-2.12.2.so` inside the exact same image proving full toolchain support (`PARTIAL RELRO`, `Canary=True`, `75` fortified `__*_chk` symbols). Every internet/LAN parser runs unsandboxed as UID `0` without `/etc/shadow`, links against `OpenSSL 1.0.0d` / `libxml2 2.7.8` / `zlib 1.2.3`, trusts `18` `<2048`-bit RSA / `8` `MD2`/`MD5` / `106` `SHA-1` CA roots in `opcacrt6.pem`, and inadvertently ships `LT0_UPG_PriKey_Prod.pem` inside the distributable `roda` image (`SEC-02`).

---

## 2. Correcting Historical Sizing Heuristics via `uenv` DWARF Evidence

In early analysis prior to dumping `upgrade_loader.pkg#part:uenv` `.data`, total board DRAM was informally estimated at `512 MB` based on Qt/Opera footprint ceilings. Dissecting the unstripped DWARF v2 `env.c` object in `uenv` (`2,384` B) revealed `global_kernel_dram_size = 0x21fb9000` (`570,134,528` B = **`543.72 MiB`** allocated specifically to the Linux kernel window excluding A/V DMA & TrustZone carveouts!). Recording both the prior estimate and its binary refutation models rigorous self-correction: total physical soldered DRAM (`Channel A + B`) must exceed `543.7 MiB` (e.g., `768 MiB` or `1 GiB` physical DDR3 minus reserved carveouts), while exact IC density awaits chassis teardown photography.

---

## 3. Why Neither Native Chromium Porting Nor Raw Custom Flashing Is Viable

1. **Irrecoverable Boot Brick Without External NAND Hardware Programmers:** Modifying `load`, `kerA`/`kerB`, `rfsA`/`rfsB`, or `3rdA`/`3rdB` without private vendor keys triggers either `0xfb000520: b #0xfb000520` infinite halt or kernel `NFSB` mount rejection before USB/network interfaces initialize. Without TSOP-48/BGA chip desoldering and an external NAND flash programmer, halting unsigned core-partition flashing prevents irreversible hardware loss.
2. **ABI & Silicon Ceilings:** Even if unlocked, running modern Chromium or streaming clients collides simultaneously with `GCC 4.5.1` (`ARM Cortex-A9 VFP`, `glibc 2.12.2`), `OpenSSL 1.0.0d` (pre-TLS 1.2), proprietary `dtv_driver.ko` kernel coupling (`3.0.13`), and fixed `51 MB`/`97 MB` SquashFS partitions.

---

## 4. Safe Preservation Practice (`mtd12` `/3rd_rw` Overlay Architecture)

Redirecting user customization strictly onto unverified UBIFS `mtd12` (`/3rd_rw`) via `<TAG>smth</TAG><METHOD>FILE</METHOD>` demonstrates how aging Smart TVs can be studied, hardened (e.g., `custom_payload/nettv/urlfilter.ini`, valid ES5 `user.js`, QML launcher prototypes via `SMConfig dynqml`), and safely operated without risking permanent hardware bricking.
