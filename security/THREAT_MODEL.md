# Threat Model (`AOC LE32S5760/20` Smart TV Platform)

> **Diagram:** [diagrams/SECURITY_THREAT_MODEL.svg](../diagrams/SECURITY_THREAT_MODEL.svg) | **Attack Surface:** [ATTACK_SURFACE_ANALYSIS.md](ATTACK_SURFACE_ANALYSIS.md)

## 1. System Assets Under Protection

| Asset ID | Protected Asset | Location in Architecture | Security Property Desired |
|---|---|---|---|
| **A-01** | Verified Boot & Kernel Root of Trust | Mask BootROM, OTP eFuse `0xf0008664`, `load`, `kerA`/`kerB`, `rfsA`/`rfsB`, `3rdA`/`3rdB` | Boot integrity & execution authenticity |
| **A-02** | DRM Secrets, Platform Provisioning Keys & Device ID | `/ro_data` (`mtd13`), Widevine/PlayReady/Marlin key objects, HDCP keys | Confidentiality & extraction resistance |
| **A-03** | Writable Smart TV Config & Persistent State | `/3rd_rw` (`mtd12`), `/perm` (`mtd11`), `/tmp/opera_home` | Integrity against unauthorized UI/browser tampering |
| **A-04** | Viewer LAN Privacy & Local Control | User viewing state, LAN DIAL/DLNA state, Wi-Fi credentials (`wpa_supplicant`) | Availability & protection against unauthorized remote app launch / MITM |

---

## 2. Adversary Classes & Realistic Capabilities

| Actor ID | Adversary Profile | Initial Access / Preconditions | Realistic Threats Against This Unit | Blocked By / Mitigations |
|---|---|---|---|---|
| **T1** | **Unprivileged Physical / USB User** | Access to external USB port & IR remote UI (`Autorun.upg` local update dialog) | Attempting unauthorized firmware downgrade/custom flash via UI; inserting crafted NTFS/FAT32 media triggering `libxml2`/`libpng`/`ntfs-3g` parser bugs | `BootROM + NFSB` block arbitrary boot code; non-persistent exploits lost on reboot unless writing `/3rd_rw` or `/perm` |
| **T2** | **LAN-Adjacent Attacker (Same Home/Guest Wi-Fi)** | Layer-2/3 adjacency on Ethernet/WLAN (`eth0`/`ra0`) | Unauthenticated SSDP/DIAL HTTP API probing (`dialserver`), DLNA/UPnP parser fuzzing (`libqtdlna.so`), plain-HTTP captive portal/ARP/DNS spoofing against EoL `OpenSSL 1.0.0d` | Firewall/guest VLAN isolation at router level (TV hosts no shipped local inbound `iptables` drop rules) |
| **T3** | **Remote Web / Malicious Portal / MITM** | User browsing arbitrary site in Opera `Presto 6213` OR active internet MITM | Downgrade to TLS 1.0 / weak ciphers; forging TLS certs under compromised/expired roots (`WoSign`); Presto JS engine memory corruption as `root` | Hardened `urlfilter.ini` (`custom_payload`) + network separation; **NO in-browser sandbox** on TV |
| **T4** | **Lab Researcher w/ Physical Board Teardown** | Desoldering raw NAND IC / external NAND programmer + UART TX/RX probing | Full offline NAND dump extraction (`roda` key extraction, reverse engineering) | `0xf0008664` OTP eFuse still rejects unauthorized bootloaders even on offline programmer rewrites! |

---

## 3. Trust Boundaries

1. **Boundary TB-1 (Unverified External Media/Network -> Rootfs Services):** Terminates external HTTP/UPnP/USB traffic inside UID `0` daemons (`opera`, `dialserver`, `dtv_svc`) without MAC (`SELinux`) or user namespaces.
2. **Boundary TB-2 (Read-Only Signed Verity Volumes -> Mutable UBIFS):** Separates `dm-verity` `NFSB` zones (`mtd4..10`) from unchecked writable `mtd11`/`mtd12` (`/perm`, `/3rd_rw`).
3. **Boundary TB-3 (MaskROM / Preloader OTP -> Main U-Boot & Linux):** Enforces irreversible silicon policy at `0xf0008664 & 0x100000`.
4. **Boundary TB-4 (Offline Factory Distribution Package -> Cryptographic Keys):** *Broken* in `upgrade_loader.pkg#part:roda`, where factory `.zip` distribution leaks private `.pem` keys alongside public verification keys ([SECURITY_FINDINGS.md](SECURITY_FINDINGS.md) `SEC-02`).
