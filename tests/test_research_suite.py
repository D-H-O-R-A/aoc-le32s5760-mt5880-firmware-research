#!/usr/bin/env python3
"""
Automated offline & CI verification suite for:
  aoc-le32s5760-mt5880-firmware-research

Runs hermetically without factory firmware blobs or OEM secrets by generating
ephemeral RSA-2048 keys inside temporary storage and validating all schemas,
manifests, SBOMs, SVGs, scripts, custom payloads, and secret hygiene rules.
"""

import csv
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFirmwareResearchArchive(unittest.TestCase):
    """Validates tooling, cryptographic roundtrips, schemas, diagrams, and repo hygiene."""

    def test_01_all_python_scripts_compile(self) -> None:
        scripts_dir = REPO_ROOT / "scripts"
        py_files = sorted(scripts_dir.glob("*.py"))
        self.assertGreaterEqual(len(py_files), 12)
        for pyf in py_files:
            py_compile.compile(str(pyf), doraise=True)

    def test_02_ci_hash_manifest_verification(self) -> None:
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "hash_verification.py"), "--ci", "--repo", str(REPO_ROOT)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, msg=f"hash_verification --ci failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("[PASS]", proc.stdout)

    def test_03_ephemeral_upg_build_and_verify_roundtrip(self) -> None:
        """Exercises build_safe_rw_upg.py -> verify_upg_container.py end-to-end with ephemeral RSA-2048 keys."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            priv_pem = td_path / "ephemeral_priv.pem"
            pub_pem = td_path / "ephemeral_pub.pem"
            aes_key = td_path / "ephemeral_aes.key"
            aes_iv = td_path / "ephemeral_aes.iv"
            out_upg = td_path / "Autorun.upg"

            subprocess.check_call(
                ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(priv_pem)],
                stderr=subprocess.DEVNULL,
            )
            subprocess.check_call(
                ["openssl", "pkey", "-in", str(priv_pem), "-pubout", "-out", str(pub_pem)],
                stderr=subprocess.DEVNULL,
            )
            # Match 33-byte (32 ASCII hex chars + '\n') OEM AES credential structure
            aes_key.write_bytes(b"00112233445566778899aabbccddeeff\n")
            aes_iv.write_bytes(b"ffeeddccbbaa99887766554433221100\n")

            build_cmd = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "build_safe_rw_upg.py"),
                "--payload-dir",
                str(REPO_ROOT / "custom_payload" / "nettv"),
                "--privkey",
                str(priv_pem),
                "--aes-key",
                str(aes_key),
                "--aes-iv",
                str(aes_iv),
                "--out",
                str(out_upg),
            ]
            subprocess.check_call(build_cmd)
            self.assertTrue(out_upg.is_file())
            self.assertGreater(out_upg.stat().st_size, 1000)

            verify_cmd = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "verify_upg_container.py"),
                "--upg",
                str(out_upg),
                "--pubkey",
                str(pub_pem),
                "--aes-key",
                str(aes_key),
                "--aes-iv",
                str(aes_iv),
            ]
            vproc = subprocess.run(verify_cmd, capture_output=True, text=True)
            self.assertEqual(vproc.returncode, 0, msg=f"verify_upg_container failed:\n{vproc.stdout}\n{vproc.stderr}")
            self.assertIn("[PASS] RSA-2048 PKCS#1 v1.5 signature", vproc.stdout)
            self.assertIn("TAG='smth', METHOD='FILE', PATH='/3rd_rw/nettv'", vproc.stdout)

    def test_04_sbom_spdx_and_cyclonedx_schemas(self) -> None:
        spdx_p = REPO_ROOT / "sbom" / "SBOM.spdx.json"
        cdx_p = REPO_ROOT / "sbom" / "SBOM.cdx.json"
        spdx = json.loads(spdx_p.read_text(encoding="utf-8"))
        cdx = json.loads(cdx_p.read_text(encoding="utf-8"))

        self.assertEqual(spdx.get("spdxVersion"), "SPDX-2.3")
        self.assertEqual(spdx.get("dataLicense"), "CC0-1.0")
        self.assertGreaterEqual(len(spdx.get("packages", [])), 26)
        self.assertGreaterEqual(len(spdx.get("relationships", [])), 26)

        self.assertEqual(cdx.get("bomFormat"), "CycloneDX")
        self.assertEqual(cdx.get("specVersion"), "1.5")
        self.assertGreaterEqual(len(cdx.get("components", [])), 25)

    def test_05_metadata_and_json_files_valid(self) -> None:
        for rel in [
            "firmware-forensics/FIRMWARE_METADATA.json",
            "comparative-analysis/comparison_metrics.json",
            "scientific-research/RESEARCH_ARTIFACTS_MANIFEST.json",
        ]:
            p = REPO_ROOT / rel
            self.assertTrue(p.is_file(), f"Missing JSON artifact: {rel}")
            obj = json.loads(p.read_text(encoding="utf-8"))
            self.assertIsInstance(obj, dict)

        meta = json.loads((REPO_ROOT / "firmware-forensics" / "FIRMWARE_METADATA.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["factory_package"]["pkg_partition_count"], 16)
        self.assertEqual(meta["kernel"]["embedded_source_path_count"], 381)
        self.assertEqual(meta["trust_store"]["certificate_count"], 186)

    def test_06_csv_files_rectangular_and_populated(self) -> None:
        expectations = [
            ("hardware/HARDWARE_COMPONENT_INVENTORY.csv", 15),
            ("firmware-forensics/FIRMWARE_BINARY_INVENTORY.csv", 40),
            ("kernel-analysis/KERNEL_MODULE_INVENTORY.csv", 12),
            ("filesystem/FILESYSTEM_INVENTORY.csv", 4000),
            ("security/SECURITY_CONTROLS_INVENTORY.csv", 10),
            ("privacy/EXTERNAL_ENDPOINT_INVENTORY.csv", 200),
            ("scientific-research/VALIDATION_RESULTS.csv", 10),
        ]
        for rel, min_rows in expectations:
            p = REPO_ROOT / rel
            self.assertTrue(p.is_file(), f"Missing CSV: {rel}")
            with p.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.reader(f))
            self.assertGreater(len(rows), min_rows, f"Unexpected low row count in {rel}: {len(rows)}")
            header_len = len(rows[0])
            for idx, r in enumerate(rows[1:], 2):
                self.assertEqual(len(r), header_len, f"Column count mismatch in {rel}:{idx}")

    def test_07_svg_diagrams_well_formed(self) -> None:
        svg_dir = REPO_ROOT / "diagrams"
        expected = [
            "HARDWARE_ARCHITECTURE.svg",
            "BOOT_CHAIN.svg",
            "FIRMWARE_STRUCTURE.svg",
            "SOFTWARE_DEPENDENCIES.svg",
            "NETWORK_ARCHITECTURE.svg",
            "UPDATE_MECHANISM.svg",
            "SECURITY_THREAT_MODEL.svg",
        ]
        for name in expected:
            p = svg_dir / name
            self.assertTrue(p.is_file(), f"Missing diagram: {name}")
            tree = ET.parse(p)
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("svg"))
            self.assertIn("viewBox", root.attrib)

    def test_08_custom_payload_js_syntax(self) -> None:
        js_file = REPO_ROOT / "custom_payload" / "nettv" / "user.js"
        self.assertTrue(js_file.is_file())
        if subprocess.run(["which", "node"], capture_output=True).returncode == 0:
            proc = subprocess.run(["node", "--check", str(js_file)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_09_no_secrets_or_proprietary_binaries_in_repo(self) -> None:
        forbidden_suffixes = (".pem", ".key", ".iv", ".pkg", ".upg", ".squashfs", ".img", ".bin", ".ko")
        secret_markers = (
            "-----BEGIN " + "RSA PRIVATE KEY-----",
            "-----BEGIN " + "PRIVATE KEY-----",
            "-----BEGIN " + "EC PRIVATE KEY-----",
        )
        for dp, _, fns in os.walk(REPO_ROOT):
            if "/.git" in dp or "__pycache__" in dp:
                continue
            for fn in fns:
                fp = Path(dp) / fn
                self.assertFalse(fn.lower().endswith(forbidden_suffixes), f"Forbidden binary/key suffix in repo: {fp}")
                if fp.suffix in (".md", ".txt", ".py", ".sh", ".yml", ".yaml", ".json", ".csv"):
                    txt = fp.read_text(encoding="utf-8", errors="ignore")
                    for marker in secret_markers:
                        self.assertNotIn(marker, txt, f"Secret key block marker leaked in {fp}")

    def test_10_markdown_relative_links_resolve(self) -> None:
        link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        broken = []
        for md_path in sorted(REPO_ROOT.rglob("*.md")):
            if ".git" in md_path.parts:
                continue
            lines = md_path.read_text(encoding="utf-8", errors="replace").splitlines()
            in_fence = False
            for lineno, line in enumerate(lines, 1):
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in link_re.findall(line):
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    rel_part = target.split("#", 1)[0].strip()
                    if not rel_part:
                        continue
                    resolved = (md_path.parent / rel_part).resolve()
                    if not resolved.exists():
                        broken.append(f"{md_path.relative_to(REPO_ROOT)}:{lineno} -> {target}")
        self.assertEqual(broken, [], msg="Broken relative Markdown links:\n" + "\n".join(broken))


if __name__ == "__main__":
    unittest.main(verbosity=2)
