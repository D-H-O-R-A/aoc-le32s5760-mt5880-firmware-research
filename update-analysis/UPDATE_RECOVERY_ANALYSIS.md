# Update Failure Handling, Recovery & Brick Boundaries

## 1. Empirical Failure Trace (`...` -> `8s` -> `"REINICIAR OU TENTAR NOVAMENTE"`)

When a user triggers `Home > Setup > Software Update > Local` -> `Autorun.upg`, `libmtkapp.so` (`_phm_upg_model_start_upgrade`, `sub_404f28`) executes sequentially:

```
  1. USB Mount & Signature Pass (libdtv_common.so)
       └── Invalid RSA / AES / MD5 / SHA256 -> immediate immediate abort before flash UI spinner
  2. Valid Signature -> UI enters progress screen ("...")
       └── sub_404f28 resolves target path from ixml <METHOD>:
             ├── METHOD="PART" (r6=0) -> formats "/dev/nand_10"
             │     └── c_fm_erase_flash_part("/dev/nand_10") -> -22 ENOENT (devtmpfs only has /dev/mtd*)
             │     └── ~8 seconds timeout/cleanup -> displays "REINICIAR OU TENTAR NOVAMENTE"
             └── METHOD="PMTD" (r6=1) -> resolves "/dev/mtd10" (or mtd12), NO A/B swap for TAG="3rdp"!
  3. METHOD="FILE" + TAG="smth" -> extracts tarball cleanly into /3rd_rw (zero raw erase risk)
```

---

## 2. Failure Recovery Matrix Across Partitions

| Update Target | Power-Loss / Corrupt Payload Outcome | Built-In Recovery Path |
|---|---|---|
| **`smth` (`mtd12` `/3rd_rw`)** | Bad tarball fails SHA-256 before extraction; worst case `/3rd_rw` corrupts only RW overlay while OS boots cleanly from RO `rfsA` + `3rdA`. | Re-flash stock `upgrade_loader.pkg` or clear `/3rd_rw` via safe `smth` payload |
| **Full Official `upgrade_loader.pkg` (`ker`/`rfs`/`3rd`)** | A/B bank parity (`kerA==kerB`, `rfsA==rfsB`, `3rdA==3rdB`) protects OS partitions on valid U-Boot failover (`except 3rdp single-bank overwrite`). | Cold-boot USB rescue with valid `upgrade_loader.pkg` (requires surviving `load`) |
| **`load` (Bootloader / Preloader)** | Any bad erase or unsigned overwrite triggers `0xfb000520` infinite loop trap on cold power-on. | **NONE in software** — requires physical NAND IC desoldering & external hardware programmer |
