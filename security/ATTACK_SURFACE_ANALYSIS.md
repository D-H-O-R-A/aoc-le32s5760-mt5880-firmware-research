# Attack Surface Analysis (`Local`, `LAN`, `Web/TLS`, `ELF Mitigations & PKI`)

## 1. Local & Physical Interfaces

| Surface | Entry Vector | Observed State in Firmware | Exploitation Constraints / Preconditions |
|---|---|---|---|
| **USB Upgrade Parser** | `Autorun.upg` (`Home > Setup > Software Update > Local`) | `libdtv_common.so` (`x_dlm_download_by_tag`) & `libmtkapp.so` (`sub_404f28`) run as `root` (`UID 0`) | Normally gated by RSA-2048; however, `LT0_UPG_PriKey_Prod.pem` leakage in `roda` (`SEC-02`) enables forging valid `LT0` `.upg` signatures |
| **USB Media & Filesystem Auto-Mount** | FAT32, NTFS (`ntfs.ko`, `ntfs-3g`), FUSE (`fuse.ko`), USB HID | Auto-probed by `libusb_detect.so`, `ntfs-3g`, `libpng 1.2.43`, `libjpeg 62`, `FFmpeg 53` | Requires physical USB insertion (`T1`); media parser vulnerabilities execute directly as `root` |
| **UART / USB Debug Shells** | `/dev/ttyMT0` & `/dev/ttyUSB0` | `inittab` comments out `ttyMT0`; `usb_console.sh` spawns passwordless `/bin/sh` only when `/proc/cmdline` contains `"ttyUSB"` | **Mitigated on locked hardware:** `vmlinux` embeds built-in cmdline `"console=ttyMT0,115200n1 root=/dev/ram"`, and altering bootargs requires unlocked U-Boot/kernel |
| **Boot Argument Helper** | `/etc/scripts/{auto, manual}_launch.sh` | Calls `/bin/fw_printenv +/- bootargs manual_launch` | Not callable remotely unless local code execution is already obtained |

---

## 2. Binary Memory-Safety Mitigation Audit (`SEC-10`, Empirical `readelf`)

Even if a parser bug requires prior attack-surface reachability (USB media, DIAL/UPnP LAN, Opera web runtime), post-exploitation severity is magnified by a **complete absence of compiler exploit mitigations across application and OEM binaries** (`SECURITY_CONTROLS_INVENTORY.csv`, [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md)):

- **`16/16` (`100%`) Audited Application/OEM ELFs Have Zero Exploit Hardening (`GNU_STACK RW` NX Only):** Including core executables (`dtv_svc` linking **`41` `DT_NEEDED` shared libraries**, `SystemManager`, `browser.out` linking **`20` `DT_NEEDED` libraries**, `netflix`, `dialserver`, `busybox`, `dmsetup`, `fw_printenv`) and middleware (`libmtkapp.so`, `libdtv_common.so`, `libnettv.so` linking **`36` `DT_NEEDED` libraries**, `libopera_hbbtv.so` `15.7 MB`, `libssl.so.1.0.0`, both `libcurl.so.4.2.0` builds, `libxml2.so.2.7.8`). Every single one reports **`RELRO=NONE`**, **`Stack Canary=False`**, **`_FORTIFY_SOURCE=0`**, and fixed non-PIE `ET_EXEC` virtual load addresses on all `8` executables.
- **Compiler Support Proven Available But Unutilized:** By contrast, `appfs1/lib/libc-2.12.2.so` (`EGLIBC`) ships with **`PARTIAL RELRO`**, **`Stack Canary=True`** (`__stack_chk_fail`), and **`75` `_FORTIFY_SOURCE` (`__*_chk`) wrapper symbols**, proving the CodeSourcery/GCC `4.5.1` (`451_vfp_ca9`) toolchain supported full hardening flags that were omitted from vendor Makefiles (`-Wl,-z,relro,-z,now`, `-fstack-protector`, `-fPIE`, `-D_FORTIFY_SOURCE=2`).

---

## 3. Local Area Network (LAN) Surfaces

*(Note: Because the TV unit was not connected to an isolated `tcpdump`/`nmap` test harness during this study, bound daemon roles reported below reflect statically inspected ELF binaries and configuration files rather than live `netstat` observations — runtime port binding remains unverified dynamically.)*

