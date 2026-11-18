# Firmware Update Mechanism Security Assessment (`TPV MTK2K14PLF` / `MT5880`)

> **Update Diagram:** [diagrams/UPDATE_MECHANISM.svg](../diagrams/UPDATE_MECHANISM.svg) | **Primary Evidence:** [evidence/03_upg_installer_disasm.txt](../evidence/03_upg_installer_disasm.txt), [evidence/04_upg_container_crypto_proof.txt](../evidence/04_upg_container_crypto_proof.txt)

## 1. Dual Upgrade Channels Identified

The `AOC LE32S5760/20` television implements two distinct update architectures serving different lifecycle roles:

| Update Channel | Package Name | Delivery Trigger | Parser Component | Enforcement Stack |
|---|---|---|---|---|
| **Factory / Boot Recovery** | `upgrade_loader.pkg` (`323.8 MB`) | USB root during cold AC boot / service factory procedure | U-Boot (`load`) | HW eFuse (`0xf0008664`), `kerA`/`B` RSA-2048 trailers, `NFSB` RSA-1024 (`e=3`) |
| **User / UI Local Upgrade (`dlm`)** | `Autorun.upg` (`#DH@FiRm`) | TV Menu: `Home > Setup > Software Update > Local` (plus remote URLs in `libnettv`/`libmtkapp`) | `libdtv_common.so` + `libmtkapp.so` | Outer hardcoded AES + Body MD5 + `AES_Prod` chunks + Chunk SHA-256 + RSA-2048 signature (`cmp r8, #0x20`) |

---

## 2. Demonstrated Security Strengths vs. Confirmed Weaknesses

### Proven Controls
1. **End-to-End Signed Hash Chain Inside `.upg`:** `x_dlm_integrity_check` and `x_dlm_download_by_tag` (`libdtv_common.so`) verify RSA-2048 PKCS#1 v1.5 over `[0x80 : end-256]`, zeroed-slot body MD5 (`0xF0`), decrypted `AES_Prod` per-chunk sentinel `"reserved mtk inc"`, and per-chunk `SHA-256`.
2. **Hardware Model Binding & Partition Verification:** `#DH@FiRm` carries product/model identifiers (`Philips_2K14...` / `TPV_MTK2K14PLF`), while boot-time kernel/rootfs authenticity remains independently protected by BootROM and `NFSB` RSA-1024 (`dm_mount_root_nfsb`) even if an `.upg` payload reaches NAND.
3. **Lock-Compliant Safe Customization Path (`smth` -> `mtd12`):** Validated offline (`19,905`-B `Autorun.upg` using `<TAG>smth</TAG><METHOD>FILE</METHOD>`) to update `/3rd_rw` UBIFS cleanly without touching `ker`/`rfs`/`3rd` read-only partitions.

### Proven Vulnerabilities & Engineering Defects
1. **`roda` Private Key Distribution (`SEC-02`):** Bundling `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem`, `COM_UPG_PriKey_Devt.pem`, and `AES_Prod.key/.iv` inside the downloadable `upgrade_loader.pkg#part:roda` breaks asymmetric isolation for LATAM/Dev `.upg` signing. Note: Kernel `NFSB` RSA-1024 & U-Boot BootROM private keys are **NOT** present in `roda`.
2. **UI Flashing Bug `sub_404f28` (`SEC-08`):** Setting `<METHOD>PART</METHOD>` causes `libmtkapp.so` (`r6 == 0`) to format `"/dev/nand_%d"`, triggering `-22 ENOENT` in `c_fm_erase_flash_part` (`8`-second `...` freeze -> `"REINICIAR OU TENTAR NOVAMENTE"`).
3. **Disabled Bank Failover on Standalone `3rdp` (`0x40ae80`):** `_phm_upg_model_start_upgrade` skips EEPROM A/B bank switching for standalone `3rdp` images.
4. **Hardcoded Outer DLM AES Key (`0x098b64`):** Synthesizes `09291094` * 4 directly in `.text`.
