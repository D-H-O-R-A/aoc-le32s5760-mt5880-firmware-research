# Chapter 5 — Lock-Compliant `/3rd_rw` (`mtd12`) Delivery Architecture & Offline Verification Thesis

**Scope:** Having proved mathematically and via machine disassembly that fused boot stages (BootROM/Preloader RSA-2048) and Linux `dm-verity` (`NFSB` RSA-1024 + two-level `dm-bht` MD5) prohibit flashing modified SquashFS partitions (`3rdp`, `rfs`) via USB on retail stock TVs, this chapter formalizes and verifies the **lock-compliant persistent customization model** targeting unverified writable UBIFS partition `mtd12` (`/3rd_rw/nettv`) via `<TAG>smth</TAG><METHOD>FILE</METHOD>`. We verify every instruction in `libmtkapp.so`'s `FILE` extractor (`sub_406934`, `sub_406a30`, `sub_407d4c`, `sub_4074c0`), document the invariant preserving `/3rd_rw/upgrade/customer_version`, examine every byte of the `19,905`-byte `Autorun.upg` deliverable (`evidence/04_upg_container_crypto_proof.txt`), and delineate strict verification boundaries.

---

## 5.1 Design Objective: Four Non-Negotiable Brick-Safety Invariants

A defensible firmware delivery methodology on cryptographically locked consumer silicon must satisfy four formal invariants simultaneously:

