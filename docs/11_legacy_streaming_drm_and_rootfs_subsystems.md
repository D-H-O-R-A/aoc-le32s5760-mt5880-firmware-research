# Chapter 11 — Legacy Streaming, Hardware DRM Modules & Read-Only/Read-Write RootFS Bridging

**Scope:** Completing our architectural characterization of `extracted/rootfs1/` (`/3rd`), this chapter documents MediaTek's factory mechanism for bridging immutable SquashFS paths to writable UBIFS storage (`3rd_rw_list.txt`), dissecting the proprietary Adobe Flash Lite YouTube Leanback stack (`stagecraft`, `wrp_leanback`, `config.ini`), `Netflix nrd-app` RW symlinks, `Widevine` / `PlayReady` / `Smooth Streaming` (`SSPK`) / `MPEG-DASH` DRM & streaming libraries, `dialserver`, and the Latin American `Ginga` SBTVD interactive middleware.

---

## 11.1 Factory `3rd_rw_list.txt` Linking Architecture

Because `/3rd` (`rfs`/`3rdA` bank) executes atop read-only SquashFS guarded by `dm-verity` `NFSB` RSA-1024 (Chapter 2), applications that must cache state, store DRM device keyboxes, or persist cookies require explicit build-time redirections onto writable `mtd12` (`/3rd_rw`). Inspection of `3rd_rw_list.txt` inside `extracted/rootfs1/netflix/` and `extracted/rootfs1/widevine/` documents MediaTek's build-time symlink specification (`link-dir`, `data`, `link-file`):

### 11.1.1 Netflix Writable Storage Bindings (`extracted/rootfs1/netflix/3rd_rw_list.txt`)

```text
# 1. data:      copy files to output/3rd_rw/ and create symlink output/3rd/ -> /3rd_rw
# 2. link-dir:  mkdir in output/3rd_rw/ and create symlink output/3rd/ -> /3rd_rw
# 3. link-file: create symlink output/3rd/ -> /3rd_rw
link-dir,       netflix/nrd-app/data/var/nrd
link-dir,       netflix/nrd-app/data/cache
link-dir,       netflix
```

Correspondingly, filesystem listing inside `extracted/rootfs1/netflix/` confirms:
- `netflix -> /3rd_rw/netflix` (`symlink`)
- Inside `nrd-app/` (`10,201,088`-byte `netflix` ELF executable), runtime persistent cache (`DiskCachePath`, checked via `Gibbon` string banner at `evidence/05_runtime_engines_and_busybox_audit.txt`, line 11) writes out through symlinks pointing into `/3rd_rw/netflix/nrd-app/data/{var/nrd,cache}`.

### 11.1.2 Widevine Keybox Provisioning (`extracted/rootfs1/widevine/3rd_rw_list.txt`)

```text
data,       widevine/keybox
```

Listing `extracted/rootfs1/widevine/` confirms `keybox -> /3rd_rw/widevine/keybox` (`symlink`), accompanied by proprietary shared objects:
- `libWVPlaybackAPI.so` (`56,200` bytes)
- `libWVStreamControlAPI.so` (`2,062,204` bytes)

Note an important implication of `3rd_rw_list.txt` design: **DRM keyboxes (`widevine/keybox`) and Netflix `nrd` state live directly on `mtd12` (`/3rd_rw`) alongside `/3rd_rw/nettv`!** That reinforces why any USB `.upg` bundle using `<METHOD>FILE</METHOD>` must specify `<PATH>/3rd_rw/nettv</PATH>` **specifically** (never `/3rd_rw` at top level!), because `libmtkapp.so`'s `sub_407d4c` unconditionally runs `rm -rf <PATH>` prior to `mkdir <PATH>` (`evidence/03_upg_installer_disasm.txt`, line 116). Targeting top-level `/3rd_rw` would wipe `widevine/keybox`, `/3rd_rw/netflix`, and `/3rd_rw/upgrade/customer_version`!

---

