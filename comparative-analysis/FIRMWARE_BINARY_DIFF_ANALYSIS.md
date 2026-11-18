# Binary Diff Analysis (`A/B Mirrors`, `Stock PKG vs Custom PKG`, `Rootfs Delta`)

> **Metrics JSON:** [comparison_metrics.json](comparison_metrics.json) | **Diff Tool:** [scripts/firmware_comparison.py](../scripts/firmware_comparison.py)

## 1. Intra-Package Bank A vs. Bank B Bit-Parity

Executing `scripts/firmware_comparison.py` across mirrored factory partitions inside `upgrade_loader.pkg` proves **100% byte-for-byte symmetry** between primary (`A`/`C`) and backup (`B`/`D`) slots at factory provisioning time:

| Bank Pair | Size Each (Bytes) | Bank A SHA-256 | Bank B SHA-256 | Bit-Identical? |
|---|---|---|---|---|
| `kerA` vs `kerB` (`mtd4` vs `mtd5`) | `2,638,124` | `dd670a548ae9546ecc91eacf7dc4de6a9d2ea457178af0afc68c27e1ad59dbe8` | `dd670a548ae9546ecc91eacf7dc4de6a9d2ea457178af0afc68c27e1ad59dbe8` | **True (`0` diffs)** |
| `rfsA` vs `rfsB` (`mtd6` vs `mtd7`) | `51,466,240` | `e7273462007cbb7880f2016f9e57e685383009aa4f757e258dd2d84a32aa6b7a` | `e7273462007cbb7880f2016f9e57e685383009aa4f757e258dd2d84a32aa6b7a` | **True (`0` diffs)** |
| `3rdA` vs `3rdB` (`mtd9` vs `mtd10`) | `97,738,752` | `48de787eb015934940b2d1b60c82259de129fe10759e209b9e3e453f777a196d` | `48de787eb015934940b2d1b60c82259de129fe10759e209b9e3e453f777a196d` | **True (`0` diffs)** |
| `chtC` vs `chtD` (`mtd27` vs `mtd28`) | `65,536` | `1cbb642bee341b0ec5cb04b19b8bb3ab80a92f30e848b3b09c99f6e5c08c5f21` | `1cbb642bee341b0ec5cb04b19b8bb3ab80a92f30e848b3b09c99f6e5c08c5f21` | **True (`0` diffs)** |

*(Because mirrored images share identical SHA-256 digests, differential offset analysis between live TV A/B wear states is only meaningful after future incremental OTA updates.)*

---

## 2. Stock `upgrade_loader.pkg` vs. Laboratory `custom_upgrade_loader.pkg`

Byte comparison between the official `323,840,461`-B `upgrade_loader.pkg` and offline laboratory test artifact `build/custom_upgrade_loader.pkg` (`323,840,461` B) shows:
- **Identical (`14/16` Partitions):** `roda`, `cfig`, `load`, `uenv`, `adsp`, `aqda`, `pqda`, `rfsB`, `rfsA`, `kerB`, `kerA`, `usig`, `chtD`, `chtC` remained bit-for-bit untouched.
- **Modified (`2/16` Partitions — `3rdA` and `3rdB`):** Both retain the outer `97,738,752`-B footprint and `NFSB\x02\x00\x00\x00` header prefix (`4e46534202000000...`), yet replacing the inner SquashFS blocks without holding MediaTek's private `1024`-bit `NFSB` RSA key fails verification immediately (`RSA_exact_match=False` in [evidence/01](../evidence/01_pkg_and_nfsb_proof.txt)).

---

## 3. Stock `extracted/rootfs1` vs. Laboratory `build/staging_rootfs`

Comparing `staging_rootfs` against stock `rootfs1` yields exactly **`21` newly added files** (`run.sh`, `opera_new.ini`, `user.css`, `sm_config.ini`, `ModernLauncher.qml`, plus `16` QML UI view/panel modules under `qt/AEDK/SystemManager/res/HomeScreen/components/`) and **`4` modified files** (`user.js` `+14,650` B, `urlfilter.ini` `+929` B, `opera.ini` `0` B same-size config tune, and `HSMain.qml` `-20,342` B). See [PATCH_ANALYSIS.md](PATCH_ANALYSIS.md) for the security and functional audit of these modifications.
