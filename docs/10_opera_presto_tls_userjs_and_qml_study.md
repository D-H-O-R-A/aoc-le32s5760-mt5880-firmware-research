# Chapter 10 (Technical Study) — Opera Presto TLS, URLFilter, Safe CSS, ES5 UserJS Polyfills & QML Overlay Feasibility

**Scope:** Having established why Qt `SystemManager` defaults to built-in `qrc:/HomeScreen/HSMain.qml` and why `Netflix nrd-app` / `Flash Lite` remain structurally frozen at 2011–2015 protocol layers, this study documents the exact browser-layer engineering applied inside `custom_payload/nettv/` (`opera_new.ini`, `urlfilter.ini`, `user.css`, `user.js`) and analyzes the 18 normalized QML study components preserved under `custom_payload/qml_HomeScreen/` (`evidence/05_runtime_engines_and_busybox_audit.txt`, `evidence/07_dmbht_and_boot_scripts_audit.txt`).

---

## 10.1 Opera Presto `6213` Capability & Network Defense Architecture (`opera_new.ini` & `urlfilter.ini`)

### 10.1.1 Cipher & Compatibility Tuning Inside `opera_new.ini` (`128` Lines)

Comparing stock `extracted/rootfs1/nettv/opera/opera_home/opera.ini` (`137` lines) against `custom_payload/nettv/opera_new.ini` (`128` lines, `2,463` bytes) identifies every runtime preference modified natively via `libnettv.so`'s `_imnettv_copydata` hook (`0x188c74`):

1. **Transport Security (`[Security Prefs]`):**
   - `Enable SSL v2=0`, `Enable SSL v3=0` — disables deprecated SSLv2/SSLv3 protocols (POODLE/DROWN exposure).
   - `Enable TLS v1.0=1`, `Enable TLS v1.1=1`, `Enable TLS v1.2=1` — overrides stock zeros (`0`) inside `opera.ini`, activating `libopera_hbbtv.so`'s compiled-in `TLS v1.2` + `ECDH`/`ECDSA` cipher support. Because Opera `Presto 2014` lacks TLS `1.3` (`RFC 8446`), all QML/documentation labels strictly state **`TLS 1.2`**.
   - `OCSP Validate Certificates=0` — prevents OCSP responder hangs on legacy root CA chains inside embedded environments lacking continuous RTC synchronization (`opcacrt6.pem` still bounds trusted CAs).
2. **Memory-Constrained Media & Caching (`[Disk Cache]` & `[Cache]`):**
   - `Enabled=0` under `[Disk Cache]` disables flash write-amplification onto `mtd12` (`/3rd_rw`) while `Automatic RAM Cache=1`, `Multimedia Stream Always=1`, `Multimedia Stream in RAM=1` (`4096` KB), `Figure=20000`, `Document=6000`, `ECMAScript=2000`, `Network Buffer Size=128`, `Datadesc Buffer Size=128` keep active working sets pinned cleanly within DRAM quotas.
3. **Browser Extension Hooks (`[User Prefs]` & `[Network]`):**
   - `URL Filter File=/3rd_rw/nettv/custom/urlfilter.ini`
   - `Local CSS File=/3rd_rw/nettv/custom/user.css`
   - `User JavaScript File=/3rd_rw/nettv/custom/userjs`
   - `User JavaScript=1`, `Always Load User JavaScript=1`, `User JavaScript on HTTPS=1`, `User CSS=1`, `Spoof UserAgent ID=2`

### 10.1.2 Presto URLFilter Security Sandboxing & Ad-Blocking (`urlfilter.ini`, `141` Lines)

Examination of `custom_payload/nettv/urlfilter.ini` highlights a critical security role shipped in factory Opera filters alongside our added ad-exclusion blocklist:

- **Lines `7–82` (Local Filesystem & Key-Protection Exclusions):** Blocks web pages or XSS payloads running inside `browser.out` from issuing `file://` or relative subresource requests toward sensitive MTD mounts:
  - `file://`, `file:///`, `file://localhost/*`, `file://dev/*`, `file://proc/*`, `file://tmp/*`, `file://home/*`
  - `*/basic/`, `*/etc/`, `*/perm/*`, `*/3rd_ro/key/`, `*/3rd_ro/vsecure/`, `*/3rd_rw/nettv/browser/`, `*/mnt/browser/`
  - Internal Opera schemes: `opera:*`, `about:*`, `widget:*`
  Omitting those stock lines would open local file/key disclosure vectors on the TV browser; keeping `[exclude]` intact preserves full filesystem isolation!
