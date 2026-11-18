# Filesystem Architecture & Logical Organization

> **Full Entry Inventory:** [FILESYSTEM_INVENTORY.csv](FILESYSTEM_INVENTORY.csv) (`4,004` entries) | **Structure Diagram:** [diagrams/FIRMWARE_STRUCTURE.svg](../diagrams/FIRMWARE_STRUCTURE.svg)

## 1. Summary Composition (`appfs1` + `rootfs1`)

| Extracted Tree | Source PKG / NAND Partitions | Regular Files | Symlinks | Directories | Special Nodes | Verification Mode |
|---|---|---|---|---|---|---|
| `extracted/appfs1` | `rfsA`/`rfsB` (`mtd6`/`mtd7`, `51,466,240` B) | `416` | `190` | `94` | `1` FIFO (`/dev/initctl`) | **RO SquashFS + `NFSB` (`12,514` blks)** |
| `extracted/rootfs1` | `3rdA`/`3rdB` (`mtd9`/`mtd10`, `97,738,752` B) | `2,919` | `157` | `228` | `0` | **RO SquashFS + `NFSB` (`23,767` blks)** |
| Runtime `/3rd_rw` | `mtd12` (`3rdw`) | Device-initialized | — | — | — | **RW UBIFS (NO NFSB)** |
| Runtime `/perm` | `mtd11` (`perm`) | Device-initialized | — | — | — | **RW UBIFS (`-rw`, NO NFSB)** |
| Runtime `/ro_data` | `roda` (`mtd13`, `5,767,168` B) | Factory key/NVM UBI | — | — | — | **RO UBIFS (`mount -r`)** |

---

## 2. Logical VFS Runtime Hierarchy (Merged by `/etc/fstab` & `etc/scripts/*`)

```
/ (SquashFS RO via dm_mount_root_nfsb on mtd6/mtd7)
├── bin/          (BusyBox v1.15.3 applets, bash, dmsetup, fw_printenv, tar, sed)
├── sbin/         (init -> busybox, mnet_down.script, udhcpc, setmac, autologin)
├── lib/          (glibc 2.12.2, ld-2.12.2.so, libz 1.2.3, libpng12, libdirectfb, libdevmapper)
├── etc/          (inittab, fstab, profile, passwd [no shadow!], init.d/rcS, rc.d/rc.local, scripts/*)
├── basic/        (dtv_svc, autorun.sh, libmtkapp.so, libdtv_common.so, dtv_driver.ko, wifi_ko/*, lib/*)
├── dev/          (initctl FIFO, fb, fusion, mapper/dm-1, pts, snd)
├── proc/, sys/, tmp/, opt/, var/run/   (procfs / sysfs / tmpfs RW in-RAM mounts per /etc/fstab)
├── perm/         <- ubiattach -m 11 -d 2 (ubi2:perm RW UBIFS: TV channel DB, settings)
├── ro_data/      <- ubiattach -m 13 -d 3 (ubi3:ro_data RO UBIFS: UPG/DRM factory keys)
├── 3rd_rw/       <- ubiattach -m 12 -d 4 (ubi4:3rd_rw RW UBIFS: user-writable overlay, opera bookmarks, SM cache)
└── 3rd/          <- dmsetup create dm-1 verity mtdblock9/10 -> mount squashfs RO
      ├── bin/        (SystemManager Qt UI shell, jsapp, wpa_supplicant, iptables-1.4.15)
      ├── lib/        (libxml2 2.7.8, libmarlin.so, libmicrohttpd.so.10, libxerces-c-3.1, libyajl)
      ├── qt/         (Qt 4.8.3 libs + AEDK/SystemManager QML resources & icons)
      ├── nettv/      (Opera Presto 6213, libnettv.so, libopera_hbbtv.so, libspotify.so, opcacrt6.pem [186 CAs])
      ├── netflix/    (nrd-app, libJavaScriptCore.so, libWTF.so, data/resources & error UI)
      ├── ginga/      (Brazilian ISDB-Tb NCL/Lua engine, FFmpeg 53 libs, Boost 1.44.0, libcurl 7.21.7)
      ├── vendor/     (dialserver & startup glue)
      └── widevine/, playready/, leanback/, mpeg_dash/, mss/, nsd/ (mDNS)
```

---

## 3. Notable Structural Findings Across Trees

1. **Duplicate / Legacy Shared Libraries Across `/basic/lib` and `/3rd/*/lib`:**
   `OpenSSL 1.0.0d`, `libcurl 4.2.0` (`7.21.7`), `libexpat 2.0.1`, `libfreetype 6.6.x`, and `libxml2 2.7.8` appear in multiple subdirectories (`/lib`, `/basic/lib`, `/3rd/lib`, `/3rd/ginga/lib`) linked dynamically via an extensive `LD_LIBRARY_PATH` chain in `/etc/profile` (`9` appended paths!).
2. **`/bin/sh` & BusyBox Synergy:** `/basic/autorun.sh` and `/etc/scripts/*.sh` invoke both `#!/bin/sh` (BusyBox `ash` / `v1.15.3`) and `#!/bin/bash` (standalone `appfs1/bin/bash`), while `etc/scripts/rm_usb_mod.sh` still retains stale hardcoded checks for `"/lib/modules/2.6.27"`, exposing legacy MediaTek SDK inheritance from earlier kernel generations.
3. **Temporary RAM Symlink Redirects (`libnettv.so`):** At runtime, Opera configuration (`opera.ini`) and caches operate out of `/tmp/opera_home` (`tmpfs`), populated by `_imnettv_copydata` from `/3rd/nettv/opera/opera_home` or overridden safely from `/3rd_rw/nettv/opera_new.ini`.
