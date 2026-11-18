# Security Findings Registry (`SEC-01` – `SEC-09`)

> **Methodology:** Every entry below follows strict evidence criteria ([SECURITY_CONTROLS_INVENTORY.csv](SECURITY_CONTROLS_INVENTORY.csv)): no theoretical issue is elevated to an exploitable vulnerability without stating exact evidence, affected components, required preconditions, realistic technical impact, and verifiable remediation.

---

## Summary Table

| ID | Title | Severity | Confidence | Affected Component(s) |
|---|---|---|---|---|
| **SEC-01** | Absence of Process Isolation / All Core Daemons & Browser Run as `root` Without `/etc/shadow` | **High** | **CONFIRMED** | `etc/passwd`, `dtv_svc`, `SystemManager`, `opera`, `dialserver` |
| **SEC-02** | OEM Private Signing Keys & AES Materials Embedded in Distributable Factory `roda` Image | **High** | **CONFIRMED** | `upgrade_loader.pkg#part:roda` (`ro_data_keys/*.pem/.key/.iv`) |
| **SEC-03** | End-of-Life `OpenSSL 1.0.0d` & `libcurl 7.21.7` (Max TLS 1.0/1.1, Known CVEs) | **High** | **CONFIRMED** | `libssl.so.1.0.0`, `libcrypto.so.1.0.0`, `libcurl.so.4.2.0` |
| **SEC-04** | Aged & Compromised Opera CA Trust Store (`57/186` Expired Roots + `WoSign`) | **High** | **CONFIRMED** | `rootfs1/nettv/opera/opera_dir/opcacrt6.pem` |
| **SEC-05** | Over a Decade of Unpatched Parser & OS Libraries (`libxml2`, `expat`, `zlib`, `BusyBox`, `Linux 3.0.13`) | **High** | **CONFIRMED** | Rootfs shared libs + `appfs1` binaries (see [KNOWN_VULNERABILITIES.md](../sbom/KNOWN_VULNERABILITIES.md)) |
| **SEC-06** | Unauthenticated Local Area Network Services (`DIAL`, `DLNA/UPnP`, `libmicrohttpd`) | **Medium** | **CONFIRMED (Static)** | `dialserver`, `libqtdlna.so`, `libmDNSResponderPosix.so` |
| **SEC-07** | Hardcoded Outer DLM AES Key & Weak Key Derivation Structure (`Autorun.upg`) | **Medium** | **CONFIRMED** | `extracted/appfs1/basic/libdtv_common.so` (`0x098b64`) |
| **SEC-08** | Updater `sub_404f28` Device Path Bug (`"/dev/nand_%d"` `-22 ENOENT`) & `3rdp` Bank-Toggle Skip | **Medium (Availability/DoS)** | **CONFIRMED** | `extracted/appfs1/basic/libmtkapp.so` (`0x404f28`, `0x40ae80`) |
| **SEC-09** | Unchecked `/3rd_rw` (`mtd12`) Persistence Allowing `SMConfig` `dynqml` UI/NetTV Override | **Low-Medium (Post-Auth/Local)** | **CONFIRMED** | `mtd12` (`/3rd_rw`), `SystemManager`, `libnettv.so`, `dtv_svc` |

---

## Detailed Structured Finding Records

### `SEC-01` — Single-User `root` Execution Model Without `/etc/shadow`
- **Description:** The embedded OS ships a single account (`root:x:0:0:root:/basic:/bin/sh` in `/etc/passwd`), omits `/etc/shadow` completely, lacks SELinux/AppArmor MAC confinement, and executes every internet-facing or LAN-facing process (`opera`, `nrd-app`, `dialserver`, `SystemManager`, `dtv_svc`) directly as UID `0`.
- **Evidence:** `appfs1/etc/passwd`, `appfs1/etc/group`, absence of `appfs1/etc/shadow`, startup flow in `appfs1/basic/autorun.sh`.
- **Affected Component:** Whole Linux userspace (`appfs1` / `rootfs1`).
- **Required Preconditions:** Attacker must first achieve arbitrary code execution via another vector (e.g., crafted media/web payload in `opera` or LAN parser in `dialserver`/`libqtdlna`), because `ttyMT0` is commented out in `/etc/inittab` and `usb_console.sh` requires `"ttyUSB"` in kernel `cmdline`.
- **Technical Impact:** Any single memory corruption vulnerability inside the browser, DLNA renderer, or USB parser instantaneously yields full `root` access with ability to read `/ro_data` keys and tamper with `/perm`/`/3rd_rw`.
- **Severity:** **High** (Zero defense-in-depth privilege separation). **Confidence:** **CONFIRMED**.
- **Recommendations:** For OEMs: run network/browser/media daemons under dedicated low-privilege UIDs (`nobody`/sandbox), adopt `seccomp`/namespaces on modern BSPs. For owners: isolate the TV on a segmented IoT VLAN.

