# Privacy Assessment (`AOC LE32S5760/20`)

> **Strict Methodological Rule:** No external host observed via `strings` or URL extraction is assumed to transmit personally identifiable information (PII) merely because its URL appears in firmware. Where runtime HTTP/DNS payloads were not captured on wire, PII impact is marked **UNCONFIRMED PENDING LIVE CAPTURE**.

---

## 1. Static Privacy Surface Evaluation

| Domain | Empirical Evidence Observed in Firmware | Privacy Risk & Epistemic Classification |
|---|---|---|
| **Portal / OEM Requests (`libnettv.so`, `libhtvLib.so`, `libmtkapp.so`)** | Compiled HTTPS endpoints (`ecdinterface.philips.com`, `nettv.corio.com`) + unencrypted HTTP download probe string (`pds.philips.com/download_request`) | **Static capability CONFIRMED**; exact device identifiers transmitted (e.g., MAC/model/serial/country) vs. deprecated DNS status **UNCONFIRMED without packet capture** |
| **Plaintext Speed / Reachability Tests** | `speedtest.oui-0x00199d.com/st.jpg` (`libdtv_common.so`), `www.google.com`, `www.bbc.co.uk` (`jsapp`) | **Medium (LAN/ISP metadata leakage)**: Clear HTTP requests leak active TV power-on timestamps & IP address to on-path observers if reached |
| **Browser History, Cookies & UserJS (`Opera` + `libnettv`)** | Runtime caches mapped through `/tmp/opera_home` (`RAM`), `/perm`, and `/3rd_rw/nettv`; custom `urlfilter.ini` supports local ad/tracker host blocking | **Local Persistence on `/3rd_rw`/`/perm`** (see [DATA_STORAGE_AND_RETENTION.md](DATA_STORAGE_AND_RETENTION.md)); `custom_payload/nettv/urlfilter.ini` mitigates third-party tracker domains statically |
| **LAN Broadcast Exposure (`DIAL` / `DLNA` / `mDNS`)** | `dialserver`, `libmDNSResponderPosix.so`, `libqtdlna.so` announce presence & active Smart TV apps on local subnet without authentication | **Low-Medium (Local Subnet)**: Reveals TV model / active casting availability to any host on the same LAN/Wi-Fi |
| **External Telemetry Beacons** | Presence of `/recommendURL.txt`, `post.audioscrobbler.com` (`libspotify.so`), Netflix/YouTube SDK configs | Exact telemetry payload fields **NOT DEMONSTRATED** statically (no live pcap captured) |

---

## 2. Controlled Network Capture Protocol (Recommended Future Work)

To transition static endpoint observations into empirically verified wire-traffic proofs:
1. Place the TV on an **isolated wired VLAN** behind a Linux router running `tcpdump -w tv_boot_capture.pcap` and DNS logging (`dnsmasq --log-queries`).
2. Record three distinct phases: (a) cold boot idle (`0–180s`), (b) Smart TV / Opera launcher entry, and (c) USB media + DIAL discovery probes.
3. Inspect DNS queries, HTTP `User-Agent`/headers, TLS SNI ClientHello handshakes (`OpenSSL 1.0.0d` cipher offers), and any non-TLS HTTP POST bodies before classifying any endpoint as actively exfiltrating device or user identifiers.
