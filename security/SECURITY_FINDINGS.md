# Security Findings Registry (`SEC-01` – `SEC-10`)

> **Controls Matrix:** [SECURITY_CONTROLS_INVENTORY.csv](SECURITY_CONTROLS_INVENTORY.csv) | **Hardening Telemetry:** [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md)  
> **Scoring Basis:** Every finding includes unique ID, concrete binary/cryptographic evidence, required exploitation preconditions, bounded impact, principled CVSS v3.1 environmental/base estimation (reflecting static analysis without live shell execution), confidence, and mitigations.

---

## Summary Matrix

| ID | Finding Title | Severity (Est. CVSS v3.1) | Confidence | Primary Evidence |
|---|---|---|---|---|
| **SEC-01** | Single-User `root` Execution Without `/etc/shadow` or MAC Isolation | **High** (`7.8–8.8` dep. vector) | **CONFIRMED** | `etc/passwd` (`root:x:0:0`), no `etc/shadow`, all daemons UID `0` |
| **SEC-02** | OEM Private Signing Keys Distributed Inside Factory `upgrade_loader.pkg` (`roda`) | **High** (`7.1` AV:L/PR:N -> forged UPG) | **CONFIRMED** | `LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem` in `roda` |
| **SEC-03** | End-of-Life `OpenSSL 1.0.0d` & `libcurl 7.21.7` (Max TLS 1.0/1.1) | **High** (`7.4` AV:N/AC:H MITM) | **CONFIRMED** | `libssl.so.1.0.0`, `libcurl.so.4.2.0` (`libcurl/7.21.7`) |
| **SEC-04** | Decayed & Weak Cryptographic CA Store (`opcacrt6.pem`: `MD2`/`MD5`/`SHA-1`/`1000b`–`1024b` RSA + `57/186` Expired) | **High** (`7.4` AV:N/AC:H MITM) | **CONFIRMED** | OpenSSL 3.0 audit: `1` MD2 (`1000b`), `7` MD5, `106` SHA-1, `18` RSA`<2048b`, `17` err, `WoSign` |
| **SEC-05** | `10+`-Year Legacy OS & C Parser CVE Debt (`Linux 3.0.13`, `glibc`, `libxml2`, `expat`, `zlib`, `BusyBox`) | **High** (`7.5–8.1` reachable parsers) | **CONFIRMED (Version)** | [sbom/KNOWN_VULNERABILITIES.md](../sbom/KNOWN_VULNERABILITIES.md) |
| **SEC-06** | Unauthenticated LAN Control & XML Discovery Surfaces (`DIAL`, `DLNA/UPnP`, `mDNS`, No Firewall) | **Medium** (`6.5` AV:A LAN) | **CONFIRMED (Static)** | `dialserver`, `libqtdlna.so`, `mDNSResponder`, zero `iptables` rules loaded |
| **SEC-07** | Hardcoded Outer DLM AES-128 Key (`0x94102909 * 4`) & `33`-Byte `\n` MD5 Derivation | **Medium** (`5.5` AV:L) | **CONFIRMED** | `libdtv_common.so` (`0x098b64..0x098b78`) |
| **SEC-08** | Updater `sub_404f28` Device Path Bug (`"/dev/nand_%d"` `-22 ENOENT`) & `3rdp` Bank-Swap Skip | **Medium** (`4.6` Availability/Brick) | **CONFIRMED** | `libmtkapp.so` (`0x404f54`, `0x40ae80`) |
| **SEC-09** | Unchecked `/3rd_rw` (`mtd12`) Persistence Enabling `SMConfig` `dynqml` & Browser Config Override | **Low-Medium** (`4.4` Post-Auth/Local) | **CONFIRMED** | `ubi4:3rd_rw`, `dtv_svc @ 0x036190`, `libnettv @ 0x1889a0`, `0x1db58c` |
| **SEC-10** | Universal Absence of RELRO, Stack Canaries, PIE & `_FORTIFY_SOURCE` Across `16/16` Audited App ELFs | **High (Defense-in-Depth Multiplier)** | **CONFIRMED** | `LC_ALL=C readelf` table in [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md) |

---

## Detailed Finding Specifications