### `SEC-02` — Private Upgrade Signing Keys Distributed Inside Public `upgrade_loader.pkg` (`roda`)
- **Description:** The `roda` UBI image bundled inside the downloadable official firmware update `LE32S5760_V2.011_V0.2.zip` contains not only public verification certificates (`*_PubKey_Prod.pem`) and AES encryption keys (`AES_Prod.key/.iv`), but also private RSA key artifacts (`TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`).
- **Evidence:** File listing extracted from `upgrade_loader.pkg#part:roda` (contents excluded from Git per policy).
- **Affected Component:** `Autorun.upg` upgrade authenticity checks in `libdtv_common.so` (`LT0` LATAM / Devt profiles).
- **Required Preconditions:** Physical USB access (`Home > Setup > Software Update > Local`) **or** pre-existing code execution on TV. Crucially, BootROM/Kernel `NFSB` RSA-1024 private keys (`rfsA`/`3rdA`/`kerA`) are **NOT** present in `roda`, so `dm-verity` & kernel gates remain intact!
- **Technical Impact:** Compromises package authenticity separation for `.upg` updates targeting `LT0` writable overlays (`smth`), turning RSA-2048 `.upg` validation from an asymmetric OEM gate into a shared secret recoverable from the factory image.
- **Severity:** **High** (OEM PKI private key leakage in public firmware distribution; bounded by intact kernel `NFSB` gate). **Confidence:** **CONFIRMED**.
- **Recommendations:** Never embed `PriKey` `.pem` files or plaintext upgrade AES keys into target flash images (`/ro_data`); keep only offline HSM-guarded private keys and public verification keys on device.

### `SEC-03` — Obsolete `OpenSSL 1.0.0d` & `libcurl 7.21.7` Cryptographic Transport Layer
- **Description:** Core HTTPS networking across `dtv_svc`, `nrd-app`, `ginga`, and system libraries links against `OpenSSL 1.0.0d` (released February 2011) and `libcurl 7.21.7`, lacking TLS 1.2/1.3, modern AEAD ciphers (`GCM`, `ChaCha20-Poly1305`), and modern Elliptic Curve parameter support.
- **Evidence:** `extracted/appfs1/basic/lib/libssl.so.1.0.0`, `libcurl.so.4.2.0` (`libcurl/7.21.7`, CERTI build path referencing `openssl-1.0.0d`).
- **Required Preconditions:** Active network/MITM position (`T2`/`T3`) during TLS handshakes or legacy server interactions.
- **Technical Impact:** Exposes sessions to historical protocol weaknesses affecting `1.0.0` series (SSLv3/TLS 1.0 downgrade, weak RC4/CBC suites, ASN.1/X.509 parsing flaws in the 1.0.0 branch prior to 1.0.0r) and breaks compatibility with modern strict TLS 1.2+/1.3 streaming APIs (Netflix/YouTube).
- **Severity:** **High**. **Confidence:** **CONFIRMED**.
- **Recommendations:** Disable legacy Smart TV streaming apps over untrusted WAN; use external modern streaming hardware over HDMI.

### `SEC-04` — Aging `opcacrt6.pem` CA Bundle (`9` Expired by 2016, `57` Expired <2026, `WoSign` Present)
- **Description:** Opera's root CA store (`opcacrt6.pem`, `186` X.509 certificates) already included `9` roots expired on or before the 2016 release (`A-Trust-nQual-03` expired Aug 2015, `Juur-SK` expired Aug 2016), accumulates `57` expired roots prior to 2026 (`AddTrust External CA Root` expired May 2020), retains distrusted issuers (`WoSign CA Limited`), and omits modern roots (`ISRG Root X1` / Let's Encrypt).
- **Evidence:** Direct OpenSSL parsing in [FIRMWARE_METADATA.json](../firmware-forensics/FIRMWARE_METADATA.json).
- **Required Preconditions:** Network HTTPS browsing (`T3`).
- **Technical Impact:** Modern HTTPS websites fail certificate verification, while retaining distrusted CA roots increases impersonation exposure if TLS 1.0 connections succeed.
- **Severity:** **High** (Operational availability break + trust store hygiene failure). **Confidence:** **CONFIRMED**.
- **Recommendations:** Do not use the onboard Opera browser for authenticated or sensitive web sessions; use `/3rd_rw/nettv` hardening strictly on isolated test networks.

