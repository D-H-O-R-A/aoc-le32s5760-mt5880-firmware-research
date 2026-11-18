#!/usr/bin/env python3
"""
Generates standards-compliant Software Bill of Materials (SBOM) files from real
target binaries observed in extracted/appfs1 and extracted/rootfs1:
  - sbom/SBOM.spdx.json  (SPDX 2.3 JSON)
  - sbom/SBOM.cdx.json   (CycloneDX 1.5 JSON)
"""

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# Component definitions mapped strictly to observed files on disk in extracted/appfs1 & extracted/rootfs1
COMPONENTS: List[Dict[str, Any]] = [
    {
        "id": "linux-kernel",
        "name": "linux-kernel-mt5880",
        "version": "3.0.13",
        "license": "GPL-2.0-only",
        "supplier": "MediaTek / TPV Technology (Linux Foundation upstream)",
        "rel_path": "scratch/vmlinux.bin",
        "cpe": "cpe:2.3:o:linux:linux_kernel:3.0.13:*:*:*:*:*:*:*",
        "purl": "pkg:generic/linux@3.0.13?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Kernel banner: Linux version 3.0.13 (roylo@TWCLS066) (gcc 4.5.1) Thu Aug 4 2016",
    },
    {
        "id": "glibc",
        "name": "glibc",
        "version": "2.12.2",
        "license": "LGPL-2.1-or-later",
        "supplier": "Free Software Foundation (GNU Project)",
        "rel_path": "extracted/appfs1/lib/libc-2.12.2.so",
        "cpe": "cpe:2.3:a:gnu:glibc:2.12.2:*:*:*:*:*:*:*",
        "purl": "pkg:generic/glibc@2.12.2?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "SONAME libc-2.12.2.so & string 'GNU C Library stable release version 2.12.2'",
    },
    {
        "id": "busybox",
        "name": "busybox",
        "version": "1.15.3",
        "license": "GPL-2.0-only",
        "supplier": "BusyBox Project",
        "rel_path": "extracted/appfs1/bin/busybox",
        "cpe": "cpe:2.3:a:busybox:busybox:1.15.3:*:*:*:*:*:*:*",
        "purl": "pkg:generic/busybox@1.15.3?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Binary string 'BusyBox v1.15.3 (2012-06-06 18:54:15 CST)'",
    },
    {
        "id": "openssl",
        "name": "openssl",
        "version": "1.0.0d",
        "license": "OpenSSL",
        "supplier": "OpenSSL Software Foundation",
        "rel_path": "extracted/appfs1/basic/lib/libssl.so.1.0.0",
        "cpe": "cpe:2.3:a:openssl:openssl:1.0.0d:*:*:*:*:*:*:*",
        "purl": "pkg:generic/openssl@1.0.0d?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "libssl.so.1.0.0 & libcurl RPATH/build path openssl-1.0.0d",
    },
    {
        "id": "libcurl",
        "name": "curl",
        "version": "7.21.7",
        "license": "curl",
        "supplier": "Daniel Stenberg / curl project",
        "rel_path": "extracted/rootfs1/ginga/lib/libcurl.so.4.2.0",
        "cpe": "cpe:2.3:a:haxx:libcurl:7.21.7:*:*:*:*:*:*:*",
        "purl": "pkg:generic/curl@7.21.7?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Embedded string 'libcurl/7.21.7' and build path curl-7.21.7",
    },
    {
        "id": "libxml2",
        "name": "libxml2",
        "version": "2.7.8",
        "license": "MIT",
        "supplier": "GNOME / Daniel Veillard",
        "rel_path": "extracted/rootfs1/lib/libxml2.so.2.7.8",
        "cpe": "cpe:2.3:a:xmlsoft:libxml2:2.7.8:*:*:*:*:*:*:*",
        "purl": "pkg:generic/libxml2@2.7.8?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library filename libxml2.so.2.7.8",
    },
    {
        "id": "expat",
        "name": "expat",
        "version": "2.0.1",
        "license": "MIT",
        "supplier": "Expat Project",
        "rel_path": "extracted/appfs1/basic/lib/libexpat.so.1.5.2",
        "cpe": "cpe:2.3:a:libexpat:expat:2.0.1:*:*:*:*:*:*:*",
        "purl": "pkg:generic/expat@2.0.1?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Embedded version string 'expat_2.0.1'",
    },
    {
        "id": "zlib",
        "name": "zlib",
        "version": "1.2.3",
        "license": "Zlib",
        "supplier": "Jean-loup Gailly & Mark Adler",
        "rel_path": "extracted/appfs1/lib/libz.so.1.2.3",
        "cpe": "cpe:2.3:a:zlib:zlib:1.2.3:*:*:*:*:*:*:*",
        "purl": "pkg:generic/zlib@1.2.3?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library filename libz.so.1.2.3",
    },
    {
        "id": "libpng",
        "name": "libpng",
        "version": "1.2.43",
        "license": "Libpng",
        "supplier": "PNG Development Group",
        "rel_path": "extracted/appfs1/lib/libpng12.so.0.1.2.43",
        "cpe": "cpe:2.3:a:libpng:libpng:1.2.43:*:*:*:*:*:*:*",
        "purl": "pkg:generic/libpng@1.2.43?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "String 'libpng version 1.2.43 - February 25, 2010'",
    },
    {
        "id": "sqlite",
        "name": "sqlite",
        "version": "3.7.2",
        "license": "blessing",
        "supplier": "SQLite Consortium",
        "rel_path": "extracted/appfs1/basic/lib/libsqlite_3_7_2.so",
        "cpe": "cpe:2.3:a:sqlite:sqlite:3.7.2:*:*:*:*:*:*:*",
        "purl": "pkg:generic/sqlite@3.7.2?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library filename libsqlite_3_7_2.so",
    },
    {
        "id": "qt4",
        "name": "qt-everywhere",
        "version": "4.8.3",
        "license": "LGPL-2.1-only",
        "supplier": "Nokia / Qt Project",
        "rel_path": "extracted/rootfs1/qt/lib/libQtCore.so.4.8.3",
        "cpe": "cpe:2.3:a:qt:qt:4.8.3:*:*:*:*:*:*:*",
        "purl": "pkg:generic/qt@4.8.3?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "QtCore/QtDeclarative/QtGui/QtNetwork/QtScript 4.8.3 shared libraries",
    },
    {
        "id": "alsa-lib",
        "name": "alsa-lib",
        "version": "1.0.24.1",
        "license": "LGPL-2.1-or-later",
        "supplier": "ALSA Project",
        "rel_path": "extracted/appfs1/basic/lib/libasound.so.2.0.0",
        "cpe": "cpe:2.3:a:alsa-project:alsa-lib:1.0.24.1:*:*:*:*:*:*:*",
        "purl": "pkg:generic/alsa-lib@1.0.24.1?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Path alsa-lib-1.0.24.1/lib/libasound.so.2.0.0",
    },
    {
        "id": "fuse",
        "name": "libfuse",
        "version": "2.8.4",
        "license": "LGPL-2.1-only",
        "supplier": "FUSE Project",
        "rel_path": "extracted/appfs1/basic/lib/libfuse.so.2.8.4",
        "cpe": "",
        "purl": "pkg:generic/libfuse@2.8.4?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library filename libfuse.so.2.8.4",
    },
    {
        "id": "ntfs-3g",
        "name": "ntfs-3g",
        "version": "2010.x-abi76",
        "license": "GPL-2.0-or-later",
        "supplier": "Tuxera / NTFS-3G",
        "rel_path": "extracted/appfs1/basic/lib/libntfs-3g.so.76.0.0",
        "cpe": "",
        "purl": "pkg:generic/ntfs-3g@76.0.0?arch=armv7",
        "status": "INFERRED_SONAME",
        "evidence": "SONAME libntfs-3g.so.76.0.0 (upstream release date inferred from ABI 76)",
    },
    {
        "id": "boost",
        "name": "boost",
        "version": "1.44.0",
        "license": "BSL-1.0",
        "supplier": "Boost C++ Libraries",
        "rel_path": "extracted/rootfs1/ginga/lib/libboost_filesystem.so.1.44.0",
        "cpe": "cpe:2.3:a:boost:boost:1.44.0:*:*:*:*:*:*:*",
        "purl": "pkg:generic/boost@1.44.0?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libboost_*.so.1.44.0 under rootfs1/ginga/lib",
    },
    {
        "id": "xerces-c",
        "name": "xerces-c",
        "version": "3.1",
        "license": "Apache-2.0",
        "supplier": "Apache Software Foundation",
        "rel_path": "extracted/rootfs1/lib/libxerces-c-3.1.so",
        "cpe": "cpe:2.3:a:apache:xerces-c\\+\\+:3.1:*:*:*:*:*:*:*",
        "purl": "pkg:generic/xerces-c@3.1?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libxerces-c-3.1.so",
    },
    {
        "id": "freetype",
        "name": "freetype",
        "version": "2.4.x-so6.6.1",
        "license": "FTL OR GPL-2.0-or-later",
        "supplier": "FreeType Project",
        "rel_path": "extracted/appfs1/lib/libfreetype.so.6.6.1",
        "cpe": "",
        "purl": "pkg:generic/freetype@6.6.1?arch=armv7",
        "status": "INFERRED_SONAME",
        "evidence": "Shared library libfreetype.so.6.6.1 (rootfs1/ginga ships 6.6.2)",
    },
    {
        "id": "libjpeg",
        "name": "libjpeg",
        "version": "6b-so62",
        "license": "IJG",
        "supplier": "Independent JPEG Group",
        "rel_path": "extracted/appfs1/lib/libjpeg.so.62.0.0",
        "cpe": "",
        "purl": "pkg:generic/libjpeg@62.0.0?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libjpeg.so.62.0.0",
    },
    {
        "id": "libiconv",
        "name": "libiconv",
        "version": "1.13-so2.4.0",
        "license": "LGPL-2.0-or-later",
        "supplier": "GNU Project",
        "rel_path": "extracted/rootfs1/lib/libiconv.so.2.4.0",
        "cpe": "",
        "purl": "pkg:generic/libiconv@2.4.0?arch=armv7",
        "status": "INFERRED_SONAME",
        "evidence": "Shared library libiconv.so.2.4.0 (ginga ships 2.5.0)",
    },
    {
        "id": "lvm2-devmapper",
        "name": "device-mapper",
        "version": "1.02",
        "license": "LGPL-2.1-only",
        "supplier": "Red Hat / LVM2",
        "rel_path": "extracted/appfs1/lib/libdevmapper.so.1.02",
        "cpe": "",
        "purl": "pkg:generic/device-mapper@1.02?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libdevmapper.so.1.02 for dm-verity/dmsetup",
    },
    {
        "id": "c-ares",
        "name": "c-ares",
        "version": "1.7.x-so2.0.0",
        "license": "MIT",
        "supplier": "c-ares Project",
        "rel_path": "extracted/appfs1/basic/lib/libcares.so.2.0.0",
        "cpe": "",
        "purl": "pkg:generic/c-ares@2.0.0?arch=armv7",
        "status": "INFERRED_SONAME",
        "evidence": "Shared library libcares.so.2.0.0",
    },
    {
        "id": "libmicrohttpd",
        "name": "libmicrohttpd",
        "version": "so10",
        "license": "LGPL-2.1-or-later",
        "supplier": "GNU Project",
        "rel_path": "extracted/rootfs1/lib/libmicrohttpd.so.10",
        "cpe": "",
        "purl": "pkg:generic/libmicrohttpd@10?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libmicrohttpd.so.10",
    },
    {
        "id": "libwebp",
        "name": "libwebp",
        "version": "so4.0.1",
        "license": "BSD-3-Clause",
        "supplier": "Google Inc.",
        "rel_path": "extracted/appfs1/basic/lib/libwebp.so.4.0.1",
        "cpe": "",
        "purl": "pkg:generic/libwebp@4.0.1?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "Shared library libwebp.so.4.0.1",
    },
    {
        "id": "directfb",
        "name": "DirectFB",
        "version": "1.4.1",
        "license": "LGPL-2.1-or-later",
        "supplier": "DirectFB / MediaTek",
        "rel_path": "extracted/appfs1/lib/libdirectfb.so",
        "cpe": "",
        "purl": "pkg:generic/directfb@1.4.1?arch=armv7",
        "status": "CONFIRMED",
        "evidence": "libdirectfb.so / libdirectfb-1.4.so.0 strings",
    },
    {
        "id": "opera-presto",
        "name": "opera-devices-sdk-presto",
        "version": "Presto-6213",
        "license": "NOASSERTION",
        "supplier": "Opera Software ASA",
        "rel_path": "extracted/rootfs1/nettv/opera/opera",
        "cpe": "",
        "purl": "",
        "status": "CONFIRMED",
        "evidence": "Opera Presto binary & User-Agent core 6213",
    },
    {
        "id": "netflix-nrd",
        "name": "netflix-ready-device-sdk",
        "version": "NRD-2015-legacy",
        "license": "NOASSERTION",
        "supplier": "Netflix Inc.",
        "rel_path": "extracted/rootfs1/netflix/nrd-app/bin/nrd-app",
        "cpe": "",
        "purl": "",
        "status": "CONFIRMED",
        "evidence": "nrd-app ELF binary and JavaScriptCore runtime under rootfs1/netflix",
    },
]


