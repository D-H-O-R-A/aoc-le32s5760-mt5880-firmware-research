# System Security Assessment (`AOC LE32S5760/20` — `MT5880` Platform)

> **Controls Matrix:** [SECURITY_CONTROLS_INVENTORY.csv](SECURITY_CONTROLS_INVENTORY.csv) | **Formal Findings:** [SECURITY_FINDINGS.md](SECURITY_FINDINGS.md) | **Threat Diagram:** [diagrams/SECURITY_THREAT_MODEL.svg](../diagrams/SECURITY_THREAT_MODEL.svg)

## 1. Executive Security Assessment

Static reverse engineering across boot, kernel, filesystem, updater, and application layers demonstrates a **strongly asymmetric security architecture** characteristic of 2014–2016 consumer Smart TVs:

1. **Strong Cryptographic Protection of Boot & Read-Only Partitions:**
   The OEM invested heavily in protecting firmware/IP integrity and DRM boot boundaries through hardware OTP eFuses (`0xf0008664`), BootROM RSA-2048 validation (`0xfb0034f0`), dual kernel trailers (`0x25152c`/`0x283f2c`), and kernel-enforced `NFSB` v2 `dm-verity` (`nfsb_rsa_check` checking all `36,281` 4 KB SquashFS pages via `dm-bht` MD5).
2. **Severe Deficiencies in Userspace Isolation, PKI Maintenance, Key Custody & Legacy Dependencies:**
   Conversely, post-boot userspace execution exhibits zero non-root sandboxing (`root:x:0:0` for `dtv_svc`, `SystemManager`, `opera`, and `dialserver`), no `/etc/shadow` password store, `10+`-year End-of-Life (EoL) shared C/C++ libraries (`OpenSSL 1.0.0d`, `libcurl 7.21.7`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`, `glibc 2.12.2`), pre-expired CA trust anchors (`9` already expired in `2016`, `57` expired before `2026`), and factory private `.pem` artifacts bundled inside the distributable `roda` image (`upgrade_loader.pkg#part:roda`).

---

## 2. Systematic Evaluation Across the 10 Mandatory Security Domains

| # | Security Domain | Empirical Posture | Summary Basis & Artifact Links |
|---|---|---|---|
| **1** | **Authentication Mechanisms** | **Weak (Userspace)** | `/etc/passwd` defines solely `root:x:0:0`; no `/etc/shadow`; LAN DIAL (`dialserver`) lacks pairing PIN/TLS in static `dial.conf`. See [AUTHENTICATION_ANALYSIS.md](AUTHENTICATION_ANALYSIS.md). |
| **2** | **Permissions & Privilege Management** | **Weak** | No non-root UID accounts (`setuid` count `0` only because everything starts under UID `0` `init`); no SELinux/AppArmor enforcement; all daemons access `/dev/mtd*`, `/ro_data`, and raw sockets directly. |
| **3** | **Protection of Sensitive Info** | **Critical Gap (Factory `roda`)** | While runtime mounts `/ro_data` read-only (`-r`), the factory `upgrade_loader.pkg` `roda` partition embeds `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`, and AES keys directly inside a publicly distributed update archive (`SEC-02`). |
| **4** | **Cryptography & Key Management** | **Mixed (Strong NFSB vs Weak DLM/TLS)** | Kernel `nfsb_rsa_check` properly closes Bleichenbacher $e=3$ padding attacks via full-width `mpuint_equal` (`HIGH`). However, DLM outer key (`0x94102909 * 4`) is hardcoded, `AES_Prod` key derivation hashes `33`-byte `\n` files via MD5 (`MEDIUM`), and network crypto relies on EoL `OpenSSL 1.0.0d` (`HIGH`). See [CRYPTOGRAPHIC_ANALYSIS.md](CRYPTOGRAPHIC_ANALYSIS.md). |
| **5** | **Component Integrity** | **Strong (Core) / Unchecked (RW)** | Bootloader, Kernel (`kerA/B`), RootFS (`rfsA/B`), and App Partition (`3rdA/B`) are cryptographically locked (`36,281` verified blocks). Writable overlays `/perm` (`mtd11`) and `/3rd_rw` (`mtd12`) have zero integrity verification (`no_chk_data_crc`). |
| **6** | **Network Service Security** | **Medium-High Risk (LAN)** | Exposes SSDP/DIAL (`dialserver`), DLNA (`libqtdlna.so`), mDNS (`libmDNSResponderPosix.so`), and Wi-Fi Direct (`libwfd.so`) without documented TLS or mutual authentication. |
| **7** | **Hardware Communication Interfaces** | **Hardened in Production** | `ttyMT0` getty is commented out in `/etc/inittab`; `usb_console.sh` only spawns `getty -l /bin/sh` if `/proc/cmdline` carries `ttyUSB`, which is blocked by signed kernel images. Physical board pads remain unprobed. |
| **8** | **Firmware Update Mechanism** | **Asymmetric (`BUG` + Signed Container)** | Uses RSA-2048 + dual AES + SHA-256 over `Autorun.upg`, yet suffers from `/dev/nand_%d` `-22 ENOENT` fault on `METHOD=PART`, skips `3rdp` A/B failover (`0x40ae80`), and leaked `LT0_UPG_PriKey_Prod.pem` in `roda` (`SEC-02`). |
| **9** | **Persistence of Configuration** | **Intact Across Reboots (`mtd11`/`mtd12`)** | `/perm` and `/3rd_rw` persist UBIFS writes safely; `dtv_svc` preserves `/3rd_rw/nettv` via `/3rd_rw/upgrade/customer_version` sentinel. |
| **10** | **Protection Against Unauthorized Mods** | **Strong on Core / Open on `mtd12` w/ Signature** | Unsigned flashes to `load`/`ker`/`rfs`/`3rd` either halt (`0xfb000520`) or fail `dm-verity`. User customization cleanly targets `/3rd_rw` via signed `smth` updates. |
