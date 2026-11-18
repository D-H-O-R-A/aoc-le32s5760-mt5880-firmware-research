# Chapter 6 — Reproducible Experimental Protocol, Script Reference & Hardware Research Guidelines

**Scope:** Every numerical claim, cryptographic digest, virtual address, dynamic dependency list, Merkle tree proof, and instruction trace across this monograph is generated deterministically by the seven proof scripts in [`scripts/`](../scripts/). This chapter documents environment dependencies, strict key-hygiene policy, script CLI usage, passive bench UART/eFuse verification protocols, and a formal glossary of platform subsystems.

---

## 6.1 Reproducibility Toolchain & Security Hygiene

All disassembly and cryptographic verification tools operate strictly in host user-space with zero root privileges or proprietary MediaTek SDKs:

| Dependency | Version / Package | Role in Proof Suite |
|---|---|---|
| **Python 3** | `3.10+` (`hashlib`, `struct`, `tarfile`, `xml.etree`) | Binary parsing, modular exponentiation `pow(sig, e, N)`, `dm-bht` Merkle proofs, ELF32 dynamic parser |
| **Capstone** | `python3-capstone` (`CS_ARCH_ARM`, `ARM`/`THUMB`) | Instruction-exact disassembly of Preloader arm/thumb, `vmlinux`, `libmtkapp`, `libdtv_common`, `SystemManager`, `dtv_svc`, `libnettv` |
| **OpenSSL CLI** | `openssl` (`enc`, `pkeyutl`) | RSA-2048 `-verifyrecover`, raw AES-128-CBC `-nopad` decryption/encryption |
| **Node.js** | `node --check` | Syntax verification of ES5 UserJS (`custom_payload/nettv/user.js`) |
| **POSIX `sh` & GNU `tar`** | Standard coreutils | Shell syntax audit (`sh -n custom_payload/patches/run.sh`) and archive layout normalization |

### Strict IP & Private-Key Hygiene
This research archive enforces strict separation between reproducible verification code and proprietary vendor secrets:
- **`.gitignore` Guardrails:** Strictly excludes `*.pkg`, `*.upg`, `*.squashfs`, `*.img`, `*.bin`, `*.pem`, `*.key`, `*.iv`, `*.tgz`, `*.tar.gz`, `vmlinux*`, `extracted/`, `original_firmware/`, and `tmp/`.
- **Zero Hardcoded Private Keys:** [`scripts/verify_upg_container.py`](../scripts/verify_upg_container.py) uses public verification materials passed explicitly on the CLI (`--pubkey`, `--aes-key`, `--aes-iv`), and [`scripts/build_safe_rw_upg.py`](../scripts/build_safe_rw_upg.py) contains no embedded vendor signing keys, requiring callers to supply explicit local key files (or ephemeral test RSA-2048 keypairs when verifying container framing in lab environments).

---

## 6.2 Executable Proof Suite & Evidence Mapping

Executing [`scripts/run_all_proofs.sh`](../scripts/run_all_proofs.sh) regenerates all seven captured proof logs deterministically into [`evidence/`](../evidence/):

```sh
./scripts/run_all_proofs.sh /path/to/local/AOC/LE32S5760
```