def file_sha256_and_size(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return {"sha256": h.hexdigest(), "size": path.stat().st_size}


def build_sboms(ws: Path, repo: Path) -> None:
    sbom_dir = repo / "sbom"
    sbom_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Resolve real hashes when workspace exists; preserve already-recorded hashes in existing SBOM if offline
    existing_hashes: Dict[str, str] = {}
    cdx_path = sbom_dir / "SBOM.cdx.json"
    if cdx_path.is_file():
        try:
            old = json.loads(cdx_path.read_text(encoding="utf-8"))
            for c in old.get("components", []):
                for hs in c.get("hashes", []):
                    if hs.get("alg") == "SHA-256":
                        existing_hashes[c["name"]] = hs["content"]
        except Exception:
            pass

    spdx_packages: List[Dict[str, Any]] = [
        {
            "name": "AOC-LE32S5760-MT5880-Firmware",
            "SPDXID": "SPDXRef-RootFirmware",
            "versionInfo": "V2.011_V0.2",
            "supplier": "Organization: TPV Technology / AOC",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "summary": "Official firmware image LE32S5760_V2.011_V0.2 (TPV MTK2K14PLF / MediaTek MT5880).",
        }
    ]
    spdx_rels: List[Dict[str, str]] = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-RootFirmware",
        }
    ]

    cdx_components: List[Dict[str, Any]] = []

    for comp in COMPONENTS:
        info = file_sha256_and_size(ws / comp["rel_path"])
        sha = info["sha256"] if info else existing_hashes.get(comp["name"], "")
        spdx_id = f"SPDXRef-pkg-{comp['id']}"

        pkg_obj: Dict[str, Any] = {
            "name": comp["name"],
            "SPDXID": spdx_id,
            "versionInfo": comp["version"],
            "supplier": f"Organization: {comp['supplier']}",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": comp["license"],
            "licenseDeclared": comp["license"],
            "comment": f"Status={comp['status']}; Evidence={comp['evidence']}; Path={comp['rel_path']}",
        }
        if sha:
            pkg_obj["checksums"] = [{"algorithm": "SHA256", "checksumValue": sha}]
        ext_refs = []
        if comp["cpe"]:
            ext_refs.append({"referenceCategory": "SECURITY", "referenceType": "cpe23Type", "referenceLocator": comp["cpe"]})
        if comp["purl"]:
            ext_refs.append({"referenceCategory": "PACKAGE-MANAGER", "referenceType": "purl", "referenceLocator": comp["purl"]})
        if ext_refs:
            pkg_obj["externalRefs"] = ext_refs

        spdx_packages.append(pkg_obj)
        spdx_rels.append({
            "spdxElementId": "SPDXRef-RootFirmware",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": spdx_id,
        })

        cdx_comp: Dict[str, Any] = {
            "type": "operating-system" if comp["id"] == "linux-kernel" else ("application" if comp["id"] in ("busybox", "opera-presto", "netflix-nrd") else "library"),
            "bom-ref": comp["id"],
            "name": comp["name"],
            "version": comp["version"],
            "supplier": {"name": comp["supplier"]},
            "properties": [
                {"name": "firmware:relativePath", "value": comp["rel_path"]},
                {"name": "firmware:verificationStatus", "value": comp["status"]},
                {"name": "firmware:evidence", "value": comp["evidence"]},
            ],
        }
        if sha:
            cdx_comp["hashes"] = [{"alg": "SHA-256", "content": sha}]
        if comp["cpe"]:
            cdx_comp["cpe"] = comp["cpe"]
        if comp["purl"]:
            cdx_comp["purl"] = comp["purl"]
        if comp["license"] != "NOASSERTION":
            cdx_comp["licenses"] = [{"license": {"id": comp["license"]}}] if " " not in comp["license"] and "-so" not in comp["license"] and comp["license"] in (
                "GPL-2.0-only", "LGPL-2.1-or-later", "OpenSSL", "curl", "MIT", "Zlib", "Libpng", "LGPL-2.1-only", "GPL-2.0-or-later", "BSL-1.0", "Apache-2.0", "BSD-3-Clause", "LGPL-2.0-or-later"
            ) else [{"license": {"name": comp["license"]}}]
        cdx_components.append(cdx_comp)

    spdx_doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "AOC-LE32S5760-MT5880-Firmware-SBOM",
        "documentNamespace": f"https://github.com/D-H-O-R-A/aoc-le32s5760-mt5880-firmware-research/spdx/{uuid.uuid5(uuid.NAMESPACE_URL, 'LE32S5760_V2.011_V0.2')}",
        "creationInfo": {
            "created": ts,
            "creators": [
                "Tool: aoc-le32s5760-sbom_generation.py-1.0",
                "Organization: D-H-O-R-A Firmware Research",
            ],
        },
        "packages": spdx_packages,
        "relationships": spdx_rels,
    }

    cdx_doc = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'cdx-LE32S5760_V2.011_V0.2')}",
        "version": 1,
        "metadata": {
            "timestamp": ts,
            "tools": [{"vendor": "D-H-O-R-A", "name": "sbom_generation.py", "version": "1.0.0"}],
            "component": {
                "type": "firmware",
                "bom-ref": "AOC-LE32S5760-V2.011_V0.2",
                "name": "AOC LE32S5760/20 Smart TV Firmware",
                "version": "V2.011_V0.2",
            },
        },
        "components": cdx_components,
    }

    spdx_path = sbom_dir / "SBOM.spdx.json"
    spdx_path.write_text(json.dumps(spdx_doc, indent=2) + "\n", encoding="utf-8")
    cdx_path.write_text(json.dumps(cdx_doc, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {spdx_path} ({len(spdx_packages)} packages)")
    print(f"Wrote {cdx_path} ({len(cdx_components)} components)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SPDX-2.3 and CycloneDX-1.5 SBOM files.")
    default_repo = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo", default=str(default_repo), help="Repository root directory")
    parser.add_argument("--workspace", default=str(default_repo.parent), help="Local workspace root")
    args = parser.parse_args()
    build_sboms(Path(args.workspace).resolve(), Path(args.repo).resolve())


if __name__ == "__main__":
    main()
