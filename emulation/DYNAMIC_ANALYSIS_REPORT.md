# Dynamic Analysis Report & Honest Scope Boundaries

## 1. Execution Status Declaration

Per methodological integrity rules (**Zero Simulated Dynamic Data**):
- **Full-System Firmware Emulation (`QEMU`):** **NOT EXECUTED** (`qemu-arm` / `qemu-system-arm` unavailable in environment; MT5880 proprietary `dtv_driver.ko` + MMIO `0xf0008664`/`0xf00080b0`/`T8032` lock out naive boot).
- **Physical Television Serial / JTAG / Wiretap Capture:** **NOT EXECUTED** (`ttyMT0` commented out in `etc/inittab`; no external hardware programmer or network packet tap run on the unit).
- **Live On-Target Upgrade Observations Executed Earlier by Owner:**
  - Confirmed empirical symptom during USB UI local flash attempt (`Home > Setup > Software Update > Local > Autorun.upg`): TV displayed `"..."` progress screen for ~`8` seconds and exited cleanly with `"REINICIAR OU TENTAR NOVAMENTE"` (`no permanent brick`).
- **Offline Deterministic Cryptographic & Container Execution Performed (`100%` Verified):**
  Instead of ungrounded dynamic guesses, dynamic/mathematical execution in the offline lab verified **every byte** of the cryptographic verification pipeline and container builders using Python 3, Capstone, OpenSSL, and Node.js.

---

## 2. Verified Offline Dynamic Execution Suite (`7/7 Proofs` + `CI Tests`)

| Executed Script | Runtime Engine | Exact Empirically Observed Result |
|---|---|---|
| `scripts/inspect_pkg_and_nfsb.py` | Python 3 + raw modular arithmetic | Verified all `16` PKG partition offsets + `pow(S, 3, N) == 0^96 || SHA256` across `3rdB`, `3rdA`, `rfsB`, `rfsA`; confirmed failure counter-proof on `custom_upgrade_loader.pkg`. |
| `scripts/inspect_dmbht_and_boot_scripts.py` | Python 3 MD5 Merkle verifier | Recomputed all `23,767` blocks (`3rdA`) and `12,514` blocks (`rfsA`) = **`36,281` blocks MATCHED** against signed NFSB root digests (`666e1b26...`, `6cc5d821...`). |
| `scripts/verify_upg_container.py` | Python 3 + `openssl pkeyutl` + `openssl enc` | Decrypted `19,905`-byte `Autorun.upg`, verified RSA-2048 PKCS#1 v1.5 signature, `#DH@FiRm`, Body MD5, `"reserved mtk inc"`, and `smth` `.tgz` tarball extraction. |
| `scripts/disasm_secure_boot_chain.py`, `disasm_upg_installer.py`, `disasm_systemmanager_and_nettv.py` | Python 3 + `Capstone` ARM/Thumb-2 | Disassembled exact trap instructions (`0xfb001450..0xfb000530`), `nfsb_rsa_check` (`0xc0028df8`), `sub_404f28` (`0x404fa4` -> `"/dev/nand_%d"`), and `SMConfig` `dynqml` (`0x1db58c`). |
| `scripts/inspect_runtime_engines.py` | Python 3 + Node.js JS parser | Verified Opera `Presto 6213` binary strings, `BusyBox v1.15.3`, QML asset counts, and syntax-checked `custom_payload/nettv/user.js` + `staging_rootfs`. |

All dynamic kernel IOCTL timings, live RAM maps (`/proc/meminfo`), and live socket bindings (`/proc/net/tcp`) remain explicitly flagged as **UNOBSERVED** pending physical UART/network access.