1. **Invariant I1 (Bit-Identical Conservation of Authenticated Boot & RO Code):** Partition images `load`, `uenv`, `kerA`/`kerB`, `rfsA`/`rfsB`, `3rdA`/`3rdB`, `perm`, `roda`, and dual-bank EEPROM bank pointers remain byte-for-byte unaltered. Power loss or corrupted USB transfers during installation cannot impair bootloader initialization, TrustZone verification, or root SquashFS mounting.
2. **Invariant I2 (Full Upstream DLM Cryptographic Compliance):** Every delivered `Autorun.upg` satisfies all five integrity layers enforced inside `libdtv_common.so`: outer `0x70`-byte `#DH@FiRm` envelope (`K_mtk = 0x94102909 * 4`), zeroed-slot body `MD5`, `33`-byte `MD5(AES_Prod.key/.iv)` `"reserved mtk inc"` chunk authenticator, chunk `SHA-256` digests, and valid `TPV_MTK2K14PLF_LT0_UPG_PubKey_Prod.pem` RSA-2048 signature (`cmp r8, #0x20`).
3. **Invariant I3 (Safe Non-Destructive BusyBox Extraction):** Every shell operation synthesized by `libmtkapp.so` (`rm -rf`, `mkdir`, `tar zxf`) must invoke executables verified present in `extracted/appfs1/bin` (`evidence/05_runtime_engines_and_busybox_audit.txt`), avoid triggering the missing `busybox unzip` branch, satisfy `libmtkapp.so`'s non-recursive `mkdir` parent requirement, and never erase `/3rd_rw/upgrade/customer_version`.
4. **Invariant I4 (Verified Stock Consumer Hook):** Deployed configuration artifacts in `/3rd_rw/nettv` are ingested natively by an already-verified stock library path (`libnettv.so`'s `/3rd_rw/nettv/opera_new.ini` loader at `0x188c74..0x188cc4`) without requiring unsigned native binary execution.

---

## 5.2 Control-Flow Proof of `METHOD=FILE` (`sub_407d4c` & `sub_4074c0`)

Disassembly of `extracted/appfs1/basic/libmtkapp.so` (`evidence/03_upg_installer_disasm.txt`, lines 106–140) traces the exact runtime execution path invoked when the TV upgrader ingests `<TAG>smth</TAG><METHOD>FILE</METHOD><PATH>/3rd_rw/nettv</PATH><FILE_NAME>smth</FILE_NAME>`:

### 5.2.1 Tag Whitelist Admission (`sub_406934` / `0x407e08..0x4080dc`)

Inside `_phm_upg_model_acquire_matched_items` and helper `sub_407d4c`, `METHOD=FILE` items are matched against a strict internal tag whitelist containing `"demo"` (`0x5aede0`), `"logo"` (`0x567368`), `"keys"` (`0x5aede8` -> `%s/drmkey`), `"smth"` (`0x5aedf8`), `"edfu"`, and `"xtvk"`:

```text
0x4080a4: ldr r1, [pc, #0x624]  -> "demo"
0x4080c0: ldr r1, [pc, #0x60c]  -> "logo"
0x4080dc: ldr r1, [pc, #0x5f4]  -> "smth"
```

When `<TAG>smth</TAG>` matches, `libmtkapp.so` routes chunk extraction identically to UI SmartHome/NetTV packages. Because `c_dlm_download_by_tag` streams payload `smth` into `/tmp/upgrade/smth` (`0x407e80` `"tmp/upgrade"`, `tmpfs` DRAM), minimizing the gzipped archive to `18,817` bytes prevents DRAM starvation on the `512 MB` SoC.

### 5.2.2 Destination Cleanup, Non-Recursive `mkdir`, and Cleanup Trace (`sub_407d4c`)

Resolved PC/GOT string pointers between `0x407db8` and `0x40815c` (`evidence/03_upg_installer_disasm.txt`, lines 115–140) expose every shell operation executed via `sub_407488`:

```text
1. [0x407db8] "rm -rf %s"          -> system("rm -rf /3rd_rw/nettv")
2. [0x40815c] "mkdir %s"           -> system("mkdir /3rd_rw/nettv")
3. [0x40806c] sub_4074c0("/tmp/upgrade/smth", "/3rd_rw/nettv")
4. [0x408078] sub_405bd8           -> Unlinks staging file "/tmp/upgrade/smth"
```

Two subtle constraints proved directly by these instructions justify our exact XML `<PATH>`:
- **Constraint C1 — Non-Recursive `mkdir /3rd_rw/nettv` (`0x40815c`):** `sub_407d4c` invokes `"mkdir %s"`, **never `"mkdir -p %s"`**. If a custom `<PATH>` pointed to an uncreated two-level subdirectory (e.g., `/3rd_rw/nettv/custom`), `mkdir /3rd_rw/nettv/custom` would immediately fail with `ENOENT` right after `rm -rf` or when missing parent directories. Choosing `<PATH>/3rd_rw/nettv</PATH>` guarantees parent `/3rd_rw` is already mounted on `ubi4:3rd_rw` (`mtd12`) by `dtv_svc` (`0x036190`).
- **Constraint C2 — Isolation From `/3rd_rw/upgrade/customer_version`:** Because `rm -rf` operates strictly on `/3rd_rw/nettv`, `/3rd_rw/upgrade/customer_version` remains completely undisturbed. On subsequent cold boots, `dtv_svc` (`0x03628c`) finds `customer_version` present and skips wiping `/3rd_rw/nettv/opera`.
- **Constraint C3 — Preserving Browser Directories & Stock UserJS Helpers:** Because `rm -rf /3rd_rw/nettv` recreates a clean `/3rd_rw/nettv`, our packaged archive explicitly restores empty directories `browser/`, `download/`, `custom/`, `custom/userjs/`, and preserves **all six stock Opera UserJS helpers** (`google.js`, `iplayer_rider4-45.js`, `legacyKeyHandling.js`, `load.js`, `ooif.js`, `spatnav_youtube.js`) unmodified from `extracted/rootfs1/`.

### 5.2.3 `tar zxf` vs `busybox unzip` Prefix Gate (`sub_4074c0`, `0x4074f8..0x4075b0`)

Inside `sub_4074c0` (`evidence/03_upg_installer_disasm.txt`, lines 106–113), the decompressor chooses between `tar zxf` and `busybox unzip` via an exact 19-byte prefix check:

```arm
  0x407504: ldr      r1, [pc, #0xa4]      ; 0x5af0c0: "/ro_data/smarthome/" (19 bytes = 0x13)
  0x407508: mov      r0, r5               ; destination <PATH> ("/3rd_rw/nettv")
  0x40750c: mov      r2, #0x13
  0x407518: bl       #0xfcef4             ; strncmp(<PATH>, "/ro_data/smarthome/", 19)
  0x40751c: cmp      r0, #0
  0x407520: beq      #0x407590            ; ONLY if equal -> "busybox unzip -oq %s -d %s" (FAILS: unzip absent!)
  0x407524: ldr      r1, [pc, #0x88]      ; ELSE -> "tar zxf %s -C %s 2>/dev/null" (SUCCEEDS: tar present!)
```

Because `extracted/appfs1/bin` contains GNU/BusyBox `tar` and `gzip` while **omitting `unzip`** (`evidence/05_runtime_engines_and_busybox_audit.txt`, line 27), routing `<PATH>/3rd_rw/nettv</PATH>` cleanly bypasses the broken `unzip` branch (`0x407590`) and executes the valid `54`-byte command:

```sh
tar zxf /tmp/upgrade/smth -C /3rd_rw/nettv 2>/dev/null
```

---

## 5.3 Cryptographic Verification of `build/Autorun.upg` (`19,905` Bytes)

Running [`scripts/verify_upg_container.py`](../scripts/verify_upg_container.py) against the built `build/Autorun.upg` (`19,905` bytes, `SHA-256: 28f17bcbae25d68db64f2cc67b32c82c6cff73037bc0555a08ca395010e6956c`) confirms every cryptographic and archival requirement offline (`evidence/04_upg_container_crypto_proof.txt`, lines 1–44):

```text
File: /home/diegooris/tv-firmware-custom/AOC/LE32S5760/build/Autorun.upg (19905 bytes)
  Outer 128B prefix: 'Autorun.upg'
  [PASS] RSA-2048 PKCS#1 v1.5 signature matches SHA256(data[0x80:-256]) = d425f0dc6da71abc9a43a052ddccec23d6f2992423b7b23a506aa032c57a52a4
  [PASS] DLM Header AES-128-CBC (09291094*4): vendor='TPV', magic=b'#DH@FiRm', id='IDTV0801_002224_9_001_23_001_225', model='LE32S5760/20', body_len=19521, flags=0x0
  [PASS] Body MD5 matches MD5(enc_hdr + 0x00*32 + chunks) = b0b05a0e5385873caf37542dcd150775
  [PASS] Chunk 'ixml': flags=0, len=440, magic='reserved mtk inc', sha256=19ebca2599852ad9700ce01d98536734519c0a93bed467ca62cbaf8bf25d6fb7
  [PASS] Chunk 'smth': flags=0, len=18817, magic='reserved mtk inc', sha256=52c7f99fa479c3c81dc6c38b930d72651c3bf1bc9488078cbb0f50af6976a806
```

### 5.3.1 Configuration Diff Applied Inside Opera (`opera.ini` -> `opera_new.ini`)

Inspecting `evidence/07_dmbht_and_boot_scripts_audit.txt` (lines 240–246) shows the exact six-setting configuration override delivered by `opera_new.ini` (`2,463` bytes):

| INI Section & Key | Stock `opera.ini` (`/usr/opera/opera_home/opera.ini`) | Custom `opera_new.ini` (`/3rd_rw/nettv/opera_new.ini`) | Engineering Effect Inside Opera Presto `6213` |
|---|---|---|---|
| `[Security Prefs] Enable TLS v1.1` | `'0'` | **`'1'`** | Enables TLS 1.1 handshake fallback |
| `[Security Prefs] Enable TLS v1.2` | `'0'` | **`'1'`** | Enables TLS 1.2 + ECDH/ECDSA modern HTTPS compatibility |
| `[Network] URL Filter File` | `'$OPERA_HOME/urlfilter.ini'` | **`'/3rd_rw/nettv/custom/urlfilter.ini'`** | Blocks telemetry/ad domains prior to TCP allocation |
| `[User Prefs] Local CSS File` | `'$OPERA_DIR/styles/user.css'` | **`'/3rd_rw/nettv/custom/user.css'`** | Injects TV-safe ad-slot CSS rules without `*ad-` false positives |
| `[User Prefs] User JavaScript File` | `'$OPERA_DIR/userjs'` | **`'/3rd_rw/nettv/custom/userjs'`** | Loads 6 stock TV helpers + remediated ES5 `user.js` (`25,421` B) |
| `[User Agent] Spoof UserAgent ID` | `'1'` (Opera) | **`'2'`** (Mozilla) | Improves compatibility with server-side UA sniffers while preserving Portal headers via JS |

---

## 5.4 USB Staging Media Hygiene & Factory Recovery Remediation

Auditing physical USB deployment media (`/media/diegooris/AOC_TV_USB`) uncovered and remediated two high-risk legacy staging hazards:
1. **Removed Stale `97.38 MB` `PART/3rdp` `.upg` Files:** Both root `Autorun.upg` and legacy `upgrades/` `.upg` bundles triggering the 8-second `/dev/nand_10` failure were removed and replaced cleanly with the verified `19,905`-byte `smth` image (`28f17bcbae...`).
2. **Purged Hazardous Root `/upgrade_loader.pkg` (`323,840,461` B, `69384280...`):** Root `/upgrade_loader.pkg` on the USB stick was bit-identical to `build/custom_upgrade_loader.pkg`, whose `3rdA` partition fails `nfsb_rsa_check` (Chapter 2). Removing it from root prevents accidental cold-boot recovery flash of an unmountable `/3rd`, while preserving genuine factory stock `recovery_original/upgrade_loader.pkg` (`SHA-256: 219de76d...`) safely in backup storage.

---

## 5.5 Strict Epistemic Scope Boundaries

| Verification Layer | Status | Scope & Machine Evidence |
|---|---|---|
| PKG partition bounds, `cfig`, `kerA`/`kerB` RSA trailers & `NFSB` RSA-1024 math | **Verified (`PASS`)** | [`evidence/01_pkg_and_nfsb_proof.txt`](../evidence/01_pkg_and_nfsb_proof.txt) |
| Full 2-level `dm-bht` MD5 Merkle tree across `36,281` blocks (`3rdA` + `rfsA`) | **Verified (`PASS`)** | [`evidence/07_dmbht_and_boot_scripts_audit.txt`](../evidence/07_dmbht_and_boot_scripts_audit.txt) |
| BootROM/Preloader HW-LZHS, Kernel `NFSB`, `libmtkapp`, `libdtv_common`, `SystemManager`, `dtv_svc`, `libnettv` disassembly | **Verified (`PASS`)** | [`evidence/02_secure_boot_chain_disasm.txt`](../evidence/02_secure_boot_chain_disasm.txt), [`03`](../evidence/03_upg_installer_disasm.txt), [`06`](../evidence/06_systemmanager_and_nettv_disasm.txt) |
| `Autorun.upg` (`19,905` B) RSA-2048, AES-128-CBC, MD5, SHA-256, XML & GNU `tar` verification | **Verified (`PASS`)** | [`evidence/04_upg_container_crypto_proof.txt`](../evidence/04_upg_container_crypto_proof.txt) |
| ELF32 `DT_NEEDED`, BusyBox, `sh -n`, `node --check`, QML Latin-1/brace, and `opera.ini` delta | **Verified (`PASS`)** | [`evidence/05_runtime_engines_and_busybox_audit.txt`](../evidence/05_runtime_engines_and_busybox_audit.txt), [`06`](../evidence/06_systemmanager_and_nettv_disasm.txt), [`07`](../evidence/07_dmbht_and_boot_scripts_audit.txt) |
| On-TV flash installation (`Upgrade Successful`) & live Opera TLS 1.2 browsing | **Not Executed Offline** | Offline sandbox lacks MT5880 silicon, `qemu-arm`, and DirectFB kernel drivers; requires physical USB validation on target AOC LE32S5760/20 unit |
