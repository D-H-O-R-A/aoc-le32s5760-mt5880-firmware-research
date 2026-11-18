# Laboratory Patch & Custom Payload Audit (`custom_payload/` vs. Stock `rootfs1`)

> **Detailed Audit Evidence:** [docs/10_opera_presto_tls_userjs_and_qml_study.md](../docs/10_opera_presto_tls_userjs_and_qml_study.md) | [evidence/05_runtime_engines_and_busybox_audit.txt](../evidence/05_runtime_engines_and_busybox_audit.txt)

## 1. Quantified Delta (`comparison_metrics.json`)

| Scope | File Count | Byte Change / SHA-256 Tracking |
|---|---|---|
| **Added Custom UI & Config Files** | `21` files (`custom_payload/*`) | `run.sh` (`3,281` B), `sm_config.ini` (`33` B), `opera_new.ini` (`2,463` B), `user.css` (`775` B), `ModernLauncher.qml` + `16` QML components |
| **Modified Stock Config / UI Files** | `4` files (`staging_rootfs` vs `rootfs1`) | `user.js` (`10,771` -> `25,421` B), `opera.ini` (`2,565` B tuned), `urlfilter.ini` (`977` -> `1,906` B), `HSMain.qml` (`32,380` -> `12,038` B) |

---

## 2. Engineering Audit of Remediated Custom Patch Bugs

Iterative static and runtime auditing identified and corrected concrete platform compatibility flaws across `custom_payload/`:

1. **ES5 vs. ES6+ JavaScript Trap (`Opera Presto 6213`):**
   Initial web polyfills/UI hooks utilizing `let`/`const`, arrow functions `=>`, or template literals fail silently on Presto `6213`. `custom_payload/nettv/user.js` was refactored strictly to valid ES5 (`var`, `function ()`, `try/catch` feature guards) and verified syntactically via Node.js in `evidence/05`.
2. **Stripped BusyBox Binary Calls in `run.sh`:**
   Earlier prototype patches invoked flags/applets missing from the stripped `73`-applet `BusyBox v1.15.3` (`appfs1/bin/busybox`). `custom_payload/patches/run.sh` is audited exclusively against verified shipped binaries under `/bin` and `/3rd`.
3. **QtQuick 1.1 (`Qt 4.8.3`) QML Compatibility:**
   `HSMain.qml`, `ModernLauncher.qml`, and `components/*.qml` target `import QtQuick 1.1` semantics without Qt5/Qt6 WebEngine dependencies, paired with `sm_config.ini` (`dynqml`) validated in `SystemManager` (`0x1db58c`).
4. **Why Custom Browser Configs Still Hit Hardware TLS Ceilings:**
   Even with hardened `opera_new.ini` User-Agent overrides, ad/tracker blocking (`urlfilter.ini`), and DOM helpers (`user.js`), **no config patch inside `/3rd_rw` can add TLS 1.2/1.3 or modern codec support (`VP9`/`H.265`)** into `OpenSSL 1.0.0d` / Presto `6213` without replacing compiled binaries — which remains blocked from full replacement unless accepting immutable-partition signature enforcement limits.
