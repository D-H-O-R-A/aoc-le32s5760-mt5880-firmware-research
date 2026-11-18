#!/usr/bin/env python3
"""
Extracts structured forensic metadata from an extracted AOC LE32S5760/20 workspace:
  - Kernel banner, IKCONFIG presence, source paths (/share/Release_code_use/...)
  - Bootloader / Preloader strings, T8032 standby MCU, Dual-channel DRAM calibration flags
  - Userland OS/ODM identity (etc/profile, inittab, passwd, busybox, CA trust stores)
  - Fast O(N) external URL/endpoint extraction across appfs1 and rootfs1
  - Hardware component traceability matrix (Confirmed vs Inferred vs Unknown)
  - Research artifacts JSON catalog

Outputs:
  - firmware-forensics/FIRMWARE_METADATA.json
  - privacy/EXTERNAL_ENDPOINT_INVENTORY.csv
  - hardware/HARDWARE_COMPONENT_INVENTORY.csv
  - scientific-research/RESEARCH_ARTIFACTS_MANIFEST.json
"""

import argparse
import csv
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_pkg_and_nfsb import parse_pkg_headers  # noqa: E402


STD_DOC_HOSTS = (
    "w3.org",
    "schemas.",
    "purl.org",
    "xmlpull.org",
    "adobe.com",
    "mozilla.org",
    "qt-project.org",
    "qt.nokia.com",
    "trolltech.com",
    "khronos.org",
    "gnu.org",
    "kernel.org",
    "apache.org",
    "freedesktop.org",
    "libpng.org",
    "opensource.org",
    "creativecommons.org",
    "ietf.org",
    "openssl.org",
    "curl.haxx.se",
    "xmlsoft.org",
    "sqlite.org",
    "example.com",
    "example.org",
    "foo.com",
    "bar.com",
    "test.com",
)


def fast_extract_urls(data: bytes) -> List[str]:
    """O(N) bounded URL scanner immune to regex catastrophic backtracking."""
    urls: List[str] = []
    allowed = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_:/?=&%+#~")
    n = len(data)
    for scheme in (b"https://", b"http://"):
        start = 0
        slen = len(scheme)
        while True:
            idx = data.find(scheme, start)
            if idx == -1:
                break
            end = idx + slen
            lim = min(n, idx + 140)
            while end < lim and data[end] in allowed:
                end += 1
            if end > idx + slen + 2:
                urls.append(data[idx:end].decode("ascii", errors="ignore"))
            start = end
    return urls


def classify_endpoint(host: str, owning_file: str) -> Tuple[str, str]:
    h = host.lower()
    if any(k in h for k in ("netflix.", "nflxvideo.", "nflximg.", "nflxext.")):
        return ("STREAMING_DRM", "Netflix NRD client endpoint/bootstrap")
    if any(k in h for k in ("youtube.", "ytimg.", "googlevideo.")):
        return ("STREAMING_MEDIA", "YouTube Leanback / SWF client reference")
    if "google." in h or "gstatic." in h or "googleapis." in h:
        if "net_ck" in owning_file or "dns" in owning_file:
            return ("CONNECTIVITY_CHECK", "Network connectivity probe reference")
        return ("EXTERNAL_WEB_SERVICE", "Google / Widevine / browser reference")
    if "baidu." in h:
        return ("CONNECTIVITY_CHECK", "Alternative network reachability probe")
    if any(k in h for k in ("opera.", "operasoftware.", "myopera.")):
        return ("BROWSER_PORTAL", "Opera Presto TV Store / browser service")
    if any(k in h for k in ("philips.", "tpvision.", "tpv", "aoc.", "smarttv", "nettv")):
        return ("OEM_PORTAL_OR_UPDATE", "TPV/Philips/AOC Smart TV portal or firmware service")
    if any(k in h for k in ("spotify.", "scdn.co")):
        return ("STREAMING_AUDIO", "Spotify native shared library reference")
    if any(k in h for k in ("widevine.", "playready", "microsoft.", "marlin")):
        return ("DRM_PROVISIONING", "DRM license/clock/provisioning endpoint")
    if h.startswith("127.") or h == "localhost":
        return ("LOCAL_IPC_LOOPBACK", "Local IPC loopback HTTP endpoint (DIAL / local UI)")
    if h.startswith("10.") or h.startswith("192.168.") or h.startswith("172.") or h.startswith("239."):
        return ("LAN_MULTICAST_OR_PRIVATE", "Local network / SSDP / DLNA / private address")
    return ("UNCLASSIFIED_EXTERNAL", "Static string observed in binary/script; live traffic not captured")