### `SEC-01` — Single-User `root` Execution Model Without `/etc/shadow`
- **Description & Evidence:** `extracted/appfs1/etc/passwd` defines only `root:x:0:0:root:/basic:/bin/sh`, `/etc/shadow` is absent, no LSM (`SELinux`/`AppArmor`) enforces MAC policy, and every network/browser binary (`dtv_svc`, `SystemManager`, `browser.out`, `netflix`, `dialserver`) runs directly as UID `0`.
- **Preconditions:** Not directly remotely exploitable standalone; requires chaining with either a parser/memory-corruption flaw (`SEC-05`/`SEC-06`/`SEC-10`) or kernel command-line tampering for `usb_console.sh` (`ttyUSB` blocked by signed kernel).
- **Technical Impact:** Escalates any arbitrary code execution inside browser, UPnP/DLNA renderer, or USB media parser directly to persistent root control and read access over `/ro_data` keys.
- **Recommendations:** Run untrusted network listeners (`dialserver`, `opera`, `nrd-app`) under non-root UIDs in dedicated mount/PID namespaces; keep TV on segmented VLAN.

### `SEC-02` — Private RSA Signing Keys Bundled Inside Distributable Factory `roda` Partition
- **Description & Evidence:** `upgrade_loader.pkg#part:roda` (`ubi3:ro_data`) includes `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem` and `COM_UPG_PriKey_Devt.pem` alongside public keys and `AES_Prod.key/.iv`.
- **Preconditions & Bounded Impact:** Requires extracting `LE32S5760_V2.011_V0.2.zip` and applying an `.upg` file locally via USB (`Home > Setup > Software Update > Local`). **Crucial Boundary:** Because BootROM (`0xfb0034f0`), `kerA`/`kerB`, and `NFSB` RSA-1024 private keys are **NOT** in `roda`, this leak only affects `LT0`/`Devt` `.upg` acceptance targeting writable overlays (`/3rd_rw`), NOT `dm-verity` `rfsA`/`3rdA` flash replacement or European (`EU0..EU2`) units carrying only public PEMs.
- **Recommendations:** Exclude all `PriKey` `.pem` artifacts from factory OTA/PKG `roda` builds; sign packages exclusively on air-gapped HSMs.

### `SEC-03` — Obsolete `OpenSSL 1.0.0d` & `libcurl 7.21.7` Transport Stack
- **Description & Evidence:** `libssl.so.1.0.0` (`OpenSSL 1.0.0d`, 2011) and `libcurl/7.21.7` max out at TLS 1.0/1.1 without TLS 1.2/1.3 or modern AEAD suites, exposing historical 1.0.0-branch vulnerabilities (`CVE-2015-0285`..`0293`, `CVE-2016-0704`).
- **Preconditions & Impact:** Active MITM (`AV:N/AC:H`) or legacy TLS endpoint communication causes handshake failures against modern streaming servers and downgrade/oracle risks on permissive endpoints.

### `SEC-04` — Decayed Cryptographic Root CA Trust Store (`opcacrt6.pem`)
- **Description & Evidence:** Auditing all `186` X.509 blocks in `rootfs1/nettv/opera/opera_dir/opcacrt6.pem` via OpenSSL 3.0.13 proves:
  - **`17`** certificates fail modern X.509 DER/ASN.1 parsing (`ParseErrors=17`).
  - **`1`** root uses broken **`md2WithRSAEncryption` + `1000`-bit RSA** (`RSA Data Security, Inc.`, exp 2010); **`7`** use **`md5WithRSAEncryption`** (`BBC FMT Greenhouse` exp 2028, `Equifax`, `GTE`, `NetLock`); **`106` (`62.7%` of parsed roots!)** use **`sha1WithRSAEncryption`**; **`18`** RSA roots use **`<2048`-bit moduli** (`17` x `1024b` + `1` x `1000b`); **`9`** expired `<=2016`; **`57`** expired `<2026`; distrusted **`WoSign CA Limited`** remains present; modern **`ISRG Root X1` / `DigiCert Global Root G2`** are missing.
- **Preconditions & Impact:** Web browsing (`T3`) or MITM against weak MD5/SHA-1/1024-bit trust anchors risks chosen-prefix CA collision impersonation on TLS 1.0 clients while failing handshakes with modern valid websites.

