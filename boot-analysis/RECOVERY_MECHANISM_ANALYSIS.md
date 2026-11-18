# Recovery & Resilience Mechanisms (`A/B Dual Banks`, `USB PKG Rescue`, `Brick Limits`)

## 1. Multi-Tier Recovery Architecture Discovered

The `TPV MTK2K14PLF` / `MT5880` firmware implements three distinct recovery layers — yet empirical and binary analysis reveals strict asymmetries between them:

| Mechanism | Protected Scope | Trigger Condition | Observed Binary / Script Proof | Can It Recover Bricked `load` / BootROM Fail? |
|---|---|---|---|---|
| **1. Dual A/B Mirrored Partitions** | `kerA`/`kerB`, `rfsA`/`rfsB`, `3rdA`/`3rdB` (`chtC`/`chtD`) | EEPROM bank toggle during full-package flash | `upgrade_loader.pkg` banks 100% bit-identical; `libmtkapp.so @ 0x40ae80` toggles bank on full UPG | **NO** — Bootloader (`load`) is NOT A/B mirrored and runs before U-Boot bank selection |
| **2. Cold-Boot USB `upgrade_loader.pkg`** | All `16` PKG partitions (when U-Boot itself survives) | USB FAT32 root containing signed `upgrade_loader.pkg` on AC cold power-on | `upgrade_loader.pkg` package layout; standard MTK U-Boot rescue path (**trigger via USB not live-tested on bricked unit**) | **NO** — If Preloader/U-Boot fails RSA Gate 1, CPU halts at `0xfb000520` before USB HCD initializes |
| **3. Normal OS Local `Autorun.upg` (`smth` / Settings UI)** | Safe writable overlay `mtd12` (`/3rd_rw`) or signed full images | TV UI: `Home > Setup > Software Update > Local` -> `Autorun.upg` | Empirical USB run + `libmtkapp.so` / `libdtv_common.so` disassembly (`evidence/03` & `04`) | **NO** — Requires booting Linux `dtv_svc` + `SystemManager` first |

---

## 2. Empirical `3rdp` Upgrade Failure Root Cause (No Fallback Swap)

As documented in [docs/03](../docs/03_dlm_upg_cryptography_and_libmtkapp_internals.md) and [evidence/03_upg_installer_disasm.txt](../evidence/03_upg_installer_disasm.txt):
- Trying to flash a standalone third-party root partition with `<TAG>3rdp</TAG><METHOD>PART</METHOD>` causes `sub_404f28` (`r6 == 0`) inside `libmtkapp.so` to build path `"/dev/nand_10"` instead of `"/dev/mtd10"`, causing `c_fm_erase_flash_part` to return `-22 ENOENT` after ~`8` seconds (`...` -> `"REINICIAR OU TENTAR NOVAMENTE"`).
- Crucially, `_phm_upg_model_start_upgrade` (`0x40ae80..0x40ae9c`) **explicitly skips EEPROM bank-switching (`3rdA` <-> `3rdB`) for standalone `3rdp` packages**. Even if flashed cleanly, `3rdp` overwrites in place without dual-bank atomic fallback — heightening brick risk if power drops or `NFSB` fails.

---

## 3. Hardware Desoldering / ISP Recovery Prerequisite (Safety Boundary)

Because:
1. Preloader Gate 1 freezes at `0xfb000520` on any bad bootloader write,
2. Kernel `kerA`/`kerB` and `NFSB` `rfsA`/`rfsB`/`3rdA`/`3rdB` fail before userland networking/ADB/telnet starts, and
3. Only `mtd12` (`/3rd_rw`) is non-verity writable storage (with `ro_data` keys needed to sign `.upg` files),
**unbrickable experimentation on kernel/rootfs partitions requires either an external TSOP-48/BGA raw NAND chip programmer or hardware UART + functional U-Boot**. Without an external NAND programmer on hand, halting unsigned partition flashing at `mtd12` prevents permanent hardware loss.