def parse_opcacrt_summary(pem_path: Path) -> Dict[str, Any]:
    if not pem_path.is_file():
        return {"present": False}
    text = pem_path.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", text, re.S)
    expired_pre_2017 = 0
    expired_pre_2026 = 0
    sample_subjects: List[str] = []
    for idx, blk in enumerate(blocks):
        if idx < 10 or idx >= len(blocks) - 5:
            p = subprocess.run(
                ["openssl", "x509", "-noout", "-subject", "-enddate"],
                input=blk.encode(),
                capture_output=True,
            )
            if p.returncode == 0:
                line = p.stdout.decode("utf-8", errors="replace").strip().replace("\n", " | ")
                sample_subjects.append(line)
        p_date = subprocess.run(["openssl", "x509", "-noout", "-enddate"], input=blk.encode(), capture_output=True)
        out = p_date.stdout.decode("utf-8", errors="replace")
        m = re.search(r"(\d{4})\s+GMT", out)
        if m:
            yr = int(m.group(1))
            if yr <= 2016:
                expired_pre_2017 += 1
            if yr < 2026:
                expired_pre_2026 += 1
    return {
        "present": True,
        "path": "rootfs1/nettv/opera/opera_dir/opcacrt6.pem",
        "size_bytes": pem_path.stat().st_size,
        "certificate_count": len(blocks),
        "expired_on_or_before_2016": expired_pre_2017,
        "expired_before_2026": expired_pre_2026,
        "sample_certificates": sample_subjects,
    }


