# Anti-Rollback & Version Gating Analysis

## 1. Epistemic Summary: What Could and Could Not Be Proven

Per strict scientific standards distinguishing verified enforcement from unobserved mechanisms:

| Mechanism | Observed State | Evidence / Verification Scope |
|---|---|---|
| **Hardware Monotonic OTP Counter (Preloader)** | **NOT OBSERVED / UNCONFIRMED** | Disassembly of `uboot.bin[:0xa040]` found `0xf0008664 & 0x100000` (Secure Boot OTP bit) and RSA verification (`0xfb0034f0`), with **no** observed RPMB/eFuse monotonic firmware version counter comparison routine in the analyzed boot stub. |
| **Container Metadata Compatibility Strings (`#DH@FiRm`)** | **CONFIRMED** | `libdtv_common.so` / `libmtkapp.so` inspect vendor, `#DH@FiRm` magic, `prod_id` (`Philips_2K14...`), `model`, and `<SW><TAG>` inside `ixml`. |
| **Customer Overlay Sentinel Check (`dtv_svc @ 0x036190`)** | **CONFIRMED (Non-Security Preserver)** | `dtv_svc` compares/checks `/3rd_rw/upgrade/customer_version` to decide whether to wipe or retain `/3rd_rw/nettv` across boots (`evidence/06`). |
| **EEPROM Version / Downgrade Rejection Rules (`_phm_upg_model`)** | **PARTIALLY OBSERVED / NO STRICT ANTI-ROLLBACK PROVEN** | No hardware anti-rollback fuse burn was observed during `Autorun.upg` parsing in `libmtkapp.so`. Whether older `upgrade_loader.pkg` (`V1.x`) is accepted or blocked by string-based version comparison inside UI `libmtkapp.so` remains **UNVERIFIED** without a second historical firmware image (`comparative-analysis/`). |

---

## 2. Empirical Observation on Version Tags

- `LE32S5760_V2.011_V0.2.zip` (`2016-08-03`) embeds `SYS_VERSION=IDTV0801_002223_9_001_23_001_224` and `TPV_VERSION=000.001.205.145` inside `appfs1/etc/profile`.
- The absence of an anti-rollback fuse check in `uboot.bin` OTP disassembly implies that **unsigned tampering is blocked by RSA signatures rather than monotonic version numbers**, while behavior regarding factory-signed downgrade packages (`V2.010` vs `V2.011`) cannot be asserted without obtaining an older signed package and testing in controlled isolation.
