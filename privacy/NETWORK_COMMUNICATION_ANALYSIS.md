# Network Communication Analysis (`AOC LE32S5760/20`)

> **Endpoint Inventory CSV:** [EXTERNAL_ENDPOINT_INVENTORY.csv](EXTERNAL_ENDPOINT_INVENTORY.csv) (`291` statically verified URLs) | **Network Diagram:** [diagrams/NETWORK_ARCHITECTURE.svg](../diagrams/NETWORK_ARCHITECTURE.svg)

## 1. Methodological Constraint: Static Strings vs. Uncaptured Wire Traffic

**Explicit Epistemic Boundary:** Live controlled packet capture (`tcpdump` / `Wireshark` / TLS MITM proxy against physical TV hardware on an isolated VLAN) was **NOT performed** in this offline workspace. Accordingly:
- Every host, URL, IPC endpoint, and trust anchor documented below represents a **statically verified string or library binding** observed inside `appfs1` or `rootfs1`.
- Static URL presence demonstrates compiled capability or residual config references — **not** verified runtime exfiltration cadence or PII payload contents ([PRIVACY_ASSESSMENT.md](PRIVACY_ASSESSMENT.md), [TELEMETRY_ANALYSIS.md](TELEMETRY_ANALYSIS.md)).

---

## 2. Dynamic Network & IPC Bindings Observed Across Core Binaries (`readelf -d`)

| Daemon / Shared Lib | Dynamic Library Count | Network / HTTP / DRM / Discovery Dependencies (`DT_NEEDED`) |
|---|---|---|
| **`dtv_svc`** (`4.25 MB`) | `41` | `libssl.so.1.0.0`, `libcrypto.so.1.0.0`, `libcurl.so.4`, `libcares.so.2`, `libhttplive.so`, `libliveMedia.so`, `libnetwork_detect.so`, `libwfd.so`, `libhdcp2x.so`, `libnettv_proxy.so` |
| **`libnettv.so`** (`2.75 MB`) | `36` | `libcurl.so.4`, `libssl.so.1.0.0`, `libcares.so.2`, `libmarlin.so`, `libhttplive.so`, `libWVPlaybackAPI.so`, `libWVStreamControlAPI.so`, `libplayready.so`, `libSSPK.so` |
| **`browser.out`** (`Opera`) | `20` | `libopera_hbbtv.so` (`15.7 MB`), `libopera_hbbtv_appman.so`, `libhtvLib.so`, `libuva.so`, `libdirectfb.so` |
| **`dialserver` & `mDNS`** | — | SSDP multicast strings `239.255.255.250` (`1900`), local loopback `http://localhost:56789/dialData?app=YouTube`, `libmicrohttpd.so.10`, `libmDNSResponderPosix.so`, `libqtdlna.so` (`1.52 MB`) |

Additionally, `/etc/inittab` continuously respawns `/sbin/mnet_down.script` (`polling /tmp/interface_down` every `0.5s` to tear down `eth0`/`ra0`), while `etc/scripts/dhcpv6.sh` manages `dibbler-client` over IPv6 alongside IPv4 `udhcpc`. Although `rootfs1/bin/iptables/iptables-1.4.15/xtables-multi` is bundled, no active inbound `DROP` rule script runs in `etc/init.d/rcS` / `rc.local`.

---

## 3. Classification of Extracted Static URLs (`291` Confirmed Entries)

| Category | Representative Confirmed URLs (`EXTERNAL_ENDPOINT_INVENTORY.csv`) | Owning Artifact(s) | Transport / State |
|---|---|---|---|
| **OEM Smart TV Portals & OTA Strings** | `https://www.ecdinterface.philips.com/DevicePortalICPRequestHandler/RequestHandler.ashx`, `https://nettv.corio.com/BluePortServlets/BookmarkUrl`, `https://nettvacc.corio.com/BluePortServlets/BluePortHome`, `http://www.pds.philips.com/download_request`, `http://speedtest.oui-0x00199d.com/st.jpg` | `libnettv.so`, `libhtvLib.so`, `libmtkapp.so`, `libdtv_common.so` | Legacy `OpenSSL 1.0.0d` HTTPS + plaintext HTTP (`speedtest` / `pds`) |
| **Netflix NRD 4.0 SDK** | `https://nrdp.nccp.netflix.com/nccp/controller`, `https://nrdpv6.nccp.netflix.com/...`, `https://uiboot.netflix.com/apps/gibbontvui/upgrade_policy`, `https://tenfootui.netflix.com/...` (+ residual QA hosts `mvc102qa.netflix.com:7001`, `foobar.netflix.com:6359`) | `nrd-app/netflix`, `common.xml`, `gibbon.xml`, `error.js` | Built `2015-04-20`; blocked today by TLS 1.2/1.3 & cipher requirements |
| **YouTube, Spotify & Partner Apps** | `http://www.youtube.com/tv`, `https://www.youtube.com/tv`, `http://www.youtube.com/dial`, `https://ap.spotify.com`, `http://post.audioscrobbler.com/?hs=true...`, `http://philips-2014.ce.skype.net`, `http://www.meethue.com/api/nupnp` | `dialserver`, `libnettv.so`, `libspotify.so`, `jsapp` | Mixed HTTP / legacy HTTPS |
| **DRM Provisioning & Secure Clock** | `http://playready.directtaps.net/pr/svc/rightsmanager.asmx`, `http://services.wmdrm.windowsmedia.com/SecureClock/?Time`, `https://ms3.service.hostedmarlin.com:8443/hms/ms3/rights/...`, `https://wstfcps005.shibboleth.tv/widevine/cypherpc/cgi-bin/{Ack,GetEMMs,Heartbeat}.cgi` | `libPRGlue.so`, `libplayready.so`, `libnettv.so` | Clear HTTP (`PlayReady`) & HTTPS |
| **QA / Test Staging Strings Left In Release** | `https://sp-test1-origin.portal.nettvservices.com/...`, `http://certification.nettvservices.com/.../marlin/prod/license_008_11.xml`, `http://drmtests.farncombe.eu/...`, `http://www.test.bbc.co.uk` | `libhtvLib.so`, `libnettv.so`, `dialserver` | Residual staging strings left in shipped binaries |

---

## 4. Root Cause Analysis of Complete HTTPS Breakage on Modern Internet Endpoints

Auditing both layers simultaneously explains why modern HTTPS browsing and streaming cannot operate natively:
1. **TLS Protocol Ceiling (`OpenSSL 1.0.0d`, Feb 2011):** Lacks `TLS 1.2` (`RFC 5246`), `TLS 1.3` (`RFC 8446`), `AEAD` (`AES-GCM` / `ChaCha20`), and modern cipher negotiation required by Cloudflare, Akamai, Google, and Netflix CDNs.
2. **X.509 Trust Store Decay (`opcacrt6.pem`):** Auditing `186` certs proves **`57` expired `<2026`** (`9` already expired at August `2016` release!), **`106` `SHA-1`**, **`8` `MD2`/`MD5`**, **`18` RSA`<2048` bits**, **`17` malformed for OpenSSL 3**, retained `WoSign`, and **absence** of `ISRG Root X1` (Let's Encrypt) and modern CA roots ([CRYPTOGRAPHIC_ANALYSIS.md](../security/CRYPTOGRAPHIC_ANALYSIS.md)).
