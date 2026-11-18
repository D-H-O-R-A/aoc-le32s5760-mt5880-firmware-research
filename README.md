# Early-Generation Smart TV Firmware Reverse Engineering: Cryptographic Chain of Trust, Container Analysis & Brick-Safe Study (`AOC LE32S5760/20` — `MediaTek MT5880` / `TPV MTK2K14PLF`)

[![Verification](https://img.shields.io/badge/Offline%20Verification-7%2F7%20PASS-brightgreen)](#verification-summary--epistemic-boundaries)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue)](https://github.com/D-H-O-R-A/aoc-le32s5760-mt5880-firmware-research/releases)
[![Study Scope](https://img.shields.io/badge/Scope-First%2FEarly%20Gen%20Smart%20TV%20Study-orange)](#educational-scope--generation-context)
[![Target SoC](https://img.shields.io/badge/SoC-MediaTek%20MT5880%20ARMv7--A-blue)](docs/01_architecture_hardware_and_flash_layout.md)
[![Secure Boot](https://img.shields.io/badge/Chain%20of%20Trust-RSA--2048%20%2B%20NFSB%20RSA--1024-red)](docs/02_secure_boot_chain_preloader_tz_and_nfsb.md)
[![Merkle Tree](https://img.shields.io/badge/dm--bht%20MD5-36%2C281%20Blocks%20Verified-blue)](docs/02_secure_boot_chain_preloader_tz_and_nfsb.md)
[![Safe Mod Delivery](https://img.shields.io/badge/RW%20Delivery-mtd12%20UBIFS%20(%2F3rd__rw)-success)](docs/05_mtd12_rw_delivery_and_offline_verification_thesis.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

> **Tags:** `smart-tv` · `first-gen-smart-tv` · `firmware-research` · `reverse-engineering` · `mediatek-mt5880` · `arm-assembly` · `thumb-2` · `secure-boot` · `dm-verity` · `nfsb` · `opera-presto` · `embedded-linux` · `cryptography` · `aoc-le32s5760`

---

## Educational Scope & Generation Context

This repository is an **educational and forensic firmware research monograph** dedicated to understanding how **first/early-generation Linux Smart TVs** (specifically the 2014–2016 `TPV MTK2K14PLF` / **MediaTek MT5880** generation represented by the **AOC LE32S5760/20**) were architected, cryptographically locked, and constrained at both hardware and application runtime levels.

All analysis, ARMv7/Thumb-2 disassembly traces, Merkle-tree proofs, and container parsers (`scripts/`) were created strictly for research, diagnostics, and reproducibility without distributing proprietary binaries or factory private keys.

---

## Abstract

Prompted by empirical upgrade failures observed when attempting to flash modified SquashFS images or factory PKG packages onto retail television hardware — specifically an **8-second progress stall (`...`) followed by abort dialog `"REINICIAR OU TENTAR NOVAMENTE"`** — and by engineering questions regarding modern streaming/browser compatibility (Netflix, Chromium, YouTube) on 2014–2016 CE silicon, this study reconstructs and proves the end-to-end enforcement pipeline from mask-ROM silicon up to Qt and Opera userland processes.

Across eleven chapters and appendices backed by **seven standalone Python/Shell proof scripts** (`scripts/`), we establish formal, instruction-verified explanations for every major security and execution boundary on the target platform:

1. **Silicon-to-Userspace Chain of Trust:** From BootROM through the Thumb-2 Preloader (`extracted/uboot.bin`), hardware **eFuse gate (`0xf0008664 & 0x100000`)**, software flag `[0xfb0053bc] == 1`, proprietary **HW-LZHS (`0xf00080b0`)** decompression block, dual RSA-2048 signature/certificate trailers inside `kerA`/`kerB`, down to the Linux kernel `dm-verity` **`NFSB` v2 raw RSA-1024 (`e = 3`)** block-integrity layer.
2. **`uImage` Virtual Offset Alignment & Complete Merkle-Tree Verification:** By identifying a `64`-byte `uImage` header (`magic = 0x27051956`, `load = 0x00007fc0`, `ep = 0x00008000`) at the head of decompressed `scratch/vmlinux.bin`, all kernel virtual addresses and `.rodata` string pointers align bit-for-bit (`N @ 0xc0429370`, `e = 3 @ 0xc04292f0`, `nfsb_rsa_check @ 0xc0028df8`, `dm_mount_root_nfsb @ 0xc0009594`, `populate_table_nfsb @ 0xc02243c4`). We verify both the textbook RSA-1024 equations across all four factory partitions (`3rdB`, `3rdA`, `rfsB`, `rfsA`) **and all `36,281` individual 4 KB SquashFS blocks (`23,767` in `3rdA`, `12,514` in `rfsA`)** through the two-level **`dm-bht` MD5 Merkle tree** up to the RSA-signed root digests (`666e1b26...` and `6cc5d821...`), accompanied by a direct failure counter-proof on `build/custom_upgrade_loader.pkg`.
3. **MTK/TPV DLM Container Cryptosystem (`Autorun.upg`) & Upgrade Engine Post-Mortem:** Disassembly of `libdtv_common.so` (`dlm_locate_codefile_hdr`, `x_dlm_download_by_tag`, `x_dlm_integrity_check`) and `libmtkapp.so` (`_phm_upg_model_*`, `sub_404f28`, `sub_407d4c`, `sub_4074c0`) resolves every layer of the `.upg` format: outer `128`-byte filename slot, AES-128-CBC envelope under hardcoded key `0x94102909 * 4` (`IV = 0`) yielding `#DH@FiRm`, zeroed-slot body `MD5`, non-standard `33`-byte (`\n`-inclusive) `MD5(AES_Prod.key/.iv)` derivation, `"reserved mtk inc"` chunk authenticator, per-chunk `SHA-256`, and raw PKCS#1 v1.5 RSA-2048 (`cmp r8, #0x20`). We pinpoint the exact causes of the 8-second failure: `<METHOD>PART</METHOD>` causes `sub_404f28` (`r6 == 0`) to format `"/dev/nand_10"` (returning `-22 ENOENT` from `c_fm_erase_flash_part` because the kernel only populates `/dev/mtd*`), and `_phm_upg_model_start_upgrade` (`0x40ae80..0x40ae9c`) explicitly skips dual-bank EEPROM toggling for standalone `3rdp` updates.
4. **Lock-Compliant Persistent Delivery on `mtd12` (`/3rd_rw`) & Application Stack Ceiling Audit:** We prove that `mtd12` (`ubi4:3rd_rw`) bypasses `NFSB`/`dm-verity`, trace `dtv_svc` (`sys_start.c @ 0x036190..0x036314`) preserving `/3rd_rw/nettv` whenever `/3rd_rw/upgrade/customer_version` exists, trace `libnettv.so` (`_imnettv_copydata @ 0x1889a0..0x188d10`) natively applying `/3rd_rw/nettv/opera_new.ini` (and managing `/mnt/browser/opcacrt6.pem`) onto `/tmp/opera_home/opera.ini`, verify the `19,905`-byte `<TAG>smth</TAG><METHOD>FILE</METHOD>` upgrade package, dissect `SystemManager` (`SMConfig` `dynqml` gate at `0x1db58c`), document why static `OpenSSL 1.0.0d` (Netflix 2015), Flash Lite (`yt_lbl.swf`), Presto `6213`, GCC `4.5.1` ABI, `512 MB` unified DRAM, and stripped BusyBox binaries prevent native Chromium/TLS 1.3 porting, and audit every bug remediated in `custom_payload/`.

---

## Why a Full Custom Firmware Could Not Be Safely Flashed (Cryptographic Locks & Hardware Brick Risk)

A core outcome of this study is proving **why building and flashing a modified full custom firmware (`kerA`/`kerB`, `rfsA`/`rfsB`, or `3rdA`/`3rdB`) is unfeasible on a retail AOC LE32S5760/20**:

1. **Unbreakable Transitive Signature Chain (No Vendor Private Keys):**
   - **Stage 1 (BootROM -> Preloader -> U-Boot):** Preloader checks hardware OTP eFuse `0xf0008664 & 0x100000` and software flag `[0xfb0053bc] == 1`. On signature mismatch, it prints `"not secure loader\n"` and enters an **infinite halt loop (`0xfb000520: b #0xfb000520`)**.
   - **Stage 2 (U-Boot -> Kernel `kerA`/`kerB`):** Both `kerA` and `kerB` carry dual `[256B RSA-2048 signature | 256B RSA-2048 certificate]` trailers (`0x25152c`, `0x283f2c`), blocking unsigned kernel patches that disable `dm-verity`.
   - **Stage 3 (Kernel -> `rfsA`/`B` & `3rdA`/`B`):** Even keeping the stock kernel intact fails for any custom SquashFS image because `nfsb_rsa_check` enforces raw RSA-1024 (`e=3`) equality against a 2-level `dm-bht` MD5 tree covering every 4 KB page (`Custom PKG counter-proof: RSA_exact_match=False`).
2. **Irrecoverable Brick Risk & Absence of External Hardware Chip Programmer:**
   - Because no hardware flasher / external NAND/SPI chip programmer (or hot-air BGA rework station to desolder and reprogram the raw NAND IC out-of-circuit) is available for emergency recovery, **flashing any experimental unsigned bootloader, kernel, or root partition risks permanently bricking the television mainboard**.
   - Furthermore, even dual-bank `3rdp` updates are explicitly blocked by `libmtkapp.so` (`0x40ae94`, bank toggle skipped).
   - **Constructive Resolution:** Rather than risking an unrecoverable NAND corruption on `mtd4..mtd10`, experimentation stopped cleanly at the verified cryptographic boundary (`mtd12` `/3rd_rw` UBIFS via `<TAG>smth</TAG><METHOD>FILE</METHOD>`), keeping all signed boot and read-only partitions bit-identical to factory stock.

---

## Programming, Scripting & Firmware Languages Used

| Layer | Languages & Formats | Concrete Role in Target / Research Suite |
|---|---|---|
| **Silicon & Kernel** | **ARMv7-A (ARM32) & Thumb-2 Assembly**, **C (`Linux 3.0.13`)** | BootROM/Preloader `uboot.bin`, HW-LZHS driver, `dm-verity` `nfsb_rsa_check` & `dm-bht` |
| **Core TV Middleware** | **C / C++ (`GCC 4.5.1`, `glibc`, `DirectFB 1.4.1`)** | `dtv_svc`, `libdtv_common.so` (DLM crypto), `libmtkapp.so` (UI upgrader), `libnettv.so` |
| **Smart TV UI & Apps** | **Qt 4.8.3 / QML (`QtQuick 1.1`)**, **ActionScript / SWF**, **NCL / Lua** | `SystemManager` (`qrc:/HomeScreen/HSMain.qml`), Adobe Flash Lite `stagecraft` (`yt_lbl.swf`), Brazilian `Ginga` SBTVD |
| **Browser & Web Hooks** | **ECMAScript 5 (`ES5 JS`)**, **CSS 2/3**, **INI / XML** | Opera `Presto 6213` engine, `opera_new.ini`, `urlfilter.ini`, `user.css`, ES5 `user.js`, `.upg` `<UPGRADE>` XML (`ixml`) |
| **Target Init / Shell** | **POSIX `/bin/sh` & BusyBox (`73` applets)** | `rc.local`, `rc.local.partial`, `autorun.sh`, `dmverity_mount_*`, `ubi_mount_*` |
| **Reverse-Engineering Suite** | **Python 3 (`Capstone`, `hashlib`, `struct`)**, **OpenSSL CLI**, **Node.js**, **Shell** | Automated binary parsing, RSA/AES/MD5/Merkle verification (`scripts/*.py`), JS syntax check |

---

## Highlighted Annotated Assembly Examples (Verified Primary Traces)

All snippets below are excerpted directly from our generated Capstone disassembly logs ([Appendix B](docs/09_appendix_annotated_arm_and_thumb_disassembly.md)):

### 1. Preloader eFuse Gate & Permanent Halt Trap (`uboot.bin`, Thumb-2, Base `0xfb000000`)
Checks OTP silicon eFuse (`0xf0008664` bit 20), tests SW flag (`0xfb0053bc`), calls BootROM RSA-2048 (`0xfb0034f0`), and halts forever (`0xfb000520`) on tampering ([`evidence/02_secure_boot_chain_disasm.txt`](evidence/02_secure_boot_chain_disasm.txt)):
```arm
  0xfb001450: ldr      r3, [pc, #0xec]        ; *(0xfb001540) = 0xf0008664 (MT5880 eFuse status MMIO)
  0xfb001458: ldr      r3, [r3]               ; Read fused hardware silicon flags
  0xfb00145a: tst.w    r3, #0x100000          ; Bit 20 == 1 -> Secure Boot permanently enabled in OTP
  0xfb00145e: beq      #0xfb001480
  0xfb001460: ldr      r3, [pc, #0xe0]        ; *(0xfb001544) = 0xfb0053bc (SW secure flag == 1 in stock)
  0xfb001462: ldr      r3, [r3]
  0xfb001464: cbz      r3, #0xfb001480
  ...
  0xfb001478: bl       #0xfb0034f0            ; BootROM RSA-2048 check (trailer @ +0x6c4b0)
  0xfb00147c: cmp      r0, #0
  0xfb00147e: bne      #0xfb001536            ; return 2 -> branches in caller to 0xfb00052a:
; Caller halt trap (0xfb00052a..0xfb000530):
  0xfb00052a: ldr      r0, [pc, #0x24]        ; *(0xfb000550) = 0xfb005094 ("not secure loader\n")
  0xfb00052c: bl       #0xfb0005ac            ; Print to UART console
  0xfb000530: b        #0xfb000520            ; 0xfb000520: b #0xfb000520 -> INFINITE BRICK HALT
```

### 2. Linux Kernel `nfsb_rsa_check` (`vmlinux.bin`, ARM32, Base `0xc0008000`)
Enforces raw textbook RSA-1024 (`e=3 @ 0xc04292f0`, `N @ 0xc0429370`) via full-width integer equality (`mpuint_equal`), eliminating Bleichenbacher padding truncation exploits ([`evidence/02_secure_boot_chain_disasm.txt`](evidence/02_secure_boot_chain_disasm.txt)):
```arm
  0xc0028ee0: mov      r2, #0x67              ; Digest length = 0x67 bytes (NFSB header[0x00:0x67])
  0xc0028f04: blx      r3                     ; crypto_hash_update(&desc, &sg, 0x67)
  0xc0028f38: blx      r3                     ; crypto_hash_final(&desc, sha256_32B)
  0xc0028f5c: add      r1, r8, #0x67          ; r1 = hdr + 0x67 (128-byte RSA-1024 signature S)
  0xc0028f64: bl       #0xc0189820            ; mpuint_setbytes(sig_mpi, hdr+0x67, 128)
  0xc0028f84: mov      r1, sb                 ; sb = e (128B BE 0x00^127 || 0x03)
  0xc0028f88: mov      r2, fp                 ; fp = N (1024-bit modulus @ 0xc0429370)
  0xc0028f8c: bl       #0xc0189f2c            ; out_mpi = S^3 mod N
  0xc0028fa8: bl       #0xc0189600            ; mpuint_trim(out_mpi)
  0xc0029000: bl       #0xc01897c4            ; mpuint_equal(out_mpi, sha256_mpi): checks S^3 mod N == 0^96 || SHA256!
  0xc0029004: cmp      r0, #0
  0xc0029008: movne    r4, #0                 ; Exact 1024-bit match -> 0 (PASS)
  0xc002900c: mvneq    r4, #0                 ; Mismatch -> -1 (FAIL -> dm-verity refuses mount)
```

### 3. `libmtkapp.so` `sub_404f28` & `libdtv_common.so` DLM Key Construction (`ARM32 PIC`)
Directly proves why `<METHOD>PART</METHOD>` caused the 8-second crash (`"/dev/nand_10"` `-22 ENOENT`) while reconstructing the hardcoded outer DLM AES key `0x94102909 * 4` ([`evidence/03_upg_installer_disasm.txt`](evidence/03_upg_installer_disasm.txt)):
```arm
; libmtkapp.so sub_404f28 (XML <METHOD> switch, r6 = method enum, r7 = partition idx):
  0x404f54: cmp      r6, #0
  0x404f5c: beq      #0x404fa4                ; METHOD=PART -> formats "nand_%d" => "/dev/nand_10" (NO SUCH DEV!)
  0x404f60: cmp      r6, #1
  0x404f64: beq      #0x404fd4                ; METHOD=PMTD -> indexes PMTD[r7] ("mtd0".."mtd13")
  0x404f68: cmp      r6, #2
  0x404f6c: beq      #0x404fbc                ; METHOD=PSDM -> formats "sdm%d"

; libdtv_common.so dlm_locate_codefile_hdr (outer AES-128-CBC envelope):
  0x098b64: movw     r3, #0x2909
  0x098b74: movt     r3, #0x9410              ; r3 = 0x94102909 -> little-endian bytes: 09 29 10 94
  0x098bbc: bl       #0x379d0                 ; memset(IV_mtk, 0, 16)
  0x098bd4..0x098c04: bl #0x3845c (x4)        ; K_mtk = 09291094092910940929109409291094 (decrypts #DH@FiRm)
```

### 4. `libnettv.so` `_imnettv_copydata` Native `opera_new.ini` Injection (`ARM32`, `0x188c74`)
Official factory override loading persistent Opera configs directly out of writable `mtd12` (`/3rd_rw/nettv`) ([`evidence/06_systemmanager_and_nettv_disasm.txt`](evidence/06_systemmanager_and_nettv_disasm.txt)):
```arm
  0x188c74: ldr      r0, [pc, #0x4f0]         ; "/3rd_rw/nettv/opera_new.ini"
  0x188c7c: bl       #0xa6744                 ; access("/3rd_rw/nettv/opera_new.ini", F_OK)
  0x188c80: cmp      r0, #0
  0x188c84: bne      #0x188d10                ; skip if absent
  0x188cb4: ldr      r0, [pc, #0x4b8]         ; "cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync"
  0x188cb8: bl       #0xa4cd4                 ; system()
  0x188cc0: ldr      r0, [pc, #0x4b0]         ; "chmod 666 /tmp/opera_home/opera.ini"
  0x188cc4: bl       #0xa4cd4                 ; system()
```

---

## 2014–2016 Smart TV Application Architecture, Browser Stack & User-Agent Spoofing Mechanics

Unlike Android TV or Tizen/webOS modern appliances, first/early-generation MTK2K14PLF televisions run a fragmented **hybrid C++/Qt/Flash/Opera architecture** inside `512 MB` unified DRAM over DirectFB `1.4.1`:

1. **Qt Embedded `4.8.3` Home Launcher (`SystemManager`, `9.44 MB`):**
   - Renders graphics directly over DirectFB (`libdirectfb.so`, `QWS_DISPLAY=directfb`), with no X11 or Wayland compositor.
   - Its entire QML HomeScreen (`qrc:/HomeScreen/HSMain.qml`) is compiled inside ELF `.rodata` (`6.56 MB`), selected automatically whenever read-only `/3rd/qt/AEDK/SystemManager/sm_config.ini` (`[tpvlib] dynqml=true`) is absent (`0x1db58c`).
2. **Legacy Proprietary Vertical Apps (Why Modern Apps Cannot Run):**
   - **Netflix (`nrd-app/netflix`, `10.20 MB`):** 2015 `Gibbon` engine embedding `JavaScriptCore`, `libplayready.so`, and **OpenSSL `1.0.0d` (`8 Feb 2011`)** — physically incapable of TLS 1.1/1.2/1.3 handshakes required by current streaming endpoints.
   - **YouTube (`leanback/wrp_leanback`):** Adobe **Flash Lite** `stagecraft` container executing `yt_lbl.swf` (`4.5 KB`) + `yt_font.swf` (`3.8 MB`) via retired Flash TV endpoints and system `libcurl`/`OpenSSL 1.0.0d`.
   - **Broadcast & DRM Ecosystem:** Brazilian SBTVD `Ginga-NCL` (`libginga_tbr_pic.so` linked by `dtv_svc`), deprecated `libspotify.so.12`, `PlayReady`, `Widevine Classic` (`widevine/keybox -> /3rd_rw`), `Smooth Streaming` (`SSPK`), `dialserver`, and `DLNA`.
3. **Browser Core (`Opera/9.80 Presto/6213`) & The Two-Tier User-Agent Spoofing Mechanism:**
   - Opera (`browser.out` + `15.72 MB` `libopera_hbbtv.so`, Jenkins build `20140526`) is **self-contained** (`7 DT_NEEDED` libraries, deliberately bypassing `/basic/lib/libssl.so.1.0.0`). Because OpenSSL `TLS 1.2` + `ECDH`/`ECDSA` are built directly into `libopera_hbbtv.so`, overriding `opera_new.ini` (`Enable TLS v1.1=1`, `Enable TLS v1.2=1`) unlocks TLS 1.2 without modifying read-only `/3rd`. Media playback delegates to hardware VPU decoders via `libuva.so` -> `libuvabackend-{capi,tpvision}.so` -> `libcmpb.so`.
   - **How User-Agent Spoofing ("faking Chrome") Works & Its Limits (`user.js` + `opera_new.ini`):**
     - **INI Layer (`opera_new.ini`):** Sets `Spoof UserAgent ID=2` (`Mozilla`) globally instead of stock `1` (`Opera`).
     - **JavaScript Layer (`custom_payload/nettv/user.js`):** On public websites *outside* Smart TV portal domains (checked against regex `isTvPortal = /nettvservices|corio|philips|tpvision|hbbtv|localhost|127\.0\.0\.1/` so Philips/HbbTV portals keep working), overrides `navigator.userAgent`, `appVersion`, `vendor`, and `window.chrome` stubs to present **`Chrome/108.0.0.0 ... SmartTV`** alongside ES5 runtime polyfills (`SimplePromise`, `fetch` over XHR, `Object.assign/entries/values`, `Array.prototype.includes/find`, `requestAnimationFrame`) and remote D-pad video clamping (`480p`).
     - **Hard Engine Ceiling:** User-Agent spoofing bypasses outdated server UA allowlists, but **cannot** add ECMAScript 6 syntax tokens (`const`, `let`, `=>`, `class`), WebAssembly, TLS 1.3 (`RFC 8446`), or modern EME/DRM into the frozen 2014 Presto Carakan parser.

---

## Core Research Theses & Empirical Conclusions

| Thesis ID | Hypothesis / Technical Question | Verified Conclusion | Primary Machine Proof |
|---|---|---|---|
| **T1** | Why did flashing a `97.38 MB` custom `Autorun.upg` (`<TAG>3rdp</TAG><METHOD>PART</METHOD>`) pass for ~8s on `...` and then abort with `"REINICIAR OU TENTAR NOVAMENTE"`? | `x_dlm_integrity_check` (`0x9a7d0`) verified the RSA-2048 signature and hashes in ~8s. `_phm_upg_model_start_upgrade` then called `sub_404f28` (`r6 == 0`), formatting `"/dev/nand_10"`. Because Linux exposes `/dev/mtd10` (`PMTD`), `c_fm_erase_flash_part` failed with `-22 ENOENT` (`Upgrade NG`). Additionally, `0x40ae94` (`strncmp(tag, "3rdp", 4)`) skips bank switching. | [`evidence/03_upg_installer_disasm.txt`](evidence/03_upg_installer_disasm.txt) |
| **T2** | Can a modified SquashFS (`3rdp`) or patched `upgrade_loader.pkg` (`custom_upgrade_loader.pkg`) mount on a stock kernel? | **No.** `dm_mount_root_nfsb` (`0xc0009594`) and `populate_table_nfsb` (`0xc02243c4`) enforce `nfsb_rsa_check` (`0xc0028df8`): textbook raw RSA-1024 (`e = 3`, `N @ 0xc0429370`) checking exact equality via `mpi_cmp` against `0x00^96 \|\| SHA256(hdr[0:0x67])`, guarding two-level `dm-bht` MD5 Merkle trees over all `36,281` 4 KB SquashFS blocks (`3rdA`: `23,767`, `rfsA`: `12,514`). | [`evidence/01_pkg_and_nfsb_proof.txt`](evidence/01_pkg_and_nfsb_proof.txt)<br/>[`evidence/07_dmbht_and_boot_scripts_audit.txt`](evidence/07_dmbht_and_boot_scripts_audit.txt) |
| **T3** | Can `kerA`/`kerB` or `uboot.bin` be patched over USB to disable `NFSB` without risking a hard brick? | **No.** Preloader (`0xfb001458`) checks HW eFuse `0xf0008664 & 0x100000` + SW flag `[0xfb0053bc] == 1`, invokes BootROM RSA-2048 (`0xfb0034f0`), and halts permanently (`0xfb000520` `"not secure loader"`) on mismatch; `kerA`/`kerB` append dual `[256B sig \| 256B cert]` trailers (`0x25152c`, `0x283f2c`). Without a hardware chip programmer, flashing altered boot stages risks an unrecoverable brick. | [`evidence/02_secure_boot_chain_disasm.txt`](evidence/02_secure_boot_chain_disasm.txt) |
| **T4** | Is there a cryptographically authentic, zero-brick-risk customization path on locked retail firmware? | **Yes.** `mtd12` (`ubi4:3rd_rw`, `/3rd_rw`) is outside `NFSB`/`dm-verity`. `libmtkapp.so` natively admits `<TAG>smth</TAG><METHOD>FILE</METHOD><PATH>/3rd_rw/nettv</PATH>` via `rm -rf` -> non-recursive `mkdir` -> `tar zxf` (`sub_407d4c` -> `sub_4074c0`), preserving `customer_version`, while `libnettv.so` (`_imnettv_copydata`) applies `/3rd_rw/nettv/opera_new.ini` cleanly onto `/tmp/opera_home/opera.ini`. | [`evidence/04_upg_container_crypto_proof.txt`](evidence/04_upg_container_crypto_proof.txt)<br/>[`evidence/06_systemmanager_and_nettv_disasm.txt`](evidence/06_systemmanager_and_nettv_disasm.txt) |
| **T5** | Can Netflix 2015, Chromium/TLS 1.3, modern YouTube, or Python proxies operate natively on stock `rfs`/`3rd`? | **No.** `netflix` (`20150420`) links against **OpenSSL 1.0.0d (Feb 2011)** (max TLS 1.0); YouTube `leanback` is Flash Lite (`yt_lbl.swf`); Opera is `Presto/9.80` (`20140526`, max **TLS 1.2** + ES5); `SystemManager` defaults to embedded `qrc:/HomeScreen/HSMain.qml` (`dynqml == 0`); BusyBox lacks `python`, `curl`, `pidof`, `pgrep`, `renice`, `ionice`, `chown`, `killall`, `unzip`. | [`evidence/05_runtime_engines_and_busybox_audit.txt`](evidence/05_runtime_engines_and_busybox_audit.txt)<br/>[`evidence/06_systemmanager_and_nettv_disasm.txt`](evidence/06_systemmanager_and_nettv_disasm.txt) |
| **T6** | Do all nine firmware ELFs and startup scripts align with GCC `4.5.1` / `DirectFB 1.4.1` and exhibit verifiable static hooks? | **Yes.** Full `DT_NEEDED` auditing across all 9 ELFs confirms DirectFB/CMPB/MTAL bindings, `rc.local.partial` sets `/dev/ttyMT3 115200`, `rc.local` checks EEPROM `0x2c20`/`0x2c25` ITM mode, and `autorun.sh` exports `LD_LIBRARY_PATH` (plus vendor typo `LD_RRELOAD`). | [`evidence/06_systemmanager_and_nettv_disasm.txt`](evidence/06_systemmanager_and_nettv_disasm.txt)<br/>[`evidence/07_dmbht_and_boot_scripts_audit.txt`](evidence/07_dmbht_and_boot_scripts_audit.txt) |

---

## System Trust & Delivery Architecture

```mermaid
flowchart TD
    BootROM["BootROM (Mask ROM)<br/>Root Key Hash / eFuse Check"] --> Preloader
    Preloader["Preloader @ 0xfb000000..0xfb00a040<br/>Checks eFuse 0xf0008664 & 0x100000<br/>SW flag 0xfb0053bc == 1 | HW-LZHS 0xf00080b0"] -->|RSA-2048 Verified| UBoot["U-Boot @ DRAM 0xd00000<br/>Decompressed 2,107,048 B (+ sig/cert @ +0x6c4b0)"]
    Preloader -->|Verify Failed| Halt["Infinite Halt Loop<br/>0xfb000520 ('not secure loader')"]
    UBoot -->|RSA-2048 Sig/Cert @ 0x25152c & 0x283f2c| Kernel["Linux Kernel 3.0.13 (kerA / kerB)<br/>64B uImage hdr + VA base 0xc0008000 + TZ"]
    Kernel -->|"dm_mount_root_nfsb (0xc0009594)<br/>nfsb_rsa_check (0xc0028df8) -> 12,514 x 4KB dm-bht"| RFS["/ RootFS (rfsA / rfsB @ mtd6/7)<br/>SquashFS 4.0 RO (NFSB RSA-1024 e=3 N@0xc0429370)"]
    Kernel -->|"populate_table_nfsb (0xc02243c4)<br/>'0 0 verity /dev/mtdblock9' -> 23,767 x 4KB dm-bht"| Third["/3rd Partition (3rdA / 3rdB @ mtd9/10)<br/>SquashFS 4.0 RO (NFSB RSA-1024 e=3 N@0xc0429370)"]
    Kernel -->|"No NFSB / No dm-verity<br/>ubiattach -m 12 -d 4 -> ubi4:3rd_rw"| ThirdRW["/3rd_rw (mtd12 UBIFS RW)<br/>Persistent Unverified Storage"]
    RFS --> DtvSvc["dtv_svc & libmtkapp.so<br/>UI Local Upgrade Menu"]
    DtvSvc -->|"<TAG>3rdp</TAG><METHOD>PART</METHOD>"| Fail8s["8s RSA Pass -> '/dev/nand_10'<br/>open64 = -22 ENOENT -> Upgrade NG"]
    DtvSvc -->|"<TAG>smth</TAG><METHOD>FILE</METHOD><PATH>/3rd_rw/nettv</PATH>"| SafeExtract["rm -rf /3rd_rw/nettv && mkdir<br/>tar zxf /tmp/upgrade/smth -C /3rd_rw/nettv"]
    SafeExtract --> NetTV["libnettv.so (_imnettv_copydata @ 0x188b48)<br/>cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini"]
    NetTV --> Opera["Opera/9.80 Presto 6213 (browser.out)<br/>TLS 1.1/1.2 + URLFilter + CSS + ES5 UserJS"]
```

---

## Monograph Structure (Chapters & Appendices)

Every section below cites verifiable byte offsets, virtual addresses, instruction traces, and computed digests captured in [`evidence/`](evidence/):

1. **[Chapter 1 — Hardware Architecture, `upgrade_loader.pkg` Anatomy, Flash Topology & BusyBox Audit](docs/01_architecture_hardware_and_flash_layout.md)**
   Characterization of the MT5880 / MTK2K14PLF hardware envelope, full 16-partition `upgrade_loader.pkg` offset table, `cfig` MTD partition mapping (`mtd1`–`mtd30`), startup script choreography (`rc.local`, `autorun.sh`, `dtv_svc`), `LD_LIBRARY_PATH` / `LD_RRELOAD` resolution order, and complete 73-tool BusyBox / `/sbin` / `/usr/bin` surface inventory.
2. **[Chapter 2 — Cryptographic Chain of Trust: BootROM, Preloader HW-LZHS, TrustZone, Kernel `NFSB` RSA-1024 & `dm-bht` Merkle Trees](docs/02_secure_boot_chain_preloader_tz_and_nfsb.md)**
   Disassembly and algebraic verification of the BootROM -> Preloader -> HW-LZHS -> U-Boot -> `kerA`/`kerB` RSA-2048 chain, resolution of the 64-byte `uImage` alignment (`0xc0007fc0` -> `0xc0008000`), exact ARM accessor reconstruction of the `0xe7`-byte `NFSB` v2 superblock, full `dm_mount_root_nfsb` and `populate_table_nfsb` traces, complete `36,281`-block `dm-bht` MD5 Merkle tree validation, Bleichenbacher `e = 3` resistance proof, and `custom_upgrade_loader.pkg` counter-proof.
3. **[Chapter 3 — Philips/TPV DLM `.upg` Cryptographic Format & `libmtkapp.so` State Machine Internals](docs/03_dlm_upg_cryptography_and_libmtkapp_internals.md)**
   Complete specification of the 5-layer `.upg` protocol, disassembly proof of `K_mtk = 0x94102909 * 4`, `#DH@FiRm`, zeroed-slot `BodyMD5`, 33-byte `\n`-inclusive `MD5(AES_Prod.key/.iv)` key/IV derivation, `"reserved mtk inc"` chunk markers, raw PKCS#1 v1.5 RSA-2048 (`cmp r8, #0x20`), instruction-level root-cause breakdown of the 8-second `/dev/nand_10` `-22 ENOENT` failure, and the hidden `3rdp` dual-bank EEPROM skip bug.
4. **[Chapter 4 — Application Stack Reverse Engineering: `SystemManager`, `libnettv.so`, Opera Presto, Netflix NRDP & Legacy Defect Post-Mortem](docs/04_systemmanager_qt_opera_presto_and_legacy_apps.md)**
   Disassembly of `SystemManager` (`main` `0x1619e4`, `SMConfig` `0x16e428`, `dynqml` gate `0x1db58c` vs `0x1db7a4`), `dtv_svc` `customer_version` provisioning FSM, `libnettv.so` (`_imnettv_copydata` `0x1889a0..0x188d20` handling `/mnt/browser/opcacrt6.pem` & `/3rd_rw/nettv/opera_new.ini`), binary forensics of Opera Presto `6213`, Netflix `nrd-app` (`OpenSSL 1.0.0d`), Flash Lite `leanback`, Ginga SBTVD, Spotify, PlayReady/Widevine DRM plugins, and post-mortem of remediated JS/CSS/INI/Shell/QML defects.
5. **[Chapter 5 — Lock-Compliant `/3rd_rw` (`mtd12`) Delivery Architecture & Offline Verification Thesis](docs/05_mtd12_rw_delivery_and_offline_verification_thesis.md)**
   Four formal brick-safety invariants (`I1..I4`), instruction-level trace of `METHOD=FILE` (`sub_407d4c` and `sub_4074c0`), non-recursive `mkdir` & `/ro_data/smarthome/` `busybox unzip` vs `tar zxf` gating, key-by-key delta between stock `opera.ini` and `opera_new.ini`, complete breakdown of the verified `19,905`-byte `Autorun.upg` deliverable, USB staging remediation, and strict epistemic validation table.
6. **[Chapter 6 — Reproducible Experimental Protocol, Script Reference & Hardware Research Guidelines](docs/06_reproduction_guide_and_experimental_protocol.md)**
   Reproducibility toolchain dependencies, IP/key security hygiene, complete CLI usage matrix across all seven verification/disassembly scripts + container builder, passive `/dev/ttyMT3 115200 8N1` UART and eFuse `0xf0008664` diagnostic guidelines, and formal glossary.
7. **[Chapter 7 — ELF32 Dynamic Linking Topology, Memory Segment Maps & Startup Script Forensics](docs/07_elf_abi_memory_maps_and_startup_scripts.md)**
   Full section/program header and `DT_NEEDED` dynamic dependency analysis across all 9 core ELFs, forensic walkthrough of `rc.local.partial`, `rc.local` (EEPROM `0x2c20`/`0x2c25` ITM checks and boot flags), `dmverity_mount_3rda/b.sh`, `ubi_mount_3rd_rw/perm/ro_data.sh`, and `autorun.sh`.
8. **[Appendix A — Verified Cryptographic, Binary, `dm-bht` & Configuration Evidence](docs/08_appendix_verified_cryptographic_and_binary_evidence.md)**
   Complete annotated reproduction and cross-reference of primary machine outputs from `01_pkg_and_nfsb_proof.txt`, `04_upg_container_crypto_proof.txt`, `05_runtime_engines_and_busybox_audit.txt`, `07_dmbht_and_boot_scripts_audit.txt`, `urlfilter.ini`, `user.css`, `opera_new.ini`, and `leanback/config.ini`.
9. **[Appendix B — Annotated ARMv7 / Thumb-2 Primary-Source Instruction Reference](docs/09_appendix_annotated_arm_and_thumb_disassembly.md)**
   Structured, column-annotated instruction listings from `02_secure_boot_chain_disasm.txt`, `03_upg_installer_disasm.txt`, and `06_systemmanager_and_nettv_disasm.txt` linking register transfers, GOT/PC-relative literal pools, and control-flow decisions back to Chapters 2–5.
10. **[Chapter 10 (Technical Study) — Opera Presto TLS, URLFilter, Safe CSS, ES5 UserJS Polyfills & QML Overlay Feasibility](docs/10_opera_presto_tls_userjs_and_qml_study.md)**
    Exact engineering specification of `opera_new.ini` ciphers, Presto security URLFilter paths vs ad exclusions, `op[code=...]` remote CSS rules, idempotent ES5 `SimplePromise` / `fetch` / portal-scoped UA shims (`user.js`, `601` lines), and Latin-1 / brace / font audit across all 18 `qml_HomeScreen` study views.
11. **[Chapter 11 — Legacy Streaming, Hardware DRM Modules & Read-Only/Read-Write RootFS Bridging](docs/11_legacy_streaming_drm_and_rootfs_subsystems.md)**
    Analysis of MediaTek's factory `3rd_rw_list.txt` symlink architecture (`netflix`, `widevine/keybox`), Flash Lite `stagecraft` (`wrp_leanback`, `config.ini`, `yt_lbl.swf`), `PlayReady`, `Smooth Streaming SSPK`, `MPEG-DASH`, `dialserver`, `dlna`, and Brazilian `Ginga` SBTVD integration.

---

## Repository Directory Map

```text
.
├── README.md
├── LICENSE
├── .gitignore                                          # Excludes *.pem, *.key, *.iv, *.pkg, *.upg, *.bin, *.squashfs, extracted/
├── docs/                                               # Monograph chapters & annotated technical appendices (3,000+ lines)
│   ├── 01_architecture_hardware_and_flash_layout.md
│   ├── 02_secure_boot_chain_preloader_tz_and_nfsb.md
│   ├── 03_dlm_upg_cryptography_and_libmtkapp_internals.md
│   ├── 04_systemmanager_qt_opera_presto_and_legacy_apps.md
│   ├── 05_mtd12_rw_delivery_and_offline_verification_thesis.md
│   ├── 06_reproduction_guide_and_experimental_protocol.md
│   ├── 07_elf_abi_memory_maps_and_startup_scripts.md
│   ├── 08_appendix_verified_cryptographic_and_binary_evidence.md
│   ├── 09_appendix_annotated_arm_and_thumb_disassembly.md
│   ├── 10_opera_presto_tls_userjs_and_qml_study.md
│   └── 11_legacy_streaming_drm_and_rootfs_subsystems.md
├── scripts/                                            # Executed proof, verification, ELF/disasm & container tools
│   ├── inspect_pkg_and_nfsb.py                         # Verifies PKG partitions, cfig, kerA/B trailers & raw RSA-1024 NFSB
│   ├── disasm_secure_boot_chain.py                     # Disassembles Preloader (Thumb) & vmlinux NFSB (ARM @ VA 0xc0008000)
│   ├── disasm_upg_installer.py                         # Disassembles libmtkapp.so & libdtv_common.so DLM internals
│   ├── verify_upg_container.py                         # Offline verifier for TPV Autorun.upg containers (public key only)
│   ├── inspect_runtime_engines.py                      # Audits ELF strings, BusyBox applets, SystemManager, sh/JS/QML
│   ├── disasm_systemmanager_and_nettv.py               # ELF32 DT_NEEDED audit + SystemManager/dtv_svc/libnettv disasm
│   ├── inspect_dmbht_and_boot_scripts.py               # Verifies 36,281 dm-bht MD5 blocks, boot scripts & opera.ini diff
│   ├── build_safe_rw_upg.py                            # Sanitized RW builder (CLI keys only; zero bundled secrets)
│   └── run_all_proofs.sh                               # Deterministic 7-stage pipeline -> evidence/*.txt
├── evidence/                                           # Real captured stdout from executing scripts/
│   ├── 01_pkg_and_nfsb_proof.txt
│   ├── 02_secure_boot_chain_disasm.txt
│   ├── 03_upg_installer_disasm.txt
│   ├── 04_upg_container_crypto_proof.txt
│   ├── 05_runtime_engines_and_busybox_audit.txt
│   ├── 06_systemmanager_and_nettv_disasm.txt
│   └── 07_dmbht_and_boot_scripts_audit.txt
└── custom_payload/                                     # Remediated config, JS/CSS/URLFilter, shell, SMConfig & QML study files
    ├── nettv/
    │   ├── opera_new.ini
    │   ├── urlfilter.ini
    │   ├── user.css
    │   └── user.js
    ├── patches/
    │   ├── run.sh
    │   └── sm_config.ini
    └── qml_HomeScreen/                                 # 18 Latin-1/ASCII-normalized study QML overlays (non-persistent without RO sm_config)
```

---

## Reproducing Proofs Against Local Extracted Firmware

Given a legally obtained local workspace `<WORKSPACE_DIR>` holding stock `extracted/upgrade_loader.pkg`, `extracted/uboot.bin`, `scratch/vmlinux.bin`, `extracted/appfs1/`, `extracted/rootfs1/`, `extracted/ro_data_keys/` (public PEM + TV `/ro_data/key` files), and `build/Autorun.upg`:

```sh
./scripts/run_all_proofs.sh <WORKSPACE_DIR>
```

All scripts emit deterministic verification logs into [`evidence/`](evidence/). **No proprietary factory firmware binaries, SquashFS dumps, or private signing keys are committed to or redistributed by this repository.**

---

## Verification Summary & Epistemic Boundaries

- **Mathematically & Statically Verified (`7/7 PASS`):**
  - Stock `upgrade_loader.pkg` all 16 partition boundaries (`323,840,461` bytes), `cfig` MTD table, and `kerA`/`kerB` RSA trailers ([`evidence/01_pkg_and_nfsb_proof.txt`](evidence/01_pkg_and_nfsb_proof.txt)).
  - Raw RSA-1024 (`e = 3 @ 0xc04292f0`, `N @ 0xc0429370`) exact equality check across `3rdB`, `3rdA`, `rfsB`, `rfsA`, plus counter-proof rejecting `custom_upgrade_loader.pkg` ([`evidence/01_pkg_and_nfsb_proof.txt`](evidence/01_pkg_and_nfsb_proof.txt)).
  - End-to-end two-level `dm-bht` MD5 Merkle tree validation across all `23,767` blocks of `3rdA` (`97,349,632` B) and all `12,514` blocks of `rfsA` (`51,257,344` B), matching the RSA-signed root digests ([`evidence/07_dmbht_and_boot_scripts_audit.txt`](evidence/07_dmbht_and_boot_scripts_audit.txt)).
  - Complete Preloader, Kernel `NFSB`, `libdtv_common.so`, `libmtkapp.so`, `SystemManager`, `dtv_svc`, and `libnettv.so` ARM/Thumb instruction traces ([`evidence/02_secure_boot_chain_disasm.txt`](evidence/02_secure_boot_chain_disasm.txt), [`03`](evidence/03_upg_installer_disasm.txt), [`06`](evidence/06_systemmanager_and_nettv_disasm.txt)).
  - Cryptographic and structural verification of the `19,905`-byte safe `Autorun.upg` deliverable (`RSA-2048 PKCS#1 v1.5`, `#DH@FiRm`, zeroed-slot `MD5`, per-chunk `SHA-256`, XML manifest, GNU `tar` payload) ([`evidence/04_upg_container_crypto_proof.txt`](evidence/04_upg_container_crypto_proof.txt)).
  - Syntax, BusyBox, ELF32 `DT_NEEDED`, startup script, `opera.ini` delta, `node --check`, and Latin-1/QML validations ([`evidence/05_runtime_engines_and_busybox_audit.txt`](evidence/05_runtime_engines_and_busybox_audit.txt), [`06`](evidence/06_systemmanager_and_nettv_disasm.txt), [`07`](evidence/07_dmbht_and_boot_scripts_audit.txt)).
- **Not Executed Inside Offline Analysis Environment:**
  - Live execution on physical AOC LE32S5760/20 silicon or QEMU ARM/DirectFB hardware emulation (`qemu-arm` and proprietary MediaTek/DirectFB kernel modules are absent in the offline workspace). Runtime behavior beyond static binary verification — such as live on-screen USB flash completion or live SoC eFuse state — requires controlled physical bench verification as outlined in [Chapter 6](docs/06_reproduction_guide_and_experimental_protocol.md).

---

## Extended Multidisciplinary Research Monograph Index (`v2.0.0`)

Beyond the foundational chapters ([`docs/01..11`](docs/01_architecture_hardware_and_flash_layout.md)) and primary proof scripts ([`scripts/`](scripts/)), the repository expands into specialized, auditable engineering directories:

| Research Domain | Key Deliverables | Highlights |
|---|---|---|
| **Hardware & Silicon** | [`hardware/`](hardware/HARDWARE_ARCHITECTURE.md) · [`HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/`](hardware/HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md) | `MT5880` SoC, `T8032` standby MCU, Dual-Ch DDR, `10` NAND IDs, explicit unverified PCB gap (`715G7904M`) |
| **Firmware Forensics** | [`firmware-forensics/`](firmware-forensics/FIRMWARE_FORENSIC_ANALYSIS.md) | `FIRMWARE_HASH_MANIFEST.txt`, `FIRMWARE_METADATA.json`, `47`-binary CSV, `PKG`/`NFSB`/`uImage`/`.upg` specs |
| **Boot & Recovery** | [`boot-analysis/`](boot-analysis/BOOT_CHAIN_ANALYSIS.md) | Mask BootROM -> Thumb-2 Preloader -> `kerA/B` -> `dm_mount_root_nfsb` -> `SystemManager` sequence |
| **Kernel Reverse Eng.** | [`kernel-analysis/`](kernel-analysis/KERNEL_DEEP_ANALYSIS.md) | `Linux 3.0.13` (`381` source paths, `8` `dtv_driver.ko` paths, `12` `.ko` `.modinfo`), mainline diff analysis |
| **Filesystems & Storage** | [`filesystem/`](filesystem/FILESYSTEM_ARCHITECTURE.md) | Full `4,004`-entry inventory (`appfs1` + `rootfs1`), `mtd0..mtd30` `cfig` table, `/perm` & `/3rd_rw` UBIFS persistence |
| **Security & Cryptography** | [`security/`](security/SECURITY_ASSESSMENT.md) | `SEC-01`–`SEC-09` structured findings, Bleichenbacher `e=3` immunity proof, `SEC-02` `roda` key leak, `12`-control CSV |
| **Update Mechanism** | [`update-analysis/`](update-analysis/FIRMWARE_UPDATE_SECURITY.md) | `#DH@FiRm` DLM wrapper, `sub_404f28` `"/dev/nand_10"` `-22 ENOENT` bug, `3rdp` failover skip, anti-rollback limits |
| **Privacy & Telemetry** | [`privacy/`](privacy/NETWORK_COMMUNICATION_ANALYSIS.md) | `291` static URLs cataloged, `DIAL`/`DLNA`/`OPCACRT6` CA audit (`57/186` expired <`2026`), uncaptured-pcap boundaries |
| **Comparative Diffing** | [`comparative-analysis/`](comparative-analysis/FIRMWARE_BINARY_DIFF_ANALYSIS.md) | A/B mirror SHA-256 parity (`ker`/`rfs`/`3rd`), stock vs `custom_upgrade_loader.pkg`, `21+4` staging delta |
| **Emulation & Validation** | [`emulation/`](emulation/EMULATION_RESEARCH.md) | MMIO/`dtv_driver.ko` re-hosting barriers, non-simulated QEMU blueprint, experimental cryptographic ledger |
| **Supply Chain & SBOM** | [`sbom/`](sbom/THIRD_PARTY_COMPONENTS.md) | Valid `SPDX-2.3` (`27` pkgs) & `CycloneDX 1.5` (`26` comps) JSONs, `LD_LIBRARY_PATH` map, legacy CVEs, GPL audit |
| **Scientific Publication** | [`scientific-research/`](scientific-research/RESEARCH_PAPER.md) | Publication monograph, [BibTeX](scientific-research/REFERENCES.bib), Costin/Firmadyne/Wright/NIST/OWASP literature synthesis |
| **Vector Diagrams** | [`diagrams/`](diagrams/BOOT_CHAIN.svg) | 7 standalone architectural SVGs (`HARDWARE`, `BOOT`, `FIRMWARE`, `DEPENDENCIES`, `NETWORK`, `UPDATE`, `THREAT_MODEL`) |
| **Tests, CI & Governance** | [`tests/`](tests/test_research_suite.py) · [`.github/workflows/`](.github/workflows/firmware-analysis.yml) | Automated ephemeral `.upg` CI test suite, [ETHICAL_RESEARCH.md](ETHICAL_RESEARCH.md), [RESPONSIBLE_DISCLOSURE.md](RESPONSIBLE_DISCLOSURE.md) |
