# Update Authentication Analysis

## 1. Signature Enforcement Mechanics (`libdtv_common.so` -> `/ro_data`)

Disassembly of `libdtv_common.so` (`x_dlm_download_by_tag`, `x_dlm_integrity_check` documented in [evidence/03_upg_installer_disasm.txt](../evidence/03_upg_installer_disasm.txt)) shows:
- The verifier extracts the trailing `256`-byte RSA-2048 signature (`cmp r8, #0x20` digest length check for SHA-256).
- It validates PKCS#1 v1.5 padding against the regional RSA public key residing on read-only `/ro_data` (`mtd13`), e.g.:
  - `TPV_MTK2K14PLF_LT0_UPG_PubKey_Prod.pem` (Latin America Production)
  - `TPV_MTK2K14PLF_LT1_UPG_PubKey_Prod.pem`
  - `TPV_MTK2K14PLF_EU0/EU1/EU2_UPG_PubKey_Prod.pem` (European regional variants)
  - `TPV_MTK2K14PLF_COM_UPG_PubKey_Devt.pem` (Development profile)

---

## 2. Hardware Model & Key Compatibility Enforcement

1. **Public vs. Private Key Isolation Failure on `LT0` (`SEC-02`):**
   While retail televisions are intended to hold only public verification keys (`*_PubKey_Prod.pem`) on `/ro_data`, inspecting `upgrade_loader.pkg#part:roda` confirmed that `TPV_MTK2K14PLF_LT0_UPG_PriKey_Prod.pem` and `COM_UPG_PriKey_Devt.pem` were packaged alongside the AES key/IV inside the downloadable `LE32S5760_V2.011_V0.2.zip` release.
2. **Why Boot/Kernel Security Holds Despite `.upg` Signing Exposure:**
   Even with a valid `LT0` `.upg` RSA-2048 signature:
   - `upgrade_loader` BootROM key (`0xfb0034f0`), `kerA`/`kerB` RSA-2048 signing key, and `NFSB` RSA-1024 private key ($d$ matching $N$ at `0xc0429370`) are **NOT** present in `roda` or anywhere on the TV flash.
   - Therefore, `.upg` authentication cannot bypass `dm-verity` (`rfsA`/`3rdA`) or BootROM (`load`), constraining authenticated third-party modifications strictly to `mtd12` (`/3rd_rw`) via `<TAG>smth</TAG>`.
3. **Security Posture:** EU-region (`EU0`/`EU1`/`EU2`) private keys were **not** present in `roda`, meaning regional European units running strict `EUx` keys reject `LT0`-signed `.upg` payloads (**verified structurally by key presence**).