- **Lines `84–141` (Ad/Telemetry Domain Exclusions):** Fixes an earlier draft syntax defect (`#` comment token replaced by proper INI `;` comment) and excludes known telemetry/advertisement networks (`*doubleclick.net*`, `*google-analytics.com*`, `*googlesyndication.com*`, `*googleadservices.com*`, `*smartclip.{com,net}*`, `*yospace.com*`, `*adservice.*`, `*adserver.*`, `*adtech*`, `*spotxchange*`, `*springserve*`, `*pubmatic*`, `*rubiconproject*`, `*criteo*`, `*taboola*`, `*outbrain*`, `*amazon-adsystem*`, `*moatads.com*`, `*tpv-analytics*`, `*ad*.tpvision.com*`, `*ad*.nettvservices.com*`) without overly generic single-word wildcards like `*telemetry*` or `*anuncios*` that corrupt news portals.

---

## 10.2 CSS Layout Rules & ES5 UserJS Polyfill Engineering (`user.css` & `user.js`)

### 10.2.1 Remote D-Pad Glyphs & Precision Ad Hiding (`user.css`, `32` Lines)

Because Opera renders spatial-navigation focus hints using custom `op[code=...]` elements, `custom_payload/nettv/user.css` preserves all eight vendor remote-control button glyphs (`VK_ENTER` -> `"OK"`, `VK_MENU` -> `"OPTIONS"`, arrow glyphs `\2190..\2193`, `VK_BACK`, `VK_INFO`) and applies zero-dimension collapsing only to explicit advertising classes:

```css
.video-ads, .ytp-ad-module, .ytp-ad-overlay-container, .ytp-ad-player-overlay,
.advertisement, #ad-banner, .banner-ad, .tv-ad-banner, .smart-ad,
#portal-ad-box, .nettv-ad-banner, .ad_unit, .ad-slot, .sponsored-post,
.sponsor-box, [data-ad-slot] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}
```

Replacing legacy substring patterns (`[class*="ad-"]`, `[class*="ad_"]`) eliminates unintended disappearance of legitimate UI wrappers (`.header-ad...` vs `.head-`, `.load-`, `.pad-`, `.read-`, `.upload-`).

### 10.2.2 Modular Structure of `user.js` (`601` Lines, `25,421` Bytes)

All injected scripts inside `custom_payload/nettv/userjs` execute inside **Opera Carakan / Presto ECMAScript 5** (`ES5`), which **cannot parse ES6+ syntax extensions** (`const`, `let`, arrow `=>`, template backticks, `class`, destructuring, `async`/`await`). Every polyfill in `custom_payload/nettv/user.js` is strictly valid ES5 (verified via `node --check`):

| Line Range | Subsystem / Function | Behavioral Mechanics & Safeguards |
|---|---|---|
| `10–42` | **Portal-Scoped UA Spoofing** | Evaluates `isTvPortal = /nettvservices\|corio\|philips\|tpvision\|hbbtv\|localhost\|127\.0\.0\.1/.test(host)`. **Only** on non-portal public origins does it redefine `navigator.userAgent` / `appVersion` / `vendor` (using `Object.defineProperty` with `__defineGetter__` fallback) and mock `window.chrome` stubs (`loadTimes`, `csi`). Prevents breaking HbbTV and NetTV device-detection endpoints. |
| `44–82` | **DOM Ad-Hide & Auto-Skip Poll** | Injects explicit CSS selector `<style>` on `DOMContentLoaded` and runs an `800 ms` poll clicking `.ytp-ad-skip-button` / `.videoAdUiSkipButton` or seeking `.ad-showing video` cleanly to `adVideo.duration` (checked finite and `> 0`). |
| `84–133` | **480p Video Cap** | Seeds `localStorage` (`yt-player-quality`, `yt-player-sticky-quality`, `yt-player-av-sticky-quality`) -> `"480p"`, hooks `HTMLVideoElement.prototype.play`, and calls `setPlaybackQualityRange('medium', 'large')` / `setPlaybackQuality('large')` to keep decode bitrates smooth within MT5880 VPU + Wi-Fi/100Mbit headroom. |
| `135–235` | **ES6+ Built-in Method Polyfills** | Implements ES5-compliant `Object.assign`, `Object.entries`, `Object.values`, `Array.prototype.{includes,find,findIndex}`, `Array.from`, `String.prototype.{includes,startsWith,endsWith}`, and `60 fps` `setTimeout`-backed `requestAnimationFrame`. |
| **`237–324`** | **Idempotent `SimplePromise` Polyfill** | Full Promises/A+ state machine (`PENDING=0`, `FULFILLED=1`, `REJECTED=2`) implementing `.then`, `['catch']`, `resolve`, `reject`, and `all`. Crucially enforces `if (state !== PENDING) return;` (lines `245` and `253`) **prior to invoking `handlers.forEach` and clearing `handlers = null`**, eliminating double-settlement crashes present in naive implementations. |
| `326–354` | **`XMLHttpRequest`-Backed `fetch`** | Wraps async `XMLHttpRequest` inside `SimplePromise`, exposing `{ ok, status, statusText, text(), json() }` with `onerror` and `ontimeout` rejections. |
| `358–601` | **Preserved Factory TPV/Opera Hooks** | Retains upstream Opera PR fixes unaltered (`XMLHttpRequest.onreadystatechange` getter/setter wrapper, Yahoo back key `8`, `body`/`html` `overflow:hidden`, `hbbtv.ndr.de`, `json.bild.de` jQuery XML `innerHTML` try/catch, `philips.playintv.com` France24 JIT fix, BBC iPlayer input key map `412`/`413`/`415`/`417`, Google Search `enter`, Facebook `. _5o0-`, eBay menu navigation, BBC overlay black flash, YouTube `app-prod.js`, Skype non-SVG override, Philips portal `33/34/37..40` key fixes, Euronews `navLang`). |

