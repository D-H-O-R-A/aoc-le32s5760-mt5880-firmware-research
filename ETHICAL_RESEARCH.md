# Ethical Research Policy

## 1. Purpose and Guiding Principles

This repository (`aoc-le32s5760-mt5880-firmware-research`) documents static reverse engineering, cryptographic container analysis, software bill of materials (SBOM) inventorying, and interoperability evaluation of **owner-possessed consumer television firmware** targeting the **AOC LE32S5760/20** (`TPV MTK2K14PLF` / **MediaTek MT5880** ARMv7-A Smart TV platform).

All research activities documented in this repository adhere to three foundational ethical principles:

1. **Authorized Ownership and Isolated Offline Scope:** Analysis was conducted exclusively against a retail television unit and its publicly distributed official OEM firmware update package (`LE32S5760_V2.011_V0.2.zip` containing `upgrade_loader.pkg`, timestamped `2016-08-03`). No unauthorized network scanning, remote exploitation, cloud server probing, or third-party infrastructure interference was performed.
2. **Non-Destructive and Brick-Avoidant Engineering:** Once static disassembly proved a three-stage cryptographic chain of trust (BootROM/Preloader OTP eFuse `0xf0008664 & 0x100000`, U-Boot kernel RSA-2048 trailers, and Linux `dm-verity` `NFSB` RSA-1024) coupled with the absence of an external hardware NAND/SPI chip programmer, invasive unsigned flash writes were deliberately halted rather than endangering end-user hardware.
3. **Dual-Use Harm Minimization:** Cryptographic container analyses (`.pkg`, `Autorun.upg`, `NFSB`) are published for interoperability verification, legacy device preservation, and defensive security auditing. Extracted symmetric AES materials (`TPV_MTK2K14PLF_LT0_UPG_AES_Prod.key/.iv`), asymmetric private/public key `.pem` files (`*.pem`, `*.key`, `*.iv`), raw binary partitions (`*.bin`, `*.squashfs`, `*.img`), and original factory images (`*.pkg`, `*.upg`) are **strictly excluded** from version control (enforced by [.gitignore](.gitignore) and automated CI hygiene checks).

## 2. Explicit Boundaries of Investigation

| Activity | Permitted in This Research | Prohibited / Out of Scope |
|---|---|---|
| Static binary disassembly & ELF inspection | Yes (local offline workspace only) | Redistribution of proprietary OEM ELF binaries |
| Offline cryptographic container verification | Yes (ephemeral test keys in CI; local materials via CLI flags) | Publishing extracted OEM AES/RSA key files or ready-to-flash unauthorized images |
| Legacy CVE & TLS/CA store risk cataloging | Yes (version-matched defensive audit) | Weaponized exploit code or remote payload delivery |
| Interoperability / accessibility customization | Yes (confined to `mtd12` `/3rd_rw` userland configuration) | Bypassing DRM/Widevine/PlayReady content protection or paid services |

## 3. Epistemic Honesty and Conflict Disclosure

Scientific integrity requires distinguishing **confirmed** artifacts (reproducibly derived from disassembled machine instructions, verified hashes, or captured file contents), **inferred** architectural properties (consistent with kernel source path strings or driver symbols), and **unknown** attributes (such as unverified bare-metal PCB silkscreen markings or uncaptured live Ethernet packet traces). No hypothesis is presented as confirmed without primary binary or empirical reproduction evidence.
