# Chapter 4 — Application Stack Reverse Engineering: `SystemManager`, `libnettv.so`, Opera Presto, Netflix NRDP & Legacy Defect Post-Mortem

**Scope:** Having established the hardware, kernel, and DLM upgrade boundaries, this chapter audits the runtime application stack inside `/3rd` (`rootfs1`) and `/basic` (`appfs1`): Qt `SystemManager`, `dtv_svc` provisioning, `libnettv.so` (`_imnettv_copydata`), `Opera/9.80 Presto`, `Netflix nrd-app`, Flash Lite `leanback`, Ginga SBTVD, legacy Spotify/DRM modules, and the complete engineering post-mortem of software defects eliminated from earlier project iterations. All facts are reproduced cleanly by [`scripts/inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py), [`scripts/disasm_systemmanager_and_nettv.py`](../scripts/disasm_systemmanager_and_nettv.py), and [`scripts/inspect_dmbht_and_boot_scripts.py`](../scripts/inspect_dmbht_and_boot_scripts.py).

---

## 4.1 `SystemManager` (`Qt 4.8.3` / `DirectFB 1.4.1`) & The `dynqml` Config Gate

The primary Home screen launcher (`/3rd/qt/AEDK/SystemManager/SystemManager`, `9,438,748` bytes, entry `0x00018d18`) is a compiled C++ Qt Embedded `4.8.3` + `QtDeclarative` (`QtQuick 1.1`) executable dynamically linked against `libdirectfb.so` (`17` libraries total in `DT_NEEDED`; `evidence/06_systemmanager_and_nettv_disasm.txt`, line 5). Crucially, `SystemManager` imports **no** media/browser libraries (`libcurl`, `libssl`, `libcmpb`, `libopera_hbbtv`) directly, functioning strictly as a Qt scene graph host and QML launcher orchestrating external binaries via IPC/system signals.

Literal pool resolution across `SystemManager` establishes the exact string anchors governing HomeScreen initialization (`evidence/05_runtime_engines_and_busybox_audit.txt`, lines 32–37):

```text
SM string 'sm_config.ini'                @ 0x250879 (VA 0x258879 / '/sm_config.ini' @ 0x258878)
SM string 'tpvlib'                       @ 0x2508b8
SM string 'dynqml'                       @ 0x2508d8
SM string 'qrc:/HomeScreen/HSMain.qml'   @ 0x256824 (VA 0x25e824)
SM string 'res/HomeScreen/HSMain.qml'    @ 0x256809 (VA 0x25e809 / '/res/HomeScreen/HSMain.qml' @ 0x25e808)
```

### 4.1.1 Disassembly Trace: `main` (`0x1619e4`), `SMConfig` (`0x16e428`), and `dynqml` Switch (`0x1db58c`)

From [`evidence/06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt) (lines 49–202):

1. **Application Base Resolution (`0x1619e4..0x161a70`):**
   - `0x161a00: ldr r0, [r6]` -> loads `argv[0]` (`"/3rd/qt/AEDK/SystemManager/SystemManager"`).
   - `0x161a14: bl #0x16ee4` -> instantiates `QFileInfo(argv[0])`.
   - `0x161a44: bl #0x17e44` -> invokes `.dir()` -> `absolutePath()` (`#0x175ec`).
   - `0x161a58: ldr r0, [pc, #0x6d8] ; *(0x162138) = 0x910aac` -> stores the resolved application directory string globally in `.bss` (`0x910aac`).
2. **`SMConfig` INI Construction (`0x16e428..0x16e4b8`):**
   - `0x16e434: bl #0x16ab8` retrieves the global application directory string (`0x910aac`), appending literal `*(0x16e8d4) -> 0x258878 ("/sm_config.ini")` via `0x18468` (`QString::append`).
   - Thus `SystemManager` **always searches for `/3rd/qt/AEDK/SystemManager/sm_config.ini`** inside the read-only `/3rd` SquashFS mount rather than `/3rd_rw`. Within `sm_config.ini`, `QSettings` queries section `[tpvlib]` for key `dynqml` (stored pointer at `0x16e8f4`).
