# Independent Reproducibility Protocol

> **Artifact Index JSON:** [RESEARCH_ARTIFACTS_MANIFEST.json](RESEARCH_ARTIFACTS_MANIFEST.json) | **Hash Verification Tool:** [scripts/hash_verification.py](../scripts/hash_verification.py)

## 1. Two-Mode Reproducibility Model

Because copyright and cryptographic key custody prohibit committing OEM firmware dumps (`*.pkg`, `*.upg`, `*.pem`, `*.key`, `*.iv`, `vmlinux*`) into Git ([DATA_HANDLING_POLICY.md](../DATA_HANDLING_POLICY.md)), every automated claim in this study can be reproduced across two complementary scopes:

### Mode A — Public Repository Verification (`--ci`, Zero Proprietary Blobs Required)
Validates repository integrity, JSON/CSV/SPDX/CycloneDX/SVG schemas, Markdown link integrity, zero leaked secrets, and end-to-end `#DH@FiRm` `Autorun.upg` container generation/verification using temporary ephemeral `RSA-2048` keys:
```sh
python3 scripts/hash_verification.py --ci
python3 -m unittest discover -s tests -v
```

### Mode B — Full Factory Firmware Bit-Level Reproduction (`--workspace`, Owner Archive Required)
When paired with an independently obtained copy of `LE32S5760_V2.011_V0.2.zip` (`SHA-256: 014e235cb9406be9d8d61cc780093d3d5196b8748f72a088b43641dc99d0d1ff`):
```sh
# 1. Confirm exact match across 103 ZIP / PKG / Partition / ELF / Repo digests
python3 scripts/hash_verification.py --workspace /path/to/workspace

# 2. Re-run all 7 primary cryptographic, Merkle & Capstone disassembly proofs
sh scripts/run_all_proofs.sh /path/to/workspace

# 3. Re-generate binary inventories, A/B diff metrics, endpoints, and SBOMs
python3 scripts/firmware_inventory.py --workspace /path/to/workspace
python3 scripts/metadata_extraction.py --workspace /path/to/workspace
python3 scripts/firmware_comparison.py --workspace /path/to/workspace
python3 scripts/sbom_generation.py --workspace /path/to/workspace
```