## 11.2 Legacy YouTube Leanback Flash Stack (`extracted/rootfs1/leanback/`)

Unlike modern HTML5 MSE YouTube TV apps (`youtube.com/tv`), the AOC LE32S5760/20 ships an Adobe **Flash Lite** (`stagecraft`) Leanback client under `extracted/rootfs1/leanback/`:

| File Name | Size (Bytes) | Functional Purpose |
|---|---:|---|
| `wrp_leanback` | `17,740` | DirectFB/AM wrapper executable (`DT_NEEDED`: `23` libs including `libapp_if.so`, `libcurl.so.4`, `libssl.so.1.0.0`, `libmtal.so`) |
| `dfb_outputdims` | `4,664` | Queries DirectFB layer output resolution (`1920x1080` / panel geometry) |
| `config.ini` | `1,720` | `stagecraft --mtkcfg config.ini <swf_file>` runtime configuration |
| `youtube_keymap.ini` | `27` | Single key remapping line: `DFBKEY(8) = AEKEY_BACKSPACE` |
| `yt_lbl.swf` | `4,515` | Minimal Shockwave Flash Leanback loader SWF (`yt_lbl`) |
| `yt_font.swf` | `3,803,786` | Embedded `3.80 MB` Flash SWF font container |

### 11.2.1 `stagecraft` Runtime Parameters (`extracted/rootfs1/leanback/config.ini`)

Inspection of all `65` lines of `extracted/rootfs1/leanback/config.ini` characterizes how Flash Lite integrated with MediaTek `DFB` and `CMPB`:

- **`[mtkfl]`:** `enable = amclient,dockui,statemachine,system`; `disable = netdetect,usbdetect`.
- **`[stagecraft]` UI & Input Loop:** `key_repeat_interval = 800`, `key_repeat_period = 400`, `dfb_surface_lock = 1` (mandatory DirectFB surface lock/unlock), `dfb_double_buffer = 0` (single-buffer mode saving video DRAM within `512 MB`), `termination_timeout = 20000`, `ignore_key_src_bits = 1`.
- **`[stagecraft]` Network (`libcurl`):** `net_action_timeout = 60000`, `urlstream_retry = 0`, `urlstream_patch = 1`, `curl_connection_timeout = 20` (relying on `/basic/lib/libcurl.so.4` + `libssl.so.1.0.0` `1.0.0d`).
- **`[cmpb]` Video Pipeline:** `log_trace_playback = 0`, `pts_from_pos = 1` (maps `GetCurrentPos()` directly to `GetCurrentPTS()`).

Because Flash Lite `yt_lbl.swf` relies on long-retired Adobe Flash SWF TV player endpoints and external `libssl.so.1.0.0` (TLS 1.0 cap), native `wrp_leanback` cannot stream modern YouTube services.

---

## 11.3 Inventory of Additional Adaptive Streaming, DRM & Broadcast Middleware (`rootfs1/`)

Examining the remaining root directories under `extracted/rootfs1/` rounds out the complete subsystem map of the AOC LE32S5760/20:

