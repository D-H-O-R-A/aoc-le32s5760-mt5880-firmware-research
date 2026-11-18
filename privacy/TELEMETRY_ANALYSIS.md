# Telemetry & Analytics Capability Analysis

## 1. Epistemic Distinction: Capability vs. Active Collection

Because all forensic investigation in this study was performed statically on `LE32S5760_V2.011_V0.2.zip` without live hardware packet capture, telemetry-related findings strictly separate:
- **CONFIRMED Static Artifacts:** Diagnostic URLs, reporting helpers, and third-party analytics/DRM SDK hooks compiled into `appfs1` and `rootfs1`.
- **UNOBSERVED Wire Behavior:** Whether those hosts currently resolve, whether user opt-in consent gates block transmission, and exact byte payloads transmitted on boot or playback.

---

## 2. Compiled Diagnostic, Portal & Partner Endpoints Found

| Component | Artifact Observed | Exact Host / Endpoint (`EXTERNAL_ENDPOINT_INVENTORY.csv`) | Functional Category | Verification Status |
|---|---|---|---|---|
| **OEM Device Portal / NetTV** | `rootfs1/nettv/libnettv.so`, `libhtvLib.so` | `https://www.ecdinterface.philips.com/DevicePortalICPRequestHandler/RequestHandler.ashx`, `https://nettv.corio.com/BluePortServlets/BookmarkUrl` | Smart TV portal bootstrap & bookmark/app catalog | URL confirmed in ELF; active beacon payload **UNOBSERVED** |
| **Bandwidth / Connectivity Test** | `appfs1/basic/libdtv_common.so`, `rootfs1/bin/jsapp` | `http://speedtest.oui-0x00199d.com/st.jpg`, `http://www.google.com`, `http://www.bbc.co.uk` | Link-check / bandwidth estimation probe | URL confirmed; trigger schedule requires live capture |
| **Netflix NRD SDK** | `rootfs1/netflix/nrd-app/...` | `https://nrdp.nccp.netflix.com/nccp/controller`, `https://uiboot.netflix.com/...` (+ residual QA hosts `mvc102qa.netflix.com`, `lgux-mdxapp1.corp.netflix.com`) | Streaming session bootstrap & legacy NRD telemetry/QA test configs | Config strings confirmed; blocked today by OpenSSL `1.0.0d` TLS obsolescence |
| **Widevine Heartbeat / EMM** | `rootfs1/nettv/libnettv.so` | `https://wstfcps005.shibboleth.tv/widevine/cypherpc/cgi-bin/{Ack,GetEMMs,Heartbeat}.cgi` | Legacy Widevine DRM periodic session heartbeat | URL present in library; only active during Widevine session |
| **Opera & Spotify SDKs** | `libopera_hbbtv.so`, `browser.js`, `libspotify.so` | `http://sitecheck2.opera.com/banner/%u/`, `http://post.audioscrobbler.com/?hs=true&...` | Opera site compatibility banner & Last.fm/Audioscrobbler scrobbling hook in `libspotify.so` | Static string in third-party SDK; user-initiated if ever used |
| **Pre-Release QA Leftovers** | `rootfs1/nettv/libnettv.so`, `libhtvLib.so` | `https://sp-test1-origin.portal.nettvservices.com/...`, `http://certification.nettvservices.com/.../marlin/prod/license_008_11.xml`, `http://drmtests.farncombe.eu/...` | Staging/certification test endpoints retained in release binaries | Confirmed dead/test strings in release firmware |

---

## 3. Practical Privacy Mitigation Without Breaking TV Tuner Function

For residential use today (using the `AOC LE32S5760/20` primarily as a local HDMI display / digital tuner):
1. Leave Ethernet unplugged and Wi-Fi unconfigured for 100% zero network exposure.
2. When LAN access is needed (e.g., local DLNA media playback), place the TV on a WAN-blocked VLAN (`RFC1918`-only LAN access) and apply DNS sinkholing for unwanted third-party tracking hosts — complemented by [custom_payload/nettv/urlfilter.ini](../custom_payload/nettv/urlfilter.ini) at the Opera browser layer.
