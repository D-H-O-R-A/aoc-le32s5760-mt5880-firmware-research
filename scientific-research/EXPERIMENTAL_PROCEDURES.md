# Standardized Experimental Procedures

Each procedure below maps 1-to-1 to deterministic scripts in [scripts/](../scripts/) and captured output logs in [evidence/](../evidence/).

## Procedure 1 — PKG Partitioning, `uImage` Alignment & `NFSB` RSA-1024 Counter-Proof
- **Command:** `python3 scripts/inspect_pkg_and_nfsb.py --pkg ../extracted/upgrade_loader.pkg --custom-pkg ../build/custom_upgrade_loader.pkg --vmlinux ../scratch/vmlinux.bin`
- **Steps:** Parses `16` tagged chunks from `0x98`, verifies embedded `cfig`, strips `0x40`-byte `uImage` header from `vmlinux.bin` to align `VA 0xc0008000`, extracts `e=3 @ 0xc04292f0` and `N @ 0xc0429370`, validates `pow(S, 3, N) == 0^96 || SHA256(hdr[0:0x67])` on stock `3rdB/3rdA/rfsB/rfsA`, and verifies cryptographic rejection (`False`) on `custom_upgrade_loader.pkg`.

## Procedure 2 — Complete `dm-bht` (`36,281`-Block) MD5 Merkle Tree Verification
- **Command:** `python3 scripts/inspect_dmbht_and_boot_scripts.py --workspace .. --repo .`
- **Steps:** Reads `rfsA` (`12,514` 4 KB blocks) and `3rdA` (`23,767` 4 KB blocks), computes every leaf & internal tree node MD5 hash up to the RSA-authenticated `dm-bht` root digest (`666e1b26...` / `6cc5d821...`), and audits all `/etc/scripts/*.sh` mount scripts.

## Procedure 3 — Multi-Stage Machine Code Disassembly (`BootROM`/`Kernel`/`Updater`/`UI`)
- **Commands:**
  1. `python3 scripts/disasm_secure_boot_chain.py --uboot ../extracted/uboot.bin --vmlinux ../scratch/vmlinux.bin`
  2. `python3 scripts/disasm_upg_installer.py --libmtkapp ../extracted/appfs1/basic/libmtkapp.so --libdtv ../extracted/appfs1/basic/libdtv_common.so`
  3. `python3 scripts/disasm_systemmanager_and_nettv.py --workspace ..`
- **Steps:** Extracts annotated Thumb-2/ARM32 instruction sequences covering `0xf0008664`, `0xfb000520`, `0xc0028df8`, `0x404f28` (`"/dev/nand_10"` bug), `0x40ae80`, `0x098b64`, `0x036190`, `0x1889a0`, and `0x1db58c`.

## Procedure 4 — Lock-Compliant `mtd12` (`smth`) Container Build & Verification Roundtrip
- **Commands:** `python3 scripts/build_safe_rw_upg.py ...` -> `python3 scripts/verify_upg_container.py ...` (reproduced hermetically in `tests/test_research_suite.py` using ephemeral temp RSA-2048 keys cleanly in CI).

## Procedure 5 — Automated Inventory, SBOM, Diff & CI Validation
- **Commands:** Run `scripts/firmware_inventory.py`, `metadata_extraction.py`, `firmware_comparison.py`, `sbom_generation.py`, `hash_verification.py --ci`, and `python3 -m unittest discover -s tests -v`.
