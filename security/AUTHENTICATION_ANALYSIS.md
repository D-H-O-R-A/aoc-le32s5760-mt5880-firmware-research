# Authentication, Privilege & Session Analysis

## 1. Operating System Account & Password Store Audit

Direct filesystem inspection of `extracted/appfs1/etc/` reveals an authentic minimalist single-user appliance configuration:

- **`/etc/passwd`:** Contains literally one account:
  ```text
  root:x:0:0:root:/basic:/bin/sh
  ```
- **`/etc/group`:**
  ```text
  root:x:0:root
  ```
- **`/etc/shadow`:** **Does NOT exist** (`exists=False`). Calling standard `login`/`getty` authentication against an `"x"` shadow placeholder without `etc/shadow` either fails interactive login or relies solely on `-n -l /bin/sh` / `-l /sbin/autologin` passwordless bypasses.

### Boot-Time Autologin Hooks
- **`/etc/inittab` (Production Hardened):** Line 22 is commented out (`#1:2345:respawn:/sbin/getty -n -L ttyMT0 115200 vt100 -l /sbin/autologin`), preventing automatic root prompt spawn over UART0 on retail boot. (`/sbin/autologin` binary remains present in `appfs1/sbin/`.)
- **`/etc/scripts/usb_console.sh` (Cmdline-Gated Passwordless Root):**
  ```sh
  usb_console_en=`cat /proc/cmdline | grep ttyUSB`
  if [ "$usb_console_en" != "" ]; then
      ...
      /sbin/getty -n -L ttyUSB0 115200 vt100 -l /bin/sh
  fi
  ```
  Notice the `-n` (*do not prompt for username*) and `-l /bin/sh` (*autologin directly to root shell*). In production, this remains dormant unless `ttyUSB` is injected into the bootloader kernel command line (`uenv` / U-Boot), which requires bypassing or modifying signed boot data (`ker`/`load`/`uenv` access).

---

## 2. Firmware Upgrade Authentication (`Autorun.upg`)

| Stage | Cryptographic Authenticator | Scope Verified | Flaw / Weakness Observed |
|---|---|---|---|
| **RSA-2048 Outer Signature** | `openssl` / `libdtv_common.so` raw PKCS#1 v1.5 check against `/ro_data/*_PubKey_*.pem` | Covers bytes `[0x80 : end-256]` (entire encrypted DLM header + MD5 slot + all chunks) | **Critically undermined by `SEC-02`**: `upgrade_loader.pkg#part:roda` ships `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem` & `COM_UPG_PriKey_Devt.pem`! |
| **Dual Symmetric AES-128-CBC** | Outer header `0x94102909 * 4` (`IV=0`); Chunks use `MD5(AES_Prod.key)` / `MD5(AES_Prod.iv)` (`33`-byte `\n`-inclusive) | Encrypts `#DH@FiRm` metadata, `"reserved mtk inc"`, and chunk SHA-256 | Keys hardcoded in `libdtv_common.so` (`0x098b64`) or bundled in `roda` (`ro_data_keys`); provides obfuscation/integrity routing rather than strong secrecy |

---

## 3. Network Service & Application Authentication

- **DIAL (`dialserver`) & DLNA (`libqtdlna.so`):** Designed as local home-network protocols; zero authentication tokens, pairing codes, or HTTPS mutual TLS observed in `vendor/` configs (`dial.conf`). Any host on the same Wi-Fi/Ethernet broadcast segment can dispatch DIAL launch requests.
- **SystemManager `dynqml` Hook (`0x1db58c`):** `/3rd_rw/sm_config.ini` controls UI replacement unconditionally based on filesystem toggle (`dynqml=true`), trusting `/3rd_rw` (`mtd12`) without a secondary signature check once written.