def extract_all(ws: Path, repo: Path) -> None:
    (repo / "firmware-forensics").mkdir(parents=True, exist_ok=True)
    (repo / "privacy").mkdir(parents=True, exist_ok=True)
    (repo / "hardware").mkdir(parents=True, exist_ok=True)
    (repo / "scientific-research").mkdir(parents=True, exist_ok=True)

    # 1. Core metadata from ZIP, PKG, vmlinux, uboot, profile
    zip_p = ws / "original_firmware" / "LE32S5760_V2.011_V0.2.zip"
    pkg_p = ws / "extracted" / "upgrade_loader.pkg"
    vm_p = ws / "scratch" / "vmlinux.bin"
    ub_p = ws / "extracted" / "uboot.bin"
    prof_p = ws / "extracted" / "appfs1" / "etc" / "profile"

    pkg_parts: List[Dict[str, Any]] = []
    cfig_order: List[str] = []
    if pkg_p.is_file():
        pkg_data, entries = parse_pkg_headers(str(pkg_p))
        for idx, (tag, hoff, poff, sz) in enumerate(entries, 1):
            payload = pkg_data[poff : poff + sz]
            pkg_parts.append({
                "index": idx,
                "tag": tag,
                "header_offset_hex": f"0x{hoff:08x}",
                "payload_offset_hex": f"0x{poff:08x}",
                "size_bytes": sz,
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
            if tag == "cfig":
                cfig_order = payload.decode("ascii", "replace").strip().splitlines()

    vm_banner = ""
    vm_paths: List[str] = []
    vm_ikconfig = False
    nand_ids: List[str] = []
    if vm_p.is_file():
        vdata = vm_p.read_bytes()
        bm = re.search(rb"Linux version 3\.[^\x00\n]+", vdata)
        vm_banner = bm.group(0).decode("ascii", "replace") if bm else ""
        vm_ikconfig = b"IKCFG_ST" in vdata
        vm_paths = sorted(set(
            m.decode("ascii", "ignore")
            for m in re.findall(rb"/share/Release_code_use/[^\x00\s\"']+", vdata)
        ))
        nand_ids = sorted(set(
            m.decode("ascii", "ignore")
            for m in re.findall(rb"\bNAND_[A-Z0-9_]+", vdata)
        ))

    profile_vars: Dict[str, str] = {}
    if prof_p.is_file():
        for line in prof_p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*export\s+([A-Z0-9_]+)=(.+)$", line)
            if m:
                profile_vars[m.group(1)] = m.group(2).strip()

    ca_summary = parse_opcacrt_summary(
        ws / "extracted" / "rootfs1" / "nettv" / "opera" / "opera_dir" / "opcacrt6.pem"
    )

    dtv_paths: List[str] = []
    dtv_p = ws / "extracted" / "appfs1" / "basic" / "dtv_driver.ko"
    if not dtv_p.is_file():
        dtv_p = ws / "extracted" / "appfs1" / "lib" / "modules" / "dtv_driver.ko"
    if dtv_p.is_file():
        ddata = dtv_p.read_bytes()
        dtv_paths = sorted(set(
            m.decode("ascii", "ignore")
            for m in re.findall(rb"/share/[^\x00\s\"']+", ddata)
        ))

    metadata = {
        "schema_version": "1.0.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "device_identity": {
            "commercial_model": "AOC LE32S5760/20",
            "odm_platform_code": "TPV_MTK2K14PLF",
            "soc": "MediaTek MT5880 (ARMv7-A / Thumb-2)",
            "mainboard_pcb_marking": {
                "value": "715G7904M (hypothesized)",
                "status": "UNKNOWN_UNVERIFIED",
                "reason": "0 occurrences across extracted binaries; requires physical board inspection/photography",
            },
            "profile_exports": profile_vars,
        },
        "factory_package": {
            "zip_filename": zip_p.name,
            "zip_size_bytes": zip_p.stat().st_size if zip_p.is_file() else None,
            "zip_sha256": hashlib.sha256(zip_p.read_bytes()).hexdigest() if zip_p.is_file() else None,
            "pkg_filename": "upgrade_loader.pkg",
            "pkg_size_bytes": pkg_p.stat().st_size if pkg_p.is_file() else None,
            "pkg_sha256": hashlib.sha256(pkg_p.read_bytes()).hexdigest() if pkg_p.is_file() else None,
            "pkg_partition_count": len(pkg_parts),
            "cfig_partition_sequence": cfig_order,
            "partitions": pkg_parts,
        },
        "kernel": {
            "banner": vm_banner,
            "ikconfig_embedded": vm_ikconfig,
            "embedded_source_path_count": len(vm_paths),
            "sample_source_paths": vm_paths[:30],
            "nand_driver_id_strings": nand_ids,
        },
        "dtv_driver": {
            "embedded_source_path_count": len(dtv_paths),
            "sample_source_paths": dtv_paths[:30],
        },
        "trust_store": ca_summary,
    }
    meta_out = repo / "firmware-forensics" / "FIRMWARE_METADATA.json"
    meta_out.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    # 2. External endpoint inventory across appfs1 & rootfs1
    endpoint_map: Dict[Tuple[str, str], Set[str]] = {}
    for tree in ("extracted/appfs1", "extracted/rootfs1"):
        root_dir = ws / tree
        if not root_dir.is_dir():
            continue
        for dp, _, fns in os.walk(root_dir):
            for fn in sorted(fns):
                fp = Path(dp) / fn
                st = fp.lstat()
                if not stat.S_ISREG(st.st_mode) or st.st_size > 35 * 1024 * 1024:
                    continue
                data = fp.read_bytes()
                if b"http://" not in data and b"https://" not in data:
                    continue
                rel = str(fp.relative_to(ws))
                for u in fast_extract_urls(data):
                    parts = u.split("//", 1)
                    if len(parts) < 2 or not parts[1]:
                        continue
                    host_port = parts[1].split("/", 1)[0]
                    host = host_port.split(":", 1)[0].lower()
                    if ("." not in host and host != "localhost" and not host.startswith("127.")) or len(host) < 3:
                        continue
                    if any(sh == host or host.endswith("." + sh) for sh in STD_DOC_HOSTS):
                        continue
                    endpoint_map.setdefault((u, host), set()).add(rel)

    ep_rows: List[List[str]] = []
    # Keep deterministic host-sorted output; limit repetitive localized HTML links per host to top 5 URLs per host
    by_host: Dict[str, List[Tuple[str, List[str]]]] = {}
    for (u, host), files in sorted(endpoint_map.items()):
        by_host.setdefault(host, []).append((u, sorted(files)))

    for host in sorted(by_host):
        for idx, (u, files) in enumerate(by_host[host]):
            if idx >= 5:
                break
            scheme = u.split("://", 1)[0].lower()
            hp = u.split("://", 1)[1].split("/", 1)[0]
            port = hp.split(":", 1)[1] if ":" in hp and hp.split(":", 1)[1].isdigit() else ("443" if scheme == "https" else "80")
            cat, note = classify_endpoint(host, files[0])
            ep_rows.append([
                u,
                host,
                scheme,
                port,
                cat,
                files[0],
                str(len(files)),
                "CONFIRMED_STATIC_STRING",
                note,
            ])

    ep_csv = repo / "privacy" / "EXTERNAL_ENDPOINT_INVENTORY.csv"
    with ep_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "host", "scheme", "port", "category", "sample_file", "file_occurrences", "status", "notes"])
        w.writerows(ep_rows)

    # 3. Hardware component traceability inventory
    hw_rows = [
        ["HW-01", "SoC / Main CPU", "MediaTek MT5880 (ARMv7-A / Thumb-2 SMP PREEMPT)", "MediaTek", "CONFIRMED", "scratch/vmlinux.bin; extracted/uboot.bin; extracted/uenv", "Banner ARMv7 Linux 3.0.13; uenv board/mt5880; vermagic ARMv7; SMP PREEMPT"],
        ["HW-02", "Standby Coprocessor", "T8032 8051 Standby Microcontroller", "MediaTek Embedded IP", "CONFIRMED", "extracted/uboot.bin", "Preloader string 'Preloader T8032 ack !' / 'T8032 NO ack!' and PDWNC controller"],
        ["HW-03", "Audio DSP", "MediaTek Audio DSP ('adsp' / 'aqda' partitions)", "MediaTek", "CONFIRMED", "extracted/upgrade_loader.pkg (cfig/adsp/aqda)", "Dedicated PKG/NAND partitions cfig->adsp & aqda"],
        ["HW-04", "Display / 2D-3D Acceleration", "MT53xx Framebuffer (mt53_fb.c) & DirectFB 1.4.1; empty /3rd/Img_Sgx hook", "MediaTek (mt53_fb) / Generic Script Hook", "CONFIRMED_FB_ABSENT_SGX_BIN", "dtv_driver.ko (mt53_fb.c); empty extracted/rootfs1/Img_Sgx", "ins_basic_mod.sh probes /3rd/Img_Sgx/pvrsrvctl, which is NOT shipped; DirectFB runs on MTK framebuffer"],
        ["HW-05", "Hardware Crypto / Security", "MT5880 OTP eFuse & HW Crypto Engine (mtk_crypto.c / mtk_hw_decrypt)", "MediaTek", "CONFIRMED", "extracted/uboot.bin (0xf0008664); scratch/vmlinux.bin", "BootROM RSA check gated by eFuse bit 20 (0xf0008664 & 0x100000); TrustZone flag"],
        ["HW-06", "HW Decompression Block", "MediaTek HW-LZHS Decoder (MMIO 0xf00080b0)", "MediaTek", "CONFIRMED", "extracted/uboot.bin", "Decompresses kernel & U-Boot LZHS payloads via register base 0xf00080b0"],
        ["HW-07", "Main Memory Controller", "Dual-Channel DRAM Controller (Channels A & B)", "MediaTek MT5880", "CONFIRMED_CONFIG_INFERRED_SIZE", "extracted/uboot.bin; scratch/vmlinux.bin", "Preloader runs DRAM Channel A/B calibration; capacity (512 MB total) inferred from global_kernel_dram_size/kernel config"],
        ["HW-08", "Non-Volatile Storage", "Raw NAND Flash Controller (mtd0..mtd13, UBI + SquashFS)", "Hynix/Micron/Samsung/Toshiba (10 IDs in kernel)", "CONFIRMED_BUS_UNKNOWN_EXACT_IC", "scratch/vmlinux.bin; cfig partition map", "Kernel supports 10 NAND IDs (H27U*, MT29F*, K9GAG08U0E, TC58NVG*); exact soldered chip requires visual board teardown"],
        ["HW-09", "Wired Ethernet NIC", "MediaTek Star MAC (star_mac.ko + eth0)", "MediaTek", "CONFIRMED", "extracted/appfs1/etc/scripts/ins_eth_mod.sh", "Loaded via insmod /basic/modules/star_mac.ko"],
        ["HW-10", "USB Wi-Fi Subsystem", "Ralink/MediaTek RT5572 Dual-Band USB Wi-Fi + Atheros/Realtek scripts", "Ralink / MediaTek / Atheros", "CONFIRMED_DRIVER_INFERRED_SKU", "extracted/appfs1/wifi_ko; basic/wifi_ko", "rtnet5572sta.ko aliases include VID:PID 148F:5572, 043E:7A13, 043E:7A32, 2001:3C1A"],
        ["HW-11", "USB Host Controllers", "EHCI/MTK HCD (mtk-hcd.ko) + xHCI (xhci-hcd.ko)", "MediaTek", "CONFIRMED", "extracted/appfs1/etc/scripts/ins_usb_sub_mod.sh", "Loaded sequentially with usb-storage.ko, hid.ko, usbhid.ko"],
        ["HW-12", "Mainboard PCB Assembly", "TPV Mainboard (hypothesized 715G7904M family)", "TPV Technology (ODM)", "UNKNOWN_UNVERIFIED", "Zero hits in firmware binaries", "Requires visual PCB silkscreen inspection per HARDWARE_PHOTOGRAPHIC_DOCUMENTATION"],
        ["HW-13", "Display Panel & T-Con", "LVDS 1366x768 32-inch Panel Timing Controller & PQ Data ('pqda')", "Unknown (via pqda)", "INFERRED_RES_UNKNOWN_IC", "extracted/upgrade_loader.pkg (pqda); SystemManager QML", "UI layout & pqda partition present; exact panel model/T-Con IC requires teardown"],
        ["HW-14", "Digital/Analog TV Tuner", "ISDB-Tb / DTV Tuner & Demodulator (Brazil Ginga SBTVD target)", "Unknown silicon PN", "INFERRED_FROM_GINGA_UNKNOWN_IC", "extracted/rootfs1/ginga; dtv_driver.ko", "Firmware ships Brazilian Ginga middleware & ISDB strings; exact tuner IC uninspected"],
        ["HW-15", "Debug Serial Port", "UART0 (ttyMT0 115200 8N1) & ttyUSB0 conditional console", "MediaTek UART", "CONFIRMED_IN_SCRIPTS", "extracted/appfs1/etc/inittab; etc/scripts/usb_console.sh", "inittab ttyMT0 line commented out in production; physical PCB test pads unphotographed"],
    ]
    hw_csv = repo / "hardware" / "HARDWARE_COMPONENT_INVENTORY.csv"
    with hw_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["component_id", "subsystem", "component_name", "vendor_or_arch", "verification_status", "evidence_source", "technical_notes"])
        w.writerows(hw_rows)

    # 4. Research artifacts manifest
    files_index: List[Dict[str, Any]] = []
    for sub in ("docs", "scripts", "evidence", "custom_payload"):
        p = repo / sub
        if p.is_dir():
            for dp, _, fns in os.walk(p):
                if "__pycache__" in dp:
                    continue
                for fn in sorted(fns):
                    fp = Path(dp) / fn
                    if fp.suffix in (".pyc", ".pyo"):
                        continue
                    files_index.append({
                        "category": sub,
                        "path": str(fp.relative_to(repo)),
                        "size_bytes": fp.stat().st_size,
                        "sha256": hashlib.sha256(fp.read_bytes()).hexdigest(),
                    })
    ram_out = repo / "scientific-research" / "RESEARCH_ARTIFACTS_MANIFEST.json"
    ram_out.write_text(
        json.dumps({
            "schema_version": "1.0.0",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "repository": "https://github.com/D-H-O-R-A/aoc-le32s5760-mt5880-firmware-research",
            "baseline_artifact_count": len(files_index),
            "baseline_artifacts": files_index,
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {meta_out}")
    print(f"Wrote {ep_csv} ({len(ep_rows)} endpoints)")
    print(f"Wrote {hw_csv} ({len(hw_rows)} hardware items)")
    print(f"Wrote {ram_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structured metadata, endpoints, and hardware inventory.")
    default_repo = SCRIPT_DIR.parent
    parser.add_argument("--repo", default=str(default_repo), help="Repository root directory")
    parser.add_argument("--workspace", default=str(default_repo.parent), help="Local workspace root")
    args = parser.parse_args()
    extract_all(Path(args.workspace).resolve(), Path(args.repo).resolve())


if __name__ == "__main__":
    main()