| Stage | Script | Required Local Inputs | Generated Evidence Output | Technical Proofs Executed |
|---:|---|---|---|---|
| **1** | [`inspect_pkg_and_nfsb.py`](../scripts/inspect_pkg_and_nfsb.py) | `extracted/upgrade_loader.pkg`, `build/custom_upgrade_loader.pkg`, `scratch/vmlinux.bin` | [`01_pkg_and_nfsb_proof.txt`](../evidence/01_pkg_and_nfsb_proof.txt) | 16 PKG entries, `cfig`, `kerA`/`kerB` RSA trailers, `uImage` `0x40` strip (`ep=0x8000`), `e=3` (`0xc04292f0`), `N` (`0xc0429370`), exact RSA-1024 checks on `3rdB`/`3rdA`/`rfsB`/`rfsA`, rejection counter-proof on `custom_upgrade_loader.pkg` |
| **2** | [`disasm_secure_boot_chain.py`](../scripts/disasm_secure_boot_chain.py) | `extracted/uboot.bin`, `scratch/vmlinux.bin` | [`02_secure_boot_chain_disasm.txt`](../evidence/02_secure_boot_chain_disasm.txt) | Thumb Preloader (`0xfb00048c..0xfb00153c`: `0xf0008664`, `0xfb0053bc`, `0xf00080b0`), `nfsb_header` getters (`0xc0028d44..0xc0028df0`), `nfsb_rsa_check` (`0xc0028df8`), `dm_mount_root_nfsb` (`0xc0009594`), `populate_table_nfsb` (`0xc02243c4`) |
| **3** | [`disasm_upg_installer.py`](../scripts/disasm_upg_installer.py) | `extracted/appfs1/basic/libmtkapp.so`, `libdtv_common.so` | [`03_upg_installer_disasm.txt`](../evidence/03_upg_installer_disasm.txt) | `sub_404f28` (`PART`/`PMTD`/`PSDM`/`EEP`), `.rodata` `PMTD[0..20]` (`0x5b0b54`), `sub_4074c0` / `sub_407d4c`, `0x4060d0` 33B loader, `0x40ae50` `3rdp` skip, `dlm_locate_codefile_hdr`, `x_dlm_download_by_tag` |
| **4** | [`verify_upg_container.py`](../scripts/verify_upg_container.py) | `build/Autorun.upg` + `/ro_data/key` public PEM & AES key/IV files | [`04_upg_container_crypto_proof.txt`](../evidence/04_upg_container_crypto_proof.txt) | Raw RSA-2048 signature verification, `#DH@FiRm` AES-128-CBC decrypt, zeroed-slot Body MD5, chunk `"reserved mtk inc"` & SHA-256 checks, `ixml` XML & 14 GNU `tar` entries |
| **5** | [`inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py) | `extracted/appfs1`, `extracted/rootfs1`, `custom_payload/` | [`05_runtime_engines_and_busybox_audit.txt`](../evidence/05_runtime_engines_and_busybox_audit.txt) | Opera/Netflix/NetTV/`dtv_svc` build strings, 73 BusyBox/bin applets + 10 missing tools check, `SystemManager` offsets, `sh -n`, `node --check`, 18 QML Latin-1/brace audits |
| **6** | [`disasm_systemmanager_and_nettv.py`](../scripts/disasm_systemmanager_and_nettv.py) | All 9 firmware ELFs in `extracted/` | [`06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt) | ELF32 section sizes, `RPATH`, `DT_NEEDED` graphs, `SystemManager` `main`/`SMConfig`/`dynqml` trace, `dtv_svc` `customer_version` trace, `libnettv.so` `_imnettv_copydata` |
| **7** | [`inspect_dmbht_and_boot_scripts.py`](../scripts/inspect_dmbht_and_boot_scripts.py) | `extracted/upgrade_loader.pkg`, `extracted/appfs1/etc/`, `custom_payload/nettv/opera_new.ini` | [`07_dmbht_and_boot_scripts_audit.txt`](../evidence/07_dmbht_and_boot_scripts_audit.txt) | Full 36,281-block two-level `dm-bht` MD5 verification (`3rdA` + `rfsA`), SquashFS 4.0 superblocks, `rc.local.partial` / `autorun.sh` / `dmverity_mount_*` / `ubi_mount_*` excerpts, `opera.ini` diff |

### Standalone CLI Usage Examples

To test any individual container (`Autorun.upg`) independently without re-running full disassembly:
```sh
python3 scripts/verify_upg_container.py \
  --upg /path/to/Autorun.upg \
  --pubkey /path/to/TPV_MTK2K14PLF_LT0_UPG_PubKey_Prod.pem \
  --aes-key /path/to/TPV_MTK2K14PLF_LT0_UPG_AES_Prod.key \
  --aes-iv /path/to/TPV_MTK2K14PLF_LT0_UPG_AES_Prod.iv
```

### Complete Script CLI Argument & Failure-Mode Matrix

