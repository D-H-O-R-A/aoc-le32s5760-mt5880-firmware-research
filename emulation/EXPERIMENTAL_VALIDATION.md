# Experimental Validation Protocol & Verification Record

> **Machine-Readable Validation Matrix:** [scientific-research/VALIDATION_RESULTS.csv](../scientific-research/VALIDATION_RESULTS.csv)

## 1. Offline Cryptographic Roundtrip & Verification Methodology

Rather than relying on passive inspection alone, every critical hypothesis in this monograph was backed by executable scripts producing auditable proofs ([evidence/01..07](../evidence/01_pkg_and_nfsb_proof.txt)):

| Hypothesis ID | Claim Tested | Experimental Method | Outcome | Artifact |
|---|---|---|---|---|
| **EXP-01** | Unsigned SquashFS modifications cannot mount under `dm-verity` (`rfsA`/`3rdA`) | Repacked `custom_upgrade_loader.pkg` (`3rdA`/`3rdB` modified) vs `upgrade_loader.pkg` and ran kernel's exact RSA-1024 + `dm-bht` equation | **CONFIRMED:** Stock `36,281/36,281` blocks PASS; custom PKG returns `RSA_exact_match=False` | [evidence/01](../evidence/01_pkg_and_nfsb_proof.txt), [evidence/07](../evidence/07_dmbht_and_boot_scripts_audit.txt) |
| **EXP-02** | Replacing U-Boot/Preloader bricks unit unless signed by BootROM OTP hash | Disassembled Thumb-2 SRAM stub at `0xfb001450..0xfb000530` | **CONFIRMED:** OTP bit 20 (`0xf0008664 & 0x100000`) gates RSA check (`0xfb0034f0`); failure jumps unconditionally to infinite loop `0xfb000520: b #0xfb000520` | [evidence/02](../evidence/02_secure_boot_chain_disasm.txt) |
| **EXP-03** | Why local USB `Autorun.upg` (`3rdp` + `METHOD=PART`) failed after ~8s with `REINICIAR OU TENTAR NOVAMENTE` | Disassembled `libmtkapp.so` (`sub_404f28`, `0x40ae80`) & `libdtv_common.so` (`0x098b64`) | **CONFIRMED:** `r6 == 0` formats `"/dev/nand_10"` (`-22 ENOENT`) and `3rdp` skips dual-bank toggle | [evidence/03](../evidence/03_upg_installer_disasm.txt) |
| **EXP-04** | Safe `mtd12` (`/3rd_rw`) container construction (`TAG=smth`, `METHOD=FILE`) obeys all OEM crypto layers cleanly | Built `19,905`-B `Autorun.upg` via `build_safe_rw_upg.py` and verified offline with `verify_upg_container.py` (and tested reproducibly in CI using ephemeral RSA-2048 keys) | **CONFIRMED:** RSA-2048, AES-128-CBC (`09291094*4`), Body MD5, `"reserved mtk inc"`, and per-chunk SHA-256 all pass cleanly | [evidence/04](../evidence/04_upg_container_crypto_proof.txt), [tests/test_research_suite.py](../tests/test_research_suite.py) |
| **EXP-05** | On-TV live flash of `19,905`-B `smth` package (`mtd12`) or QEMU live boot | **NOT EXECUTED** in this offline archival phase | Marked **PENDING HARDWARE/LAB ACCESS** (respecting non-fabricated validation rule) | [RESEARCH_SCOPE.md](../RESEARCH_SCOPE.md) |