3. **Hardcoded Resource Branch (`dynqml == 0`, `0x1db58c..0x1db620`) vs Filesystem Branch (`dynqml != 0`, `0x1db7a4..0x1db840`):**
   ```arm
     0x1db58c: bl       #0x16e958            ; query SMConfig::dynqml()
     0x1db590: cmp      r0, #0
     0x1db594: bne      #0x1db7a4            ; branch ONLY when dynqml == true!
     0x1db598: ldr      r0, [pc, #0x978]     ; *(0x1dbf18) -> 0x25e824: "qrc:/HomeScreen/HSMain.qml"
     ...
     0x1db5fc: ldr      r1, [pc, #0x918]     ; "2closeHS(int)" -> connect Qt QML signals
     0x1db61c: ldr      r1, [pc, #0x900]     ; "2launch(int)"
     ...
   ; dynqml != 0 branch:
     0x1db7ac: bl       #0x16ab8             ; base dir (/3rd/qt/AEDK/SystemManager)
     0x1db7d0: ldr      r1, [pc, #0x79c]     ; *(0x1dbf74) -> 0x25e808: "/res/HomeScreen/HSMain.qml"
     0x1db7f0: bl       #0x18468             ; QString append -> "<appDir>/res/HomeScreen/HSMain.qml"
   ```

Because `/3rd` is mounted read-only over `dm-verity` `NFSB` RSA-1024 and `/3rd/qt/AEDK/SystemManager/sm_config.ini` is absent on stock firmware, `dynqml` permanently evaluates to `0`, forcing Qt to execute its compiled-in binary `qrc:/` resource bundle and ignoring external QML modifications. Even if a researcher extracted `/3rd` on an unlocked bench board, adding `[tpvlib]\ndynqml=true` in `custom_payload/patches/sm_config.ini` is mandatory before filesystem QML loading activates.

---

## 4.2 Service Provisioning (`dtv_svc`) & NetTV Hook Architecture (`libnettv.so`)

Reverse engineering `dtv_svc` (`4,255,100` bytes) and `libnettv.so` (`2,749,744` bytes) reveals the exact factory-provided RW hook mechanism connecting read-only `/3rd` software to writable `mtd12` (`/3rd_rw/nettv`).

### 4.2.1 `dtv_svc` `sys_start.c` Boot Provisioning Guard (`0x036190..0x036320`)

