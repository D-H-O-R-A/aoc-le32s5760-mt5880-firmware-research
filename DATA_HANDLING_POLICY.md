# Data Handling and Repository Hygiene Policy

## 1. Artifact Classification

To balance full scientific reproducibility against copyright, privacy, and cryptographic safety, all materials touched by this investigation are classified into three tiers:

| Tier | Description | Examples | Git Commit Policy |
|---|---|---|---|
| **Tier 1: Open Research Artifacts** | Original analysis scripts, Capstone disassembly parsers, metadata schemas, SBOMs, SVGs, tests, and Markdown documentation | `docs/*.md`, `scripts/*.py`, `evidence/*.txt`, `hardware/`, `security/`, `sbom/*.json`, `scientific-research/`, `diagrams/*.svg`, `tests/` | **Committed** to repository under MIT License (scripts/docs) |
| **Tier 2: User-Authored Configuration Experiments** | Original QML UI prototypes, Opera INI/CSS/JS user-agent/adblock configs (`custom_payload/`) | `custom_payload/patches/*`, `custom_payload/nettv/*`, `custom_payload/qml/*` | **Committed** (authored cleanly without copying OEM binaries) |
| **Tier 3: Restricted Proprietary & Key Materials** | Factory flash archives, SquashFS/UBI images, proprietary OEM ELFs/modules, RSA private/public `.pem`, AES `.key`/`.iv` files | `original_firmware/`, `extracted/`, `*.pkg`, `*.upg`, `*.bin`, `*.squashfs`, `*.pem`, `*.key`, `*.iv`, `vmlinux*` | **NEVER COMMITTED** (blocked by [.gitignore](.gitignore) and verified in CI) |

## 2. Redaction and Verification Architecture

- **Parameterized Proof Scripts:** All Python tools under [scripts/](scripts/) accept filesystem paths via CLI flags (`--pkg`, `--vmlinux`, `--pubkey`, `--aes-key`, `--aes-iv`, `--workspace`) instead of hardcoding OEM keys or embedding proprietary payloads.
- **Public Output Proofs Only:** Evidence logs under [evidence/](evidence/) contain only deterministic mathematical proofs (SHA-256 digests, RSA moduli `N` as public verification constants embedded in firmware `rodata`, instruction addresses, and ASCII disassembly traces) — never private exponents `d` or raw AES product key bytes.
- **CI Dual-Mode Execution:** Continuous Integration runs in `--ci` offline mode using generated JSON/CSV/SBOM manifests plus ephemeral in-memory/tempdir RSA-2048 keys for roundtrip container testing (`tests/test_research_suite.py`), while full cryptographic verification (`scripts/run_all_proofs.sh`) runs against a local researcher workspace containing the official ZIP/PKG archive.

## 3. Re-Verification Against Local Workspace

Independent researchers with a legitimate copy of `LE32S5760_V2.011_V0.2.zip` (`SHA-256: 014e235cb9406be9d8d61cc780093d3d5196b8748f72a088b43641dc99d0d1ff`) can verify bit-for-bit consistency using [scripts/hash_verification.py](scripts/hash_verification.py) `--workspace ..`.