| Directory (`extracted/rootfs1/`) | Principal Artifacts | Protocol / Standards Role | Coupled Kernel/Basic Dependencies |
|---|---|---|---|
| **`dialserver/`** | `dialserver` (`63,932 B`) | DIscovery And Launch (`DIAL`) HTTP/SSDP server for second-screen cast launching (YouTube/Netflix dial wakeups) | `libdtv_common`, network interfaces via `rc.local` |
| **`dlna/xml/`** | UPnP AV / DLNA XML device & service descriptions | MediaRenderer / Digital Media Player discovery | `dtv_svc`, `/3rd/dmsapp` |
| **`mpeg_dash/`** | `libmpdparser.so.1` (`539,856 B`) | MPEG-DASH MPD XML manifest parser | `libuva.so`, `libhttplive.so` |
| **`mss/`** | `SSPK_library/`, `include/` | Microsoft Smooth Streaming PlayReady Kit | `libSSPK.so` imported by `libnettv.so` |
| **`playready/`** | `libplayready.so` (`1,848,932 B`) | Microsoft PlayReady `2.x` DRM decryption & license client | Used by both `netflix` and `libnettv.so` (`libPRGlue.so`, `libuvadrmbackend-playready.so`) |
| **`widevine/`** | `libWVPlaybackAPI.so`, `libWVStreamControlAPI.so` | Google Widevine Classic DRM SDK | `libnettv.so` + `/3rd_rw/widevine/keybox` |
| **`nettv/` DRM & UVA Plugins** | `libMarlin.so` (`94,840 B`), `libspotify.so.12` (`2.60 MB`), `libuva.so`, `libuvabackend-{capi,mtk,tpvision}.so`, `libuvadrmbackend-clearkey.so`, `libTrace.so` | Adaptive streaming abstraction, Marlin/ClearKey DRM, Spotify legacy C runtime, debug trace | `browser.out` links `-capi`, `-tpvision`, `libhtvLib.so`, `libTrace.so` |
| **`ginga/` & `ginga_tbr/`** | `libginga_tbr_pic.so` & NCL/Lua libs | Brazilian **SBTVD / ISDB-T Ginga-NCL** interactive broadcast middleware (`autorun.sh` line 86) | Loaded dynamically by `dtv_svc` (`evidence/06`) |
| **`nsd/`** | `nsd/lib/` | Network Service Discovery support library (`autorun.sh` line 91 prepends `/3rd/nsd/lib`) | Background discovery services |
| **`wpa_supplicant/`** | Wi-Fi supplicant configs & binaries | Wireless WPA/WPA2 association (`rc.local` line 150 `/etc/config/wifi`) | Wi-Fi USB/internal modules (`ins_wifi_mod.sh`) |

---

## 11.4 Architectural Synthesis: Read-Only Core vs. Safe RW Customizations

```text
/                         (rfsA / rfsB @ mtd6/7)   -- SquashFS + NFSB RSA-1024 + dm-bht [IMMUTABLE]
├── /basic                (inside rfsA/B)          -- dtv_svc, libmtkapp, libdtv_common, libssl 1.0.0d
├── /3rd                  (3rdA / 3rdB @ mtd9/10)  -- SquashFS + NFSB RSA-1024 + dm-bht [IMMUTABLE]
│   ├── qt/AEDK/SystemManager                      -- Qt 4.8.3 qrc:// built-in QML (dynqml=0)
│   ├── nettv/            (browser.out, opera_hbbtv, libnettv.so -> reads opera_new.ini!)
│   ├── netflix/          (symlink -> /3rd_rw/netflix via 3rd_rw_list.txt)
│   ├── widevine/         (keybox -> /3rd_rw/widevine/keybox via 3rd_rw_list.txt)
│   └── leanback/         (stagecraft Flash Lite yt_lbl.swf)
├── /ro_data              (mtd13 UBI RO)           -- /ro_data/key/TPV_MTK2K14PLF_* [READ-ONLY]
├── /perm                 (mtd11 UBI RW)           -- Factory keys/DRM [DO NOT TOUCH]
└── /3rd_rw               (mtd12 UBI RW)           -- NO NFSB / NO dm-verity [SAFE WRITABLE]
    ├── upgrade/customer_version                   -- Preserved! Guards against Opera overwrite
    ├── netflix/                                   -- Untouched when targeting /3rd_rw/nettv
    ├── widevine/                                  -- Untouched when targeting /3rd_rw/nettv
    └── nettv/            <-- DELIVERABLE TARGET   -- <TAG>smth</TAG><METHOD>FILE</METHOD>
        ├── opera_new.ini                          -- Enables TLS 1.1 / TLS 1.2 & extensions
        ├── custom/urlfilter.ini                   -- Preserves lines 1..82 security filter + adblock
        ├── custom/user.css                        -- Remote op[code] glyphs + safe ad hiding
        └── custom/userjs/                         -- 6 stock JS + ES5 Promise/fetch/UA user.js
```