| Binary / Daemon | Observed Capabilities & Libraries | Exposed Functionality | Preconditions & Exposure Notes |
|---|---|---|---|
| **`dialserver`** (`rootfs1/vendor/dialserver/dialserver`) | Discovery & Screen Launch (`DIAL` v1 REST, SSDP `239.255.255.250`, `localhost:56789/dialData` referenced) | Launches YouTube (`/dial`) & Netflix apps on screen via LAN requests | Requires LAN adjacency (`T2`); no authentication token or PIN pairing configured in inspected `dial.conf`; runs unhardened (`Non-PIE`, `RELRO=NONE`, `No Canary`) |
| **DLNA / UPnP (`libqtdlna.so`, `libminiupnpc.so`, `libmicrohttpd.so.10`)** | Embedded UPnP AV / HTTP server library in `SystemManager` (`1.52 MB`) | Media rendering / metadata XML exchange (`libxml2 2.7.8`, `libxerces-c-3.1`) | Requires LAN adjacency; exposes 2011-era XML parsers inside non-hardened UID `0` `SystemManager` |
| **mDNS / Zeroconf (`libmDNSResponderPosix.so`)** | Multicast DNS responder (`dns_sd`) | Announces service records (`_dial`, DLNA) on LAN | LAN broadcast domain only |
| **Wi-Fi Direct / P2P (`libwfd.so`, `libp2p.so`)** | Wireless display / Miracast stack (`305,244` B + `84,360` B) | Wireless video sink control | Dependent on active P2P/Wi-Fi Direct session state |
| **IPv4 / IPv6 DHCP Clients (`udhcpc`, `dibbler-client`)** | `/etc/scripts/dhcpv6.sh`, `/sbin/dhcpc.script` | Parses network options via BusyBox / shell hooks as `root` | Rogue DHCP/RA server on malicious LAN |

---

## 4. WAN, Opera Web Runtime & Trust-Store (`opcacrt6.pem`) Surfaces

1. **Opera Devices Presto Engine (`6213`) & HbbTV (`libopera_hbbtv.so` `15.7 MB` + `browser.out` `20` deps + `libnettv.so` `36` deps):**
   - Full HTML/CSS/ES5 JS runtime + legacy plugins running unsandboxed as `UID 0` with `RELRO=NONE`, `No Canary`, non-PIE `EXEC` (`browser.out`), and `_FORTIFY_SOURCE=0`.
   - `user.js` / `opera_new.ini` / `urlfilter.ini` loaded from writable `/3rd_rw/nettv` if initialized via `smth` updates.
2. **EoL TLS Stack (`OpenSSL 1.0.0d` + `libcurl 7.21.7`):**
   - Built against `2011`-era cipher/protocol support (`SSLv3`/`TLS 1.0`), incompatible with modern `TLS 1.2`/`1.3` AEAD-only endpoints (`curl` / `OpenSSL` handshake incompatibility).
3. **Quantified X.509 Trust-Store Decay (`opcacrt6.pem` = `186` Certificates via `OpenSSL 3.0.13`):**
   - **`17` (`9.1%`)** fail strict OpenSSL `3.0` X.509 parsing (`169` parsed cleanly).
   - Cryptographic distribution across the `169` parsed anchors: **`1` `md2WithRSAEncryption` (`1000`-bit `RSA Data Security` root)**, **`7` `md5WithRSAEncryption`**, **`106` (`62.7%`) `sha1WithRSAEncryption`**, `43` `sha256WithRSAEncryption`, `4` `sha384WithRSAEncryption`, `6` `ecdsa-with-SHA384`, `2` `ecdsa-with-SHA256`, and **`18` RSA keys `< 2048` bits** (`17` x `1024`-bit + `1` x `1000`-bit).
   - Temporal decay: **`9` roots already expired at factory ship year (`<= 2016`)** and **`57` expired prior to `2026`**, alongside distrusted anchors such as `WoSign CA Limited`.
4. **Shared Legacy Parser Exposure:** `libpng 1.2.43`, `zlib 1.2.3`, `expat 2.0.1`, `libxml2 2.7.8`, and `SQLite 3.7.2` are linked across QML, Ginga (`arm_mtk451`), Opera, and `dtv_svc`.
