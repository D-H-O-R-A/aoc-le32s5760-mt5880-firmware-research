# Network Communication Analysis (`AOC LE32S5760/20`)

> **Endpoint Inventory CSV:** [EXTERNAL_ENDPOINT_INVENTORY.csv](EXTERNAL_ENDPOINT_INVENTORY.csv) (`291` statically confirmed entries) | **Network Diagram:** [diagrams/NETWORK_ARCHITECTURE.svg](../diagrams/NETWORK_ARCHITECTURE.svg)

## 1. Methodological Constraint: Static Binary Observation vs. Uncaptured Wire Traffic

**Important Epistemic Boundary:** Live controlled packet capture (`tcpdump` / `Wireshark` / TLS MITM proxy against physical TV hardware powered on in an isolated lab VLAN) was **NOT performed** in this workspace. Consequently:
- Every host, URL, protocol, and port listed here and in [EXTERNAL_ENDPOINT_INVENTORY.csv](EXTERNAL_ENDPOINT_INVENTORY.csv) represents a **statically verified artifact compiled into binaries, configuration files, or X.509 CRL/CA stores**.
- Static presence proves **reachability intent or compiled capability**, NOT active payload transmission, transmission cadence, or personal data content on live networks (see [PRIVACY_ASSESSMENT.md](PRIVACY_ASSESSMENT.md) and [TELEMETRY_ANALYSIS.md](TELEMETRY_ANALYSIS.md)).

---

## 2. Network Stack & Interface Daemons Observed

| Layer / Binary | File Path | Observed Network Behavior / Config |
|---|---|---|
| **Kernel Networking** | `scratch/vmlinux.bin` + `star_mac.ko` + `rt5572sta.ko` | IPv4 + IPv6 (`net/ipv6/*`, `sit.c`), `nf_conntrack` + `nf_nat`, `eth0` wired + `ra0` Ralink RT5572 USB Wi-Fi |
| **IPv4 / IPv6 Address Allocation** | `appfs1/sbin/{udhcpc, dhcpc.script, dns.script}`, `appfs1/bin/dibbler-client`, `etc/scripts/dhcpv6.sh` | DHCPv4 & stateful/stateless DHCPv6 (`dibbler-client`) |
| **Interface Monitor** | `appfs1/sbin/mnet_down.script` (respawned in `inittab`) | Polls `/tmp/interface_down` every `0.5s`; brings down `eth0` and `ra0` via `ifconfig` |
| **Firewall** | `rootfs1/bin/iptables/iptables-1.4.15/xtables-multi` | Shipped in `/3rd/bin/iptables`, though no active inbound `DROP` rule script runs in `etc/init.d/rcS` / `rc.local` |
| **Connectivity Probes** | `appfs1/bin/jsapp`, `dtv_common`, `net_ck.conf` | References `http://www.google.com`, `http://www.bbc.co.uk`, `http://speedtest.oui-0x00199d.com/st.jpg` (`OUI 00-19-9D` = Vizio/TPV/AmTRAN family test probe!) |
| **LAN Discovery & Casting** | `rootfs1/vendor/dialserver/dialserver`, `libqtdlna.so`, `libmDNSResponderPosix.so`, `libwfd.so` | DIAL SSDP (`239.255.255.250`), local loopback `http://localhost:56789/dialData?app=YouTube`, UPnP/DLNA, mDNS/DNS-SD |

---

## 3. Classification of Extracted Static URLs (`291` Unique Matches)

| Category | Confirmed Sample Hosts / URLs (`EXTERNAL_ENDPOINT_INVENTORY.csv`) | Owning Binary / File | Transport |
|---|---|---|---|
| **OEM Portal & Smart TV Backend** | `https://www.ecdinterface.philips.com/DevicePortalICPRequestHandler/RequestHandler.ashx`, `https://nettv.corio.com/BluePortServlets/BookmarkUrl`, `https://nettvacc.corio.com/...`, `https://sp-test1-origin.portal.nettvservices.com/...`, `http://www.pds.philips.com/download_request` | `libnettv.so`, `libhtvLib.so`, `libmtkapp.so` | HTTPS (TLS 1.0) & HTTP |
| **Netflix NRD SDK** | `https://nrdp.nccp.netflix.com/nccp/controller`, `https://nrdpv6.nccp.netflix.com/...`, `https://api-global.netflix.com`, `https://uiboot.netflix.com/apps/gibbontvui/upgrade_policy`, `https://tenfootui.netflix.com/...` + QA strings (`mvc102qa.netflix.com`, `foobar.netflix.com`) | `nrd-app`, `common.xml`, `gibbon.xml`, `error.js` | HTTPS (`OpenSSL 1.0.0d`) & QA HTTP |
| **YouTube & Legacy Partners** | `http://www.youtube.com/tv`, `https://www.youtube.com/tv`, `http://www.youtube.com/dial`, `https://ap.spotify.com`, `http://philips-2014.ce.skype.net`, `http://www.meethue.com/api/nupnp` | `dialserver`, `libnettv.so`, `libspotify.so`, `jsapp` | Mixed HTTP / HTTPS |
| **DRM Licensing & Clock** | `http://playready.directtaps.net/pr/svc/rightsmanager.asmx`, `http://services.wmdrm.windowsmedia.com/SecureClock/?Time`, `https://ms3.service.hostedmarlin.com:8443/hms/ms3/rights/...`, `https://wstfcps005.shibboleth.tv/widevine/cypherpc/cgi-bin/...` | `libPRGlue.so`, `libplayready.so`, `libnettv.so` | Unencrypted HTTP (`PlayReady`) & HTTPS |
| **Opera Browser & CA CRLs/OCSP** | `https://bugs.opera.com/`, `http://sitecheck2.opera.com/banner/%u/`, multiple `crl.*`/`ocsp.*` strings inside `libmarlin.so` / `opcacrt6.dat` / `cacerts` | `opera`, `libopera_hbbtv.so`, `browser.js`, `libmarlin.so` | HTTP / HTTPS |

---

## 4. Cryptographic & TLS Transport Findings Affecting Privacy

1. **Pre-2012 TLS Cipher Suite Ceiling (`OpenSSL 1.0.0d`):** Modern CDN endpoints (`api-global.netflix.com`, `youtube.com/tv`, `nettv.corio.com`) enforce TLS 1.2/1.3 with forward-secret ECDHE/AEAD suites; `OpenSSL 1.0.0d` is rejected at handshake level by current web infrastructure.
2. **Stale Trust Store (`opcacrt6.pem`):** `57` of `186` Opera root certificates have expired before `2026` (`9` were already expired in `2016`), and newer CA roots (e.g., Let's Encrypt `ISRG Root X1`, DigiCert `Global Root G2`) are absent.
3. **Plaintext HTTP Legacy Endpoints:** Endpoints such as `http://www.pds.philips.com/download_request`, `http://speedtest.oui-0x00199d.com/st.jpg`, `http://services.wmdrm.windowsmedia.com/SecureClock/?Time`, and QA URLs use unencrypted HTTP `80`, allowing passive on-path observation if contacted.
