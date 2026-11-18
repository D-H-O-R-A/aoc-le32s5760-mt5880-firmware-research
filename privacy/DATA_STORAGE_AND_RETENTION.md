# User & Device Data Storage and Retention Analysis

## 1. Volatility vs. Non-Volatile Persistence Across Partitions

| Storage Path | Backing Device & FS | Volatility & Lifecycle | Data Categories Stored (Confirmed / Inferred) | Retention / Wipe Behavior |
|---|---|---|---|---|
| **`/tmp/opera_home`** | `tmpfs` (RAM) | **Volatile** (cleared on every cold power-off / AC unplug) | Active `opera.ini`, browser session caches, temporary cookies during session | Automatically lost at power-off (`etc/fstab`: `none /tmp tmpfs defaults`); source defaults re-copied by `libnettv.so` |
| **`/var/run`, `/opt`** | `tmpfs` (RAM) | **Volatile** | PID files (`dibbler/client.pid`), IPC sockets, `/tmp/3rd_mounted` state flags | Wiped completely on reboot |
| **`/3rd_rw` (`mtd12`)** | NAND UBIFS (`ubi4:3rd_rw`) | **Persistent** across reboots | `/3rd_rw/nettv` overrides (`opera_new.ini`, `user.js`, `urlfilter.ini`), Netflix/Widevine app RW data (`3rd_rw_list.txt`), `/3rd_rw/upgrade/customer_version`, `sm_config.ini` | Retained across reboots; preserved by `dtv_svc @ 0x036190` while `customer_version` flag exists; overwritten only by explicit `smth` update or factory NAND wipe |
| **`/perm` (`mtd11`)** | NAND UBIFS (`ubi2:perm`) | **Persistent** across reboots | Channel lists, UI settings, Wi-Fi/network pairing/preferences, SQLite/persistent config | Retained across reboots (`mount -rw ubi2:perm /perm`); factory UI reset clears user settings while `pkg` reflash preserves or resets per script |
| **`/ro_data` (`mtd13`)** | NAND UBIFS (`ubi3:ro_data`) | **Factory Permanent (RO)** | Upgrade RSA verification/private keys, AES production keys, DRM provisioning materials (`mount -r`) | Mounted strictly read-only at OS runtime; only updated via low-level `upgrade_loader.pkg` (`roda`) |
| **EEPROM / NOR NVM** | Board EEPROM/NOR (`nor/storage.c`) | **Persistent** across reflashes | Bank flags (`A` vs `B`), panel/region/tuner configuration | Preserved across normal power cycles |

---

## 2. Security & Forensic Retention Implications

1. **Sanitization Prior to Disposal/Resale:** Performing a standard menu "Factory Reset" clears user preferences in UI databases, yet without physically reflashing `mtd11` (`/perm`) and `mtd12` (`/3rd_rw`) or wiping UBIFS blocks, cached tokens/Wi-Fi keys/bookmarks on `ubi2:perm` and `ubi4:3rd_rw` (including unlinked flash wear-leveling PEBs on raw NAND) may remain recoverable to hardware flash dumpers.
2. **Safe User Custom Data Isolation:** Keeping experimental browser/UI overrides inside `/3rd_rw` (`mtd12`) ensures temporary experiments never alter `/perm` channel scan data or read-only `/ro_data` calibration keys.