| Script | CLI Flags | Expected Exit Status & Assertion Invariants |
|---|---|---|
| `inspect_pkg_and_nfsb.py` | `--pkg <stock.pkg> [--custom-pkg <mod.pkg>] --vmlinux <vmlinux.bin>` | Asserts `IH_MAGIC == 0x27051956`, `NFSB` headers on `3rdB`/`3rdA`/`rfsB`/`rfsA` satisfy `pow(sig, 3, N) == 0^96 \|\| SHA256`, and modified `--custom-pkg` fails verification cleanly |
| `disasm_secure_boot_chain.py` | `--uboot <uboot.bin> --vmlinux <vmlinux.bin>` | Disassembles Thumb-2 Preloader (`0xfb000000` base) + strips `0x40`-byte `uImage` header on `vmlinux.bin` before ARM32 disassembly (`0xc0008000`) |
| `disasm_upg_installer.py` | `--libmtkapp <libmtkapp.so> --libdtv <libdtv_common.so>` | Resolves `.rodata` `PMTD[0..20]` (`0x5b0b54`), `sub_404f28`, PIC GOT string literals (`got_base = 0x68aa74`), and `libdtv_common.so` DLM routines |
| `verify_upg_container.py` | `--upg <file.upg> --pubkey <pub.pem> --aes-key <key> --aes-iv <iv>` | Fails via `AssertionError` on any RSA-2048 mismatch, invalid `#DH@FiRm` magic, length mismatch, zeroed-slot MD5 divergence, wrong `"reserved mtk inc"` chunk marker, wrong chunk SHA-256, or unsafe `tar` path (`/` or `..`) |
| `inspect_runtime_engines.py` | `--workspace <ws> --repo <repo>` | Runs `sh -n` + BusyBox forbidden-command check (`pidof`, `pgrep`, `renice`, `ionice`, `chown`, `killall`, `unzip`), `node --check` on `user.js`, and ISO-8859-1 (`<= 0xff`) + balanced-brace check on all 18 QML files |
| `disasm_systemmanager_and_nettv.py` | `--workspace <ws>` | Audits all 9 ELF32 headers/sections/`DT_NEEDED`, disassembles `SystemManager`, `dtv_svc` (via GOT `0x411170`), and `libnettv.so` |
| `inspect_dmbht_and_boot_scripts.py` | `--workspace <ws> --repo <repo>` | Asserts 100% leaf + Level-0 + signed root MD5 match on `3rdA` (`23,767` blocks) & `rfsA` (`12,514` blocks), extracts clean boot script excerpts, and prints exact `opera.ini` delta |
| `build_safe_rw_upg.py` | `--payload-dir <dir> [--stock-userjs <dir>] --privkey <pem> --aes-key <k> --aes-iv <iv> --out <out.upg>` | Packages deterministic root-owned GNU tarball into `<TAG>smth</TAG><METHOD>FILE</METHOD><PATH>/3rd_rw/nettv</PATH>`; no signing key bundled |

### Ephemeral Lab Container Structural Validation (Zero Vendor Secrets Required)

Researchers replicating container framing locally without vendor keys can validate `build_safe_rw_upg.py` and `verify_upg_container.py` end-to-end against a disposable OpenSSL test keypair:
```sh
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /tmp/test_priv.pem
openssl pkey -in /tmp/test_priv.pem -pubout -out /tmp/test_pub.pem
printf '00112233445566778899aabbccddeeff\n' > /tmp/test.key
printf 'ffeeddccbbaa99887766554433221100\n' > /tmp/test.iv
python3 scripts/build_safe_rw_upg.py --payload-dir custom_payload/nettv --privkey /tmp/test_priv.pem --aes-key /tmp/test.key --aes-iv /tmp/test.iv --out /tmp/test.upg
python3 scripts/verify_upg_container.py --upg /tmp/test.upg --pubkey /tmp/test_pub.pem --aes-key /tmp/test.key --aes-iv /tmp/test.iv
```

---

## 6.3 Hardware Bench Research Protocol (UART / eFuse Inspection)

For researchers investigating physical MTK2K14PLF hardware revisions offline on a workbench, arbitrary kernel flashing over USB is strictly discouraged without non-volatile flash backups. Standard non-destructive observation methodology:

1. **Full Pre-Experiment Flash Image Backup:** Preserve verified stock `upgrade_loader.pkg` (`SHA-256: 219de76d...`) and capture raw NAND/SPI dumps via programmer prior to modifying any boot or root partition.
2. **Passive Serial UART Diagnostics (`3.3V` TTL, `115200 8N1`):** As proved by `extracted/appfs1/etc/rc.d/rc.local.partial` line 5 (`stty -F /dev/ttyMT3 115200`), console diagnostics output on `/dev/ttyMT3` at `115200` baud. Monitoring RX/TX passively captures:
   - Preloader `not secure loader` / HW-LZHS messages (`0xfb00052a`) and U-Boot environment strings.
   - Kernel `dm-verity` / `nfsb` logs (`<6>/dev/nfsb: NFSB header found and verified.`, `dm_bht_verify_block` mismatches).
   - Runtime `[PHM_UPG]` messages (`sub_404f28` path formation, `c_fm_erase_flash_part` return codes) and `[P]========>>3rd_rw r/w file opera.ini exsit!!` (`libnettv.so` `_imnettv_copydata`).