### `SEC-05` — Extensive End-of-Life Third-Party C/C++ Parser Debt
- **Description & Evidence:** Ships `Linux 3.0.13`, `glibc 2.12.2`, `BusyBox 1.15.3`, `libxml2 2.7.8`, `expat 2.0.1`, `zlib 1.2.3`, `libpng 1.2.43`, and `sqlite 3.7.2` ([sbom/KNOWN_VULNERABILITIES.md](../sbom/KNOWN_VULNERABILITIES.md)).
- **Preconditions & Impact:** Untrusted XML (DLNA/DIAL/HbbTV), HTTP, or media files parsed under UID `0` without memory-corruption defenses (`SEC-10`).

### `SEC-06` — Unauthenticated LAN Discovery & App Control Daemons (`DIAL`, `DLNA`, `mDNS`)
- **Description & Evidence:** Ships `dialserver`, `libqtdlna.so`, `libmicrohttpd.so.10`, and `libmDNSResponderPosix.so` with `iptables-1.4.15` unconfigured in `etc/init.d/rcS` / `rc.local`.
- **Preconditions & Impact:** Same-subnet host (`AV:A`) can discover and invoke `DIAL` endpoints (`YouTube`/`Netflix`) or fuzz XML/UPnP handlers. Live runtime bound port numbers unverified statically without LAN nmap scan.

### `SEC-07` — Hardcoded DLM Outer AES-128 Key (`0x94102909 * 4`)
- **Description & Evidence:** `libdtv_common.so` (`0x098b64..0x098b78`) constructs static AES key `09291094` * 4 (`IV=0`) and applies `MD5()` over `33`-byte `\n`-inclusive key/IV files for inner chunks.
- **Impact:** Removes outer container header confidentiality across `TPV_MTK2K14PLF` updates (independent of RSA-2048 authenticity).

### `SEC-08` — Updater `sub_404f28` Device Path Bug (`"/dev/nand_%d"`) & `3rdp` Failover Skip
- **Description & Evidence:** `libmtkapp.so` formats `"/dev/nand_10"` (`-22 ENOENT`) for `<METHOD>PART</METHOD>` (`r6==0 @ 0x404f54`) and skips A/B bank swapping (`0x40ae80`) on `TAG=3rdp`.
- **Impact:** Causes deterministic `8`-second update abort (`REINICIAR OU TENTAR NOVAMENTE`) or single-bank brick exposure during `3rdp` power loss.

### `SEC-09` — Unsigned Persistence Surface on UBIFS `/3rd_rw` (`mtd12`)
- **Description & Evidence:** `mtd12` (`/3rd_rw`) omits `dm-verity` (`-o no_chk_data_crc`) and hooks UI replacement (`SMConfig` `dynqml` @ `0x1db58c`), `Opera` config merge (`libnettv @ 0x1889a0`), and `dtv_svc` preservation (`0x036190`).
- **Preconditions & Impact:** Post-exploitation or valid `smth` `.upg` write persists custom QML and ES5 `user.js` across reboots while leaving core RO flash intact.

### `SEC-10` — Universal Absence of Compiler Binary Hardening Across `16/16` Audited App/OEM ELFs
- **Description & Evidence:** Automated `readelf -h -l -d --dyn-syms` analysis proves **`100%` (`16/16`)** of audited executables and OEM/third-party shared libraries (`dtv_svc`, `busybox`, `dmsetup`, `fw_printenv`, `SystemManager`, `browser.out`, `netflix`, `dialserver`, `libmtkapp.so`, `libdtv_common.so`, `libssl.so.1.0.0`, `libcurl.so.4.2.0`, `libnettv.so`, `libopera_hbbtv.so`, `libxml2.so.2.7.8`) ship with **`RELRO = NONE`**, **`Stack Canary = False`**, and **`_FORTIFY_SOURCE = 0`**, while **all 8 executables** lack **PIE (`Type=EXEC` fixed `0x8000` load base)** — only `GNU_STACK RW (NX)` is active, despite `libc-2.12.2.so` confirming GCC `4.5.1` toolchain support (`PARTIAL RELRO`, `Canary=True`, `75` `_chk` symbols).
- **Preconditions:** Attacker must trigger an existing stack/heap memory corruption bug inside a reachable parser (`SEC-05` / `SEC-06`).
- **Technical Impact:** Eliminates GOT write-protection, stack buffer overflow termination cookies, and executable address randomization (`ASLR` code gadgets remain at deterministic fixed addresses inside `browser.out`, `dtv_svc`, and `SystemManager`), drastically lowering exploit engineering cost under UID `0` (`SEC-01`).
- **Recommendations:** Compile all userland binaries with `-fPIE -pie -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,relro,-z,now`.
