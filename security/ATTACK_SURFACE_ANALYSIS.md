# Attack Surface Analysis (`Local`, `LAN`, `Web/TLS`, `Parser/Storage`)

## 1. Local & Physical Interfaces

| Surface | Entry Vector | Observed State in Firmware | Exploitation Constraints / Preconditions |
|---|---|---|---|
| **USB Upgrade Parser** | `Autorun.upg` (`Home > Setup > Software Update > Local`) | `libdtv_common.so` (`x_dlm_download_by_tag`) & `libmtkapp.so` (`sub_404f28`) run as `root` | Normally gated by RSA-2048; however, `LT0_UPG_PriKey_Prod.pem` leakage (`SEC-02`) enables forging valid `LT0` `.upg` signatures |
| **USB Media & Filesystem Auto-Mount** | FAT32, NTFS (`ntfs.ko`, `ntfs-3g`), FUSE (`fuse.ko`), USB HID | Auto-probed by `libusb_detect.so`, `ntfs-3g`, `libpng 1.2.43`, `libjpeg 62`, `FFmpeg 53` | Requires physical USB insertion (`T1`); media parser bugs run with `root` privileges |
| **UART / USB Debug Shells** | `/dev/ttyMT0` & `/dev/ttyUSB0` | `inittab` comments out `ttyMT0`; `usb_console.sh` spawns passwordless `/bin/sh` only when `/proc/cmdline` has `"ttyUSB"` | **Mitigated on locked hardware:** altering bootargs normally requires valid U-Boot/kernel access |
| **Boot Argument Helper** | `/etc/scripts/{auto, manual}_launch.sh` | Calls `/bin/fw_printenv +/- bootargs manual_launch` | Not callable remotely unless local code execution already obtained |

---

## 2. Local Area Network (LAN) Surfaces

*(Note: Because the TV unit was not connected to an isolated tcpdump/nmap test harness during this study, exact bound TCP/UDP port numbers reported below reflect confirmed daemon binaries and config strings rather than live `netstat` output — any unverified runtime socket status is flagged accordingly.)*

| Binary / Daemon | Observed Capabilities & Libraries | Exposed Functionality | Preconditions & Exposure Notes |
|---|---|---|---|
| **`dialserver`** (`rootfs1/vendor/dialserver/dialserver`) | Discovery & Screen Launch (`DIAL` v1 REST, SSDP `239.255.255.250`, HTTP `localhost:56789/dialData` referenced) | Launches YouTube (`/dial`) & Netflix apps on screen via LAN requests | Requires LAN adjacency (`T2`); no authentication token or PIN pairing configured in inspected `dial.conf` |
| **DLNA / UPnP (`libqtdlna.so`, `libminiupnpc.so`, `libmicrohttpd.so.10`)** | Embedded UPnP AV / HTTP server library in `SystemManager` (`1.52 MB`) | Media rendering / metadata XML exchange (`libxml2 2.7.8`, `libxerces-c-3.1`) | Requires LAN adjacency; exposes 2011-era XML parser to crafted SSDP/SOAP payloads |
| **mDNS / Zeroconf (`libmDNSResponderPosix.so`)** | Multicast DNSresponder (`dns_sd`) | Announces service records (`_dial`, DLNA) on LAN | LAN broadcast domain only |
| **Wi-Fi Direct / P2P (`libwfd.so`, `libp2p.so`)** | Wireless display / Miracast stack (`305,244` B + `84,360` B) | Wireless video sink control | Dependent on active P2P/Wi-Fi Direct session state |
| **IPv4 / IPv6 DHCP Clients (`udhcpc`, `dibbler-client`)** | `/etc/scripts/dhcpv6.sh`, `/sbin/dhcpc.script` | Parses network options via BusyBox / shell hooks as `root` | Rogue DHCP/RA server on malicious LAN |

---

## 3. WAN / Web / Application Surfaces

1. **Opera Devices Presto Engine (`6213`) & HbbTV (`libopera_hbbtv.so` `15.7 MB`):**
   - Full HTML/CSS/ES5 JS runtime + legacy plugins running unsandboxed as UID `0`.
   - `user.js` / `opera_new.ini` / `urlfilter.ini` loaded from writable `/3rd_rw/nettv` if initialized via `smth` updates.
2. **EoL TLS Stack (`OpenSSL 1.0.0d` + `libcurl 7.21.7` + `opcacrt6.pem`):**
   - Lacks TLS 1.2/1.3 (maxes out at TLS 1.0 / SSLv3 era).
   - `opcacrt6.pem` trusts `186` CAs including `9` roots already expired in `2016`, `57` expired prior to `2026`, and distrusted `WoSign CA Limited`.
3. **Multi-Binary Image/XML Stack:** `libpng 1.2.43`, `zlib 1.2.3`, `expat 2.0.1`, `libxml2 2.7.8`, `SQLite 3.7.2` shared widely across QML, Ginga, Opera, and `dtv_svc`.