3. **Key Greppable Diagnostic Signatures Over UART (`/dev/ttyMT3`):**
   - `NFSB header found and verified.` -> Kernel `dm_mount_root_nfsb` verified `rfs` RSA-1024 header.
   - `nfsb: header verification failed` / `Failed to create mapped device` -> Kernel `NFSB` rejected modified SquashFS partition.
   - `[PHM_UPG]` + `Upgrade NG` -> `libmtkapp.so` aborted flash installation (`-22 ENOENT` if `PART` hit `/dev/nand_10`).
   - `rm -rf /3rd_rw/nettv` / `tar zxf /tmp/upgrade/smth -C /3rd_rw/nettv` / `Upgrade Successful` -> Expected clean path for `<TAG>smth</TAG><METHOD>FILE</METHOD>`.
   - `3rd_rw r/w file opera.ini exsit!! copy to ENV_OPERA_HOME folder` -> Expected confirmation from `libnettv.so` upon launching Opera/NetTV.
4. **Read-Only eFuse Verification (`0xf0008664`):** Only when authorized hardware UART/U-Boot diagnostics are accessible on a board revision can reading register `0xf0008664` bit `20` (`0x100000`) empirically distinguish retail fused boards from engineering unfused samples. Until verified otherwise, treat `load`, `kerA`/`kerB`, `rfsA`/`rfsB`, and `3rdA`/`3rdB` as strictly immutable and anchor persistent modifications exclusively on `mtd12` (`/3rd_rw`).

---

## 6.4 Technical Glossary

- **`Autorun.upg`:** Philips/TPV five-layer DLM container ingested by the TV local USB upgrade menu (`libdtv_common.so` + `libmtkapp.so`).
- **`#DH@FiRm`:** 8-byte decrypted header magic validated inside `dlm_locate_codefile_hdr` (`0x98b60`) under internal AES-128-CBC key `0x94102909 * 4`.
- **`dm-bht`:** Two-level Chromium-lineage MD5 Merkle hash tree appended after SquashFS 4.0 payloads inside `3rdA/B` (`23,767` blocks) and `rfsA/B` (`12,514` blocks).
- **`HW-LZHS`:** MediaTek proprietary LZSS + Huffman + 8-bit checksum silicon decompression block mapped at MMIO `0xf00080b0..0xf00080bc`.
- **`NFSB`:** `0xe7`-byte `dm-verity` v2 superblock wrapping SquashFS partitions; enforces raw textbook RSA-1024 (`e = 3 @ 0xc04292f0`, `N @ 0xc0429370`) via full-width `mpuint_equal` (`0xc0029000`).
- **`PART` vs `PMTD`:** XML `<METHOD>` selectors in `libmtkapp.so` `sub_404f28`; `PART` (`r6=0`) generates invalid `/dev/nand_%d` (failing `-22 ENOENT`), whereas `PMTD` (`r6=1`) indexes `mtd0..mtdsdm20`.
- **`/3rd_rw` (`mtd12`):** Unverified UBI/UBIFS read-write partition (`ubi4:3rd_rw`), safe persistence target for `<TAG>smth</TAG><METHOD>FILE</METHOD>` delivery (`opera_new.ini`).
- **`SystemManager` (`dynqml`):** Qt `4.8.3` DirectFB HomeScreen executable; loads `qrc:/HomeScreen/HSMain.qml` unless `/3rd/qt/AEDK/SystemManager/sm_config.ini` sets `[tpvlib] dynqml=true`.
- **`uImage` Header Alignment:** `64`-byte `0x27051956` prefix in `scratch/vmlinux.bin` (`load=0x00007fc0`, `ep=0x00008000`) whose stripping aligns kernel `.text`/`.rodata` virtual pointers identically at `0xc0008000`.
- **`_imnettv_copydata`:** Setup function inside `libnettv.so` (`0x1889a0..0x188d20`) synchronizing `/mnt/browser/op*.{dat,pem}` and honoring `/3rd_rw/nettv/opera_new.ini`.
- **`customer_version`:** Sentinel file `/3rd_rw/upgrade/customer_version` checked by `dtv_svc` (`0x03628c`); suppresses factory overwrite of `/3rd_rw/nettv/opera` across reboots.
- **`3rd_rw_list.txt`:** MediaTek build-time symlink specification (`data`, `link-dir`, `link-file`) mapping `/3rd` SquashFS subdirectories onto writable `/3rd_rw` paths (`netflix`, `widevine/keybox`).
- **`stagecraft` (`wrp_leanback`):** Legacy Adobe Flash Lite runtime used for `yt_lbl.swf`, governed by `extracted/rootfs1/leanback/config.ini` and `youtube_keymap.ini`.
- **`GOTOFF` / PIC Relocation:** Position-independent ARM code pattern loading negative `.rodata` displacement offsets added to a register holding `.got` (`0x411170` in `dtv_svc`, `0x68aa74` in `libmtkapp.so`).