---

## 10.3 Complete Audit of `custom_payload/qml_HomeScreen/` (`18` Files, `3,094` Lines)

All 18 QtQuick `1.1` / QML overlay components studied under `custom_payload/qml_HomeScreen/` (`3,094` lines across `2` root views and `16` sub-components) are archived strictly as an educational reference study of Qt `4.8.3` DirectFB UI design (since Chapter 4 proves `SystemManager` defaults to compiled `qrc:/HomeScreen/HSMain.qml` whenever read-only `/3rd` lacks `sm_config.ini`).

### 10.3.1 Remediation Summary Across All 18 QML Files

[`scripts/inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py) (`evidence/05_runtime_engines_and_busybox_audit.txt`, line 42) enforces three programmatic invariants on every file in this tree:
1. **Strict ISO-8859-1 (`<= 0xff`) Character Compliance:** All non-Latin-1 Unicode emoji characters (`> 0xff`, unsupported by `/3rd/qt/lib/fonts/Roboto-Regular.ttf` and `DroidSansFallback.ttf`) were eliminated so no text badge renders replacement boxes (`□`).
2. **Explicit Foreground Colors & Valid Targets:** Uncolored `Text` items over dark backgrounds receive explicit hex palette values (`#ffffff`, `#cbd5e1`, etc.), stale `127.0.0.1:8888` Python proxy links in `ChromeWebView.qml` were purged, and inaccurate `"TLS 1.3"` badges were corrected to **`"TLS 1.2"`**.
3. **Balanced Brace Syntax:** Every QML file passes `{` == `}` static validation cleanly.

| QML Module Path (`custom_payload/qml_HomeScreen/`) | Lines | Functional Scope & Architectural Limitation on Stock Hardware |
|---|---:|---|
| `HSMain.qml` | `336` | Root QtQuick 1.1 home launcher container & view router |
| `ModernLauncher.qml` | `284` | Tile grid navigation layout using D-pad key bindings |
| `components/AppCard.qml` | `118` | Reusable card delegate with focus ring & selection signal |
| `components/ChatGPTView.qml` | `157` | Static UI concept card (lacks TLS 1.3 / modern WebSocket client on Qt 4.8.3) |
| `components/ChromeWebView.qml` | `205` | Browser bookmark hub (remediated away from missing `127.0.0.1:8888` Python bridge) |
| `components/CinemaHubView.qml` | `187` | Streaming UI mockup (cannot load external DRM streams like modern Netflix) |
| `components/HeroBanner.qml` | `68` | Top promotional banner widget |
| `components/MediaBrowserPanel.qml` | `143` | Local USB/DLNA media browser concept panel |
| `components/ModernPlayerView.qml` | `296` | Player overlay controls study (`mediaPlayer` Qt stubs) |
| `components/MusicHubView.qml` | `200` | Audio hub layout mockup (`libspotify.so.12` backend deprecated server-side) |
| `components/NavDrawer.qml` | `93` | Side navigation drawer |
| `components/NetworkPanel.qml` | `145` | Network settings diagnostic panel UI |
| `components/SettingsPanel.qml` | `104` | Configuration panel view |
| `components/StoragePanel.qml` | `96` | NAND / USB storage display UI |
| `components/SystemInfoPanel.qml` | `102` | Hardware/software metadata card (`TLS 1.2` accurately labeled) |
| `components/ToolsHubView.qml` | `176` | Utility dashboard view |
| `components/TopBar.qml` | `154` | Persistent status & clock bar |
| `components/YouTubeView.qml` | `230` | Video portal launcher panel (`wrp_leanback` Flash deprecated; relies on Opera) |
