# Coordinated Responsible Disclosure Policy

## 1. Context of Legacy End-of-Life (EoL) Hardware

The target device (**AOC LE32S5760/20**, `TPV MTK2K14PLF` platform) runs firmware built around **August 3–4, 2016** (`Linux 3.0.13`, `BusyBox v1.15.3`, `glibc 2.12.2`, `OpenSSL 1.0.0d`, `libcurl 7.21.7`, `Qt 4.8.3`, Opera `Presto 6213`). At the time of this publication (`2026`), the platform is roughly a decade post-release and outside active consumer software maintenance cycles.

## 2. Classification of Security Observations

Architectural findings documented in [security/SECURITY_FINDINGS.md](security/SECURITY_FINDINGS.md) and [security/SECURITY_ASSESSMENT.md](security/SECURITY_ASSESSMENT.md) fall into two distinct categories:

1. **Structural / Hardware-Bound Platform Characteristics:**
   - Presence of `root:x:0:0` without `etc/shadow` in extracted initramfs/rootfs (`appfs1/etc/passwd`) alongside boot scripts allowing console spawn via kernel command line (`usb_console.sh` gating on `ttyUSB` in `/proc/cmdline`, `inittab` having `ttyMT0` commented out). Note that exploitation of `usb_console.sh` requires either kernel command-line tampering (which is upstream-blocked by U-Boot kernel signature verification on retail secure-boot units) or physical UART board access.
   - Use of textbook/unpadded raw `pow(sig, 3, N)` comparison (`e = 3`) in kernel `nfsb_rsa_check`, mitigated in this specific binary by exact 1024-bit `mpuint_equal` against `0^96 || SHA256` (no trailing-garbage acceptance).
   - Multi-bank downgrade/re-flash semantics and hardcoded DLM AES wrapper (`0x94102909 * 4`) combined with per-chunk AES-128-CBC wrapping over `ro_data` key files (`TPV_MTK2K14PLF_LT0_UPG_AES_Prod.*`) and asymmetric RSA-2048 outer signatures.
2. **Legacy Third-Party Component Lifecycle Debt:**
   - End-of-life shared libraries (`OpenSSL 1.0.0d`, `libcurl 7.21.7`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`, `BusyBox 1.15.3`, `Linux 3.0.13`) and an aging `opcacrt6.pem` CA trust store (`186` root certificates containing expired anchors such as `Juur-SK` 2016 and `A-Trust-nQual-03` 2015, plus `AddTrust External CA Root` expired 2020 and `WoSign`).

## 3. Disclosure Posture and Vendor Notifications

- **No Zero-Day Weaponization:** This archive intentionally omits any bypass exploit for active DRM (PlayReady, Widevine, Marlin, HDCP 2.x), private signing keys, or remote exploit PoCs targeting active consumer deployments.
- **Vendor Contact Channels:** Should any currently shipping TPV Technology / AOC / MediaTek hardware line share vulnerable configuration patterns (for example, shared hardcoded outer DLM keys or legacy update script behaviors), maintainers should direct coordinated disclosures to:
  - **TPV Technology / AOC Security & Support:** Official product security / regional technical support channels via [https://www.tpv-tech.com](https://www.tpv-tech.com) and [https://aoc.com](https://aoc.com).
  - **MediaTek Product Security Incident Response Team (PSIRT):** [https://corp.mediatek.com/product-security](https://corp.mediatek.com/product-security) (`security@mediatek.com`).
- **90-Day Standard & Redaction Rule:** Any newly discovered zero-day vulnerability affecting supported devices discovered in follow-up work must undergo standard 90-day coordinated vendor notification prior to public release.
