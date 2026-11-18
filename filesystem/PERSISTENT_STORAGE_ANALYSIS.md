# Persistent Storage Analysis (`/perm`, `/3rd_rw`, `/ro_data`, `EEPROM`)

## 1. Non-Volatile Persistent Partitions Mapped at Runtime

While `rfsA`/`B` (`/`) and `3rdA`/`B` (`/3rd`) are strictly immutable SquashFS volumes protected by `NFSB` RSA-1024 and `dm-bht`, the firmware mounts **three separate UBI/UBIFS partitions** plus hardware EEPROM storage to handle configuration, factory keys, and state persistence across reboots:

| Partition & Device | Mount Point & Mode | Mount Command (`etc/scripts/*`) | Persistence Content & Role |
|---|---|---|---|
| `mtd11` (`perm`) -> `ubi2:perm` | `/perm` (**Read-Write**) | `mount -rw -t ubifs -o no_chk_data_crc -o bulk_read ubi2:perm /perm` | Core TV user preferences, channel/NVM databases, pairing/app state (exact live TV `/perm` files not in factory PKG) |
| `mtd12` (`3rdw`) -> `ubi4:3rd_rw` | `/3rd_rw` (**Read-Write**) | `mount -t ubifs -o no_chk_data_crc -o bulk_read ubi4:3rd_rw /3rd_rw` | Writable 3rd-party overlay! Houses `/3rd_rw/nettv` (Opera prefs/CAs/CSS/UserJS), `/3rd_rw/netflix`, `/3rd_rw/widevine`, `/3rd_rw/upgrade/customer_version`, and SystemManager QML override hooks |
| `mtd13` (`roda`) -> `ubi3:ro_data` | `/ro_data` (**Read-Only**) | `mount -r -t ubifs -o no_chk_data_crc -o bulk_read ubi3:ro_data /ro_data` | Factory-provisioned RSA public keys (`TPV_MTK2K14PLF_*_UPG_PubKey_Prod.pem`) & AES upgrade key/IV materials (protected by `-r` UBI mount + `/ro_data` provenance; see key separation below!) |
| Auxiliary NVM / EEPROM (`nor/storage.c`) | Hardware I2C/NOR | Accessed via `dtv_driver.ko` & `libmtkapp.so` | Active bank bit (`A` vs `B` for `ker`/`rfs`/`3rd`), TV model/board flags, standby state |

---

## 2. How Persistent Overrides Work on `/3rd_rw` (`mtd12`)

Disassembly and file-list analysis across `extracted/` ([evidence/06](../evidence/06_systemmanager_and_nettv_disasm.txt), [rootfs1/netflix/3rd_rw_list.txt](../docs/05_mtd12_rw_delivery_and_offline_verification_thesis.md)) confirm four persistent hooks spanning reboot cycles:

1. **Sentinel Preservation in `dtv_svc` (`0x036190..0x036314`):**
   On boot, `dtv_svc` checks for `/3rd_rw/upgrade/customer_version` (comparing with factory `/3rd/upgrade/customer_version`). When the sentinel file matches/exists, `dtv_svc` **skips wiping `/3rd_rw/nettv`**, preserving custom files across power cycles.
2. **Opera Runtime Merge in `libnettv.so` (`_imnettv_copydata @ 0x1889a0`):**
   Merges `/3rd_rw/nettv/opera_new.ini` cleanly into `/tmp/opera_home/opera.ini` and copies `/mnt/browser/opcacrt6.pem` when present, enabling non-destructive changes to `User-Agent`, DNS/TLS toggles, `User JS`, and `urlfilter.ini`.
3. **App State Whitelists (`3rd_rw_list.txt`):**
   Explicit configuration files (`netflix/3rd_rw_list.txt`, `widevine/3rd_rw_list.txt`, `leanback/config.ini`) dictate which mutable data folders map out of read-only `/3rd` onto writable `/3rd_rw`.
4. **SystemManager `SMConfig` `dynqml` Gate (`0x1db58c`):**
   If `/3rd_rw/sm_config.ini` sets `dynqml=true`, `SystemManager` branches away from built-in `qrc:/HomeScreen/HSMain.qml` to load mutable external QML layouts without modifying `mtd9`/`mtd10` (`3rdA`/`3rdB`).

---

## 3. Forensic Finding on `ro_data` (`/ro_data`) Factory Provisioning

While `/ro_data` is mounted **read-only (`-r`)** on the television to preserve OEM upgrade verification materials and DRM provisioning files, inspecting the factory `roda` UBI partition (`5,767,168` B) revealed that the factory archive includes **both** regional public verification keys (`*_PubKey_Prod.pem`) **and** `AES_Prod.key`/`iv` encryption secrets alongside development/LATAM test `.pem` artifacts (`TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`). Those filenames are noted strictly as structural evidence of key-hygiene flaws in the OEM image (`SEC-02`), while **100% of `.pem`/`.key`/`.iv` file contents are withheld and `.gitignore`d** per [ETHICAL_RESEARCH.md](../ETHICAL_RESEARCH.md).