### `SEC-05` — Extensive End-of-Life C/C++ Parser & Kernel Component Debt
- **Description:** Ships `Linux 3.0.13`, `BusyBox 1.15.3`, `glibc 2.12.2`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`, `libpng 1.2.43`, and `sqlite 3.7.2` with numerous historical memory-corruption and DoS CVEs mapped in [sbom/KNOWN_VULNERABILITIES.md](../sbom/KNOWN_VULNERABILITIES.md).
- **Required Preconditions:** Delivery of malformed XML/PNG/gzip/network frames to `opera`, `libqtdlna`, USB gallery, or network clients.
- **Technical Impact:** Crash or potential arbitrary code execution under `root` UID (`SEC-01`).
- **Severity:** **High** (Component version match confirmed; live exploit chains not weaponized in this static audit). **Confidence:** **CONFIRMED**.

### `SEC-06` — Unauthenticated LAN Discovery & App Control (`DIAL`, `DLNA`, `mDNS`)
- **Description:** Ships `dialserver` (`http://localhost:56789/dialData?app=YouTube` loopback bridge), `libqtdlna.so`, and `libmDNSResponderPosix.so` without documented pairing tokens, TLS, or inbound host ACLs (`iptables` shipped but no filtering scripts invoked in `rc.local`).
- **Required Preconditions:** Layer-2/3 same-subnet LAN access (`T2`); TV powered on (`dtv_svc` / `dialserver` running).
- **Technical Impact:** Untrusted LAN hosts (guests, compromised IoT devices) can trigger YouTube/Netflix launches or fuzz XML/SSDP parsers. Exact live open TCP/UDP ports on retail runtime remain **UNMEASURED** pending LAN scan against physical TV.
- **Severity:** **Medium**. **Confidence:** **CONFIRMED (Static config) / INFERRED (Runtime socket state)**.

### `SEC-07` — Hardcoded DLM AES-128 Key (`0x94102909 * 4`) in `libdtv_common.so`
- **Description:** Outer `#DH@FiRm` upgrade header encryption relies on a deterministic repeating 32-bit word (`09 29 10 94` * 4, zero IV) reconstructed directly via `movw`/`movt` instructions (`0x098b64`).
- **Required Preconditions:** Possession of `libdtv_common.so` from `upgrade_loader.pkg`.
- **Technical Impact:** Removes container header confidentiality across the entire `TPV_MTK2K14PLF` line (does not by itself bypass RSA-2048 signature verification).
- **Severity:** **Medium**. **Confidence:** **CONFIRMED**.

### `SEC-08` — `libmtkapp.so` Path-Formatting Bug (`"/dev/nand_10"`) & Absent `3rdp` Failover
- **Description:** Flashing an `.upg` with `<METHOD>PART</METHOD>` causes `sub_404f28` (`r6 == 0`) to format `"/dev/nand_%d"` rather than `"/dev/mtd%d"`, failing `c_fm_erase_flash_part` with `-22 ENOENT` after ~8 seconds (`...` -> `"REINICIAR OU TENTAR NOVAMENTE"`). Additionally, `0x40ae80` skips A/B bank swap for `3rdp` tags.
- **Required Preconditions:** Local USB update with `METHOD=PART` or `TAG=3rdp`.
- **Technical Impact:** Update failure (denial of upgrade) or brick vulnerability if an in-place single-bank flash write is interrupted.
- **Severity:** **Medium**. **Confidence:** **CONFIRMED**.

### `SEC-09` — Unsigned Persistence Override Surface on `/3rd_rw` (`mtd12`)
- **Description:** Unlike `mtd4..mtd10`, `/3rd_rw` (`mtd12` UBIFS) is mounted writable without `dm-verity` (`no_chk_data_crc`) and exposes configuration override entry points into `SystemManager` (`SMConfig` `dynqml` @ `0x1db58c`) and `libnettv.so` (`_imnettv_copydata` copying `/3rd_rw/nettv/opera_new.ini`, `urlfilter.ini`, `user.js`).
- **Required Preconditions:** Local write access to `/3rd_rw` via valid `smth` `.upg` package (requiring `LT0` signing key / `SEC-02`) OR prior root code execution (`SEC-01`).
- **Technical Impact:** Enables persistent UI replacement (`HSMain.qml`) and browser DOM script (`user.js`) persistence across reboots without altering RO SquashFS partitions.
- **Severity:** **Low-Medium** (Requires prerequisite `.upg` signature or local root). **Confidence:** **CONFIRMED**.
