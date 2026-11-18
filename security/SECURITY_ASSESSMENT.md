# System Security Assessment (`AOC LE32S5760/20` — `MT5880` Platform)

> **Controls Matrix:** [SECURITY_CONTROLS_INVENTORY.csv](SECURITY_CONTROLS_INVENTORY.csv) | **Formal Findings:** [SECURITY_FINDINGS.md](SECURITY_FINDINGS.md) (`SEC-01`–`SEC-10`) | **Threat Diagram:** [diagrams/SECURITY_THREAT_MODEL.svg](../diagrams/SECURITY_THREAT_MODEL.svg)

## 1. Executive Security Assessment

Static reverse engineering across Preloader SRAM, the Linux `3.0.13` kernel, OEM installers, binary exploit mitigations, and X.509 trust bundles reveals a **stark contrast between pre-boot DRM integrity and post-boot userspace hygiene**:

1. **Strong Cryptographic Protection of Boot & Read-Only SquashFS Code:** OTP hardware eFuses (`0xf0008664`), BootROM RSA-2048 (`0xfb0034f0`), dual kernel RSA-2048 trailers (`0x25152c`/`0x283f2c`), and kernel `NFSB` RSA-1024 (`e=3`) with full-width `mpuint_equal` + `36,281`-block `dm-bht` MD5 trees prevent unsigned kernel or OS persistence.
2. **Total Absence of Modern Binary & OS Exploit Mitigations in Userspace:** Measuring `17` ELF binaries via `readelf` proves **`0/16` OEM/application binaries** enable RELRO, Stack Canaries (`__stack_chk_fail`), `_FORTIFY_SOURCE`, or PIE — even though `libc-2.12.2.so` proves compiler toolchain support (`PARTIAL RELRO`, `Canary=True`, `75` `_chk` helpers). All core daemons execute as **UID `0` `root` without `/etc/shadow` or LSM confinement (`SEC-01`)**.
3. **Broken Key Custody & Decayed PKI Store:** Factory `upgrade_loader.pkg#part:roda` bundles private signing keys (`TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`) inside the public download archive (`SEC-02`), while `opcacrt6.pem` (`186` certs) embeds `1` `MD2`+`1000`-bit RSA root, `7` `MD5` roots, `106` `SHA-1` roots (`62.7%` of parsed roots), `18` `<2048`-bit RSA keys, `17` OpenSSL-3-unparseable entries, `9` roots already expired in `2016`, and `57` expired prior to `2026`.

---

## 2. Empirical ELF Binary Hardening Audit (`LC_ALL=C readelf -h -l -d --dyn-syms`)

| Binary / Shared Object | Type (`PIE?`) | NX (`GNU_STACK`) | RELRO | Stack Canary | `_FORTIFY_SOURCE` | Builder `DT_RPATH` Leakage |
|---|---|---|---|---|---|---|
| `appfs1/basic/dtv_svc` (`41` libs) | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/bin/busybox` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/bin/dmsetup` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/bin/fw_printenv` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/basic/libmtkapp.so` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/basic/libdtv_common.so` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/basic/lib/libssl.so.1.0.0` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `appfs1/basic/lib/libcurl.so.4.2.0` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | MediaTek `BDP_V301` (`c-ares-1.7.4`) |
| `rootfs1/qt/.../SystemManager` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `451_vfp_ca9/qt-4.8.3-dfb1.4.1` |
| `rootfs1/nettv/opera/browser.out` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `rootfs1/nettv/libnettv.so` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `rootfs1/nettv/libopera_hbbtv.so` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `rootfs1/netflix/nrd-app/netflix` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `p4/w/20150420_194932/.../gnuarm-4.5.1_vfp_ca9` (`18` dirs) |
| `rootfs1/dialserver/dialserver` | `EXEC` (`No PIE`) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| `rootfs1/ginga/lib/libcurl.so.4.2.0` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `/home/local/CERTI/vtz/.../arm_mtk451` |
| `rootfs1/lib/libxml2.so.2.7.8` | `DYN` (ShLib) | `RW` (Enabled) | **NONE** | **False** | **0** | `[]` |
| *Reference Toolchain Baseline:* `appfs1/lib/libc-2.12.2.so` | `DYN` (C Lib) | `RW` (Enabled) | **`PARTIAL`** | **`True`** | **`75` `_chk` symbols** | `[]` |

---

## 3. Systematic Evaluation Across the 10 Mandatory Security Domains

| # | Security Domain | Empirical Posture | Summary Basis |
|---|---|---|---|
| **1** | **Authentication** | **Weak (Userspace)** | Single `root:x:0:0` entry; no `/etc/shadow`; unauthenticated LAN `DIAL`/`DLNA`. |
| **2** | **Permissions & Mitigations** | **Critical Gap (`SEC-01`, `SEC-10`)** | All daemons run as UID `0`; `0/16` OEM binaries enable RELRO, Canaries, PIE, or `FORTIFY`. |
| **3** | **Sensitive Key Custody** | **High Risk (`SEC-02`)** | Factory `roda` archive distributes `LT0_UPG_PriKey_Prod.pem` + `COM_UPG_PriKey_Devt.pem` + AES keys. |
| **4** | **Cryptography & TLS** | **Asymmetric (`High Boot` / `Broken TLS`)** | `nfsb_rsa_check` immune to Bleichenbacher `e=3`; network uses EoL `OpenSSL 1.0.0d` + `18` weak `<2048b` RSA & `8` MD2/MD5 CAs. |
| **5** | **Component Integrity** | **Strong Core / Unchecked `/3rd_rw`** | `36,281` `4KB` SquashFS blocks verified by `dm-bht`; `/perm` & `/3rd_rw` (`mtd11`/`12`) lack integrity verification. |
| **6** | **Network Services** | **Medium-High Risk (LAN)** | Exposes `dialserver`, `libqtdlna.so`, `mDNSResponder`, `libwfd.so` without shipped `iptables` drops. |
| **7** | **Debug / Serial Interfaces** | **Hardened in Prod** | `inittab` comments out `ttyMT0`; `usb_console.sh` only starts passwordless `/bin/sh` if kernel `cmdline` contains `ttyUSB`. |
| **8** | **Update Pipeline** | **Buggy + Asymmetric (`SEC-07`, `SEC-08`)** | `METHOD=PART` formats invalid `"/dev/nand_%d"` (`-22 ENOENT`); `3rdp` skips A/B swap (`0x40ae80`); hardcoded outer AES (`0x94102909*4`). |
| **9** | **Persistence Controls** | **Deterministic (`mtd12`)** | `dtv_svc @ 0x036190` preserves `/3rd_rw/nettv` on `customer_version` flag; `SMConfig dynqml` gate @ `0x1db58c`. |
| **10** | **Unauthorized Flash Prevention** | **Strong Boot / Conditional RW** | Core flash partitions (`mtd0..10`) are unmodifiable without private OTP/kernel/NFSB keys; `mtd12` accepts signed `smth` overlays. |