Tracing [`evidence/06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt) (lines 204–305, resolved via GOT `0x411170`):

1. `0x036190`: Executes `"sh /etc/scripts/mount_3rd_rw.sh"` (`0x3316bc`), mounting `/dev/mtd12` (`0x3316dc`) onto `/3rd_rw` (`0x3316e8`).
2. `0x03628c`: Attempts to open `"/3rd_rw/upgrade/customer_version"` (`0x3316f0`).
   - If the file **exists** (`r0 >= 0` / normal television state): branches immediately to `0x0363c0` / `0x035e20`, leaving the entire contents of `/3rd_rw/nettv/` completely untouched across power cycles.
   - Only if `customer_version` is **missing** (`0x036298: cmn r0, #6`): `dtv_svc` invokes shell helper `0x34618` sequentially for:
     - `0x0362a0`: `"rm -rf /3rd_rw/nettv/opera;"` (`0x331714`)
     - `0x0362b4`: `"mkdir -p /3rd_rw/nettv/opera;"` (`0x331730`)
     - `0x0362c8`: `"cp -rf /3rd/nettv/opera/* /3rd_rw/nettv/opera;"` (`0x331750`)
     Followed by `sync()` (`0x0362dc`) and creation of `/3rd_rw/upgrade/customer_version` (`0x036300`).

### 4.2.2 `libnettv.so` `_imnettv_copydata` Native Override Pipeline (`0x1889a0..0x188d20`)

When Smart TV or Internet browser initialization runs, `libnettv.so` executes `_imnettv_copydata` (`evidence/06_systemmanager_and_nettv_disasm.txt`, lines 306–424):

| Address | Target Action / Command String | Functional Consequence |
|---|---|---|
| `0x1889c4..0x188b38` | Checks `/mnt/browser/ClientCert.bag`, `opcacrt6.dat`, `opcacrt6.pem`; copies from `/usr/opera/opera_dir/` if missing or 0-byte | Synchronizes Opera TLS X.509 CA bundle & client certs into writable browser storage |
| `0x188b4c..0x188b58` | `mkdir /tmp/opera_home` -> `cp -f /usr/opera/opera_home/* /tmp/opera_home` | Populates writable DRAM `tmpfs` profile cleanly every browser launch |
| `0x188ba8..0x188c44` | `rm -f /mnt/browser/opssl6.dat`; `cp -f /mnt/browser/op*.dat /tmp/opera_home; sync`; `cp -f /mnt/browser/op*.pem /tmp; sync`; `chmod 666 /tmp/opera_home/*` | Clears stale SSL session cache and synchronizes `opcacrt6` stores |
| `0x188c58` | Logs `"YTLB certification support, opera.ini R/W\n"` | Vendor hook designed for YouTube Leanback certification INI overrides! |
| **`0x188c74..0x188cc4`** | **`access("/3rd_rw/nettv/opera_new.ini", F_OK)` -> if `0`, executes `"cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync"` & `"chmod 666 /tmp/opera_home/opera.ini"`** | **Officially supported RW mechanism activating custom TLS, URLFilter, UserJS, and CSS inside stock Opera!** |
| `0x188d10..0x188e68` | Registers 25 runtime debug channels (`7,NETTV`, `7,BRCTL`, `1,BRPXY`, `1,DLMGR`, `1,SHELLCMD`, `1,DRMPLG`, `1,BROWSER_HBBMW`, etc.) | Enables serial trace visibility when trace masks are enabled |

Notice the extraordinary implication of `0x188c58..0x188cc4`: MediaTek and TPV explicitly coded `/3rd_rw/nettv/opera_new.ini` support directly into `libnettv.so` (`_imnettv_copydata`) so field certifications (such as YouTube certification overrides) could reconfigure Opera runtime policies purely on writable `mtd12` without modifying read-only `/3rd` (`rootfs1`).

---

## 4.3 Forensic Audit of Proprietary Runtime Engines & Obsolescence Boundaries

Inspecting binary headers, build metadata, embedded OpenSSL banners, and filesystem layouts (`extracted/rootfs1/`, `evidence/05_runtime_engines_and_busybox_audit.txt`, `evidence/06_systemmanager_and_nettv_disasm.txt`) resolves all practical questions regarding native app feasibility:

| Engine / Subsystem | Binary / Path (`rootfs1/`) | Size | Embedded Build & Library Fingerprint | Technical Reality & Obsolescence Constraint |
|---|---|---:|---|---|
| **Smart TV Browser** | `nettv/libopera_hbbtv.so` + `nettv/opera/browser.out` | `15.72 MB` + `803 KB` | `Opera/9.80 (Opera TV Store/6213)`<br/>Build `20140526_1239_jenkins_38e` (`Presto`) | Self-contained statically embedded OpenSSL supports **`TLS 1.0`, `TLS 1.1`, `TLS 1.2`** (`Enable TLS v1.1/1.2` disabled in stock `opera.ini`, unlockable via `opera_new.ini`). Hard ceiling: **No TLS 1.3**, **ES5 JS parser only**, Presto DOM/CSS layout. |
| **Netflix App** | `netflix/nrd-app/netflix` | `10.20 MB` | `20150420_194932/TPV_linux_REL_PHILIPS_2K14`<br/>`Gibbon` / `nrdp` + **`OpenSSL 1.0.0d 8 Feb 2011`** + `libplayready.so` | **Max TLS 1.0** (OpenSSL `1.0.0d` predates TLS 1.1/1.2 added in OpenSSL `1.0.1`), 2015 NRDP/ESN protocol deprecated on modern Netflix servers; dynamically coupled to `libapp_client.so` / `libmtal.so` / `libcmpb.so`. |
| **YouTube App** | `leanback/wrp_leanback` | `17.7 KB` | `stagecraft` Flash wrapper + `yt_lbl.swf` (`4,515 B`) + `yt_font.swf` (`3.8 MB`) | Discontinued Adobe Flash Lite YouTube Leanback TV SWF launcher (`2014–2015`), dead API endpoints; `Opera/Presto` H.264 `<video>` relies on `libuva.so` / `libuvabackend-{capi,mtk,tpvision}.so` + `libTrace.so`. |
| **Brazilian DTV (SBTVD)** | `ginga/` & `ginga_tbr/` | Directory | `libginga_tbr_pic.so` linked by `dtv_svc` | Broadcast Ginga NCL/Lua interactive TV middleware (`autorun.sh` line 86 `LD_LIBRARY_PATH`). |
| **Legacy Spotify & DRM** | `nettv/libspotify.so.12`, `playready/`, `widevine/`, `nettv/libMarlin.so` | `2.60 MB` (+libs) | Deprecated `libspotify` v12 C API, Marlin, ClearKey, PlayReady, Widevine Classic (`libWVStreamControlAPI.so`) | Legacy hardware-bound DRM & shut-down Spotify v12 APIs; coupled to `libmtk_hw_decrypt.so` / `libsecurestorage.so`. |
| **Chromium / Blink Porting** | *(Absent)* | N/A | GCC `4.5.1` + `glibc` + DirectFB `1.4.1` + `512 MB` unified DRAM | Modern Chromium requires Wayland/X11/Ozone, modern C++17+ GCC/GLIBC toolchain, typically >1 GB RAM, and VPU DirectFB/CMPB glue — impossible without BSP source + unlocked bootloader. |

### 4.3.1 Unlocking Hidden Capabilities Inside Stock Opera (`libopera_hbbtv.so`)

Whereas stock `extracted/rootfs1/nettv/opera/opera_home/opera.ini` (`137` lines) ships conservatively locked down (`Enable TLS v1.1=0`, `Enable TLS v1.2=0`), `libopera_hbbtv.so` explicitly compiles and parses all modern Presto configuration keys (`evidence/05_runtime_engines_and_busybox_audit.txt`, lines 5–7):
- `"Enable TLS v1.1"` & `"Enable TLS v1.2"` -> Restores compatibility with HTTPS portals requiring TLS 1.2!
- `"User JavaScript File"` (`/3rd_rw/nettv/custom/userjs`), `"Always Load User JavaScript=1"`, `"User JavaScript on HTTPS=1"` -> Loads ES5 API polyfills (`Promise`, `fetch` wrapper, `Object.assign`, `Array.from`/`includes`) and TV remote-control D-pad UX scripts without mutating signed flash!
- `"URL Filter File"` (`/3rd_rw/nettv/custom/urlfilter.ini`) & `"Local CSS File"` (`/3rd_rw/nettv/custom/user.css`) -> Blocks ad/tracking endpoints natively inside Presto's network stack prior to socket allocation, conserving scarce `512 MB` DRAM.

---

## 4.4 Post-Mortem Audit of Defects Remediated Across Project Artifacts

Prior to assembling the final deliverable and monograph archive, every concrete defect identified across earlier draft UserJS scripts, Opera filters, QML overlays, Qt configs, and shell scripts was audited, corrected, and statically verified under `custom_payload/`:

| Component | Original Defect Found | Failure Mechanism on Target TV | Verified Remediation Implemented (`custom_payload/`) |
|---|---|---|---|
| **UserJS Ad-Block CSS (`user.js`)** | Broad substring selectors `[class*="ad-"]`, `[class*="ad_"]`, `[class*="ads-"]`, `iframe[src*="ad"]` | Substring `*ad-` matches legitimate classes such as `.head-`, `.load-`, `.pad-`, `.read-`, `.upload-`, causing severe layout destruction | Narrowed strictly to explicit ad-slot containers (`.video-ads`, `.ytp-ad-module`, `.advertisement`, `#ad-banner`, `.ad_unit`, `.ad-slot`, `iframe[src*="doubleclick.net"]`) |
| **UserJS `Promise` Polyfill (`user.js`)** | `fulfill(val)` and `reject(err)` lacked idempotency state guard | Calling `resolve`/`reject` twice executes `handlers.forEach` after `handlers = null` -> fatal `TypeError` | Added `if (state !== PENDING) return;` at entry to both `fulfill` and `reject` |
| **UserJS User-Agent (`user.js`)** | Blanket unconditional `navigator.userAgent` Chrome spoofing | Breaks SmartTV / Philips NetTV / HbbTV portals probing Opera CE-HTML / TV Store headers | Wrapped spoof inside hostname exclusion check (`isTvPortal` regex preserving TV portals) |
| **Opera URL Filter (`urlfilter.ini`)** | Line 84 used `#` comment prefix and overly broad substrings (`*telemetry*`, `*anuncios*`) | Opera `urlfilter.ini` treats `;` as comment and `#` as literal pattern; broad words block legitimate articles | Converted comments cleanly to `;` and scoped exclusions to specific tracking/ad hostnames |
| **18 QML Views (`qml_HomeScreen/`)** | Non-Latin-1 emojis (`> 0xff`, absent in `Roboto-Regular.ttf` / `DroidSansFallback.ttf`), invisible default-black text on dark backgrounds, dead `127.0.0.1:8888` Python links, false `"TLS 1.3"` label | Glyphs render as missing boxes (`□`), invisible text, broken localhost sockets (no `python` on TV), inaccurate security claim | Replaced emojis with ASCII/Latin-1 (`<= 0xff`), set explicit high-contrast foreground colors, pointed bookmarks to live HTTPS endpoints, corrected label to `"TLS 1.2"` |
| **Boot Tuning Script (`run.sh`)** | Used missing binaries (`pidof`, `pgrep`, `renice`), unguarded `>> /tmp/hosts` append, and unredirected subshell FDs | Commands fail on MT5880 BusyBox; `/tmp/hosts` grows on repeated runs; subshell holds open FDs blocking caller pipe | Rewrote loop using BusyBox `ps \| awk`, guarded `/tmp/hosts` via `grep -q`, and redirected subshell `</dev/null >/dev/null 2>&1 &` |
| **Qt Dynamic QML Gate (`sm_config.ini`)** | Absent from overlay deliverables | `SystemManager` defaults to `dynqml == 0` (`qrc:/HomeScreen/HSMain.qml`) | Added `custom_payload/patches/sm_config.ini` documenting `[tpvlib]\ndynqml=true` |

All remediated artifacts pass `sh -n`, BusyBox command compliance, `node --check`, and Latin-1/brace verification (`evidence/05_runtime_engines_and_busybox_audit.txt`, lines 39–42).
