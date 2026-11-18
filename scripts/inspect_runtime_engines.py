#!/usr/bin/env python3
"""
Audits stock TV userland runtime versions, library dependencies, SystemManager SMConfig
behavior, BusyBox applets, and custom QML/JS/shell payload compliance.
"""

import argparse
import glob
import os
import re
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit runtime engines, BusyBox applets, and custom payload")
    parser.add_argument("--workspace", required=True, help="Path to AOC/LE32S5760 base workspace")
    parser.add_argument("--repo", required=True, help="Path to research repository root")
    args = parser.parse_args()

    ws = args.workspace
    repo = args.repo

    print("=== 1. Proprietary App Engine Fingerprints ===")
    checks = [
        ("Opera TV (libopera_hbbtv.so)", os.path.join(ws, "extracted/rootfs1/nettv/libopera_hbbtv.so"),
         [b"Opera/9.80", b"20140526", b"Enable TLS v1.1", b"Enable TLS v1.2", b"User JavaScript File"]),
        ("Netflix (nrd-app/netflix)", os.path.join(ws, "extracted/rootfs1/netflix/nrd-app/netflix"),
         [b"OpenSSL 1.0.", b"20150420", b"Gibbon"]),
        ("NetTV Launcher (libnettv.so)", os.path.join(ws, "extracted/rootfs1/nettv/libnettv.so"),
         [b"/3rd_rw/nettv/opera_new.ini", b"cp -f /3rd_rw/nettv/opera_new.ini"]),
        ("Service Init (dtv_svc)", os.path.join(ws, "extracted/appfs1/basic/dtv_svc"),
         [b"/3rd_rw/upgrade/customer_version", b"cp -rf /3rd/nettv/opera/* /3rd_rw/nettv/opera"]),
    ]
    for label, path, pats in checks:
        data = open(path, "rb").read()
        print(f"  [{label}] ({len(data)} bytes):")
        for pat in pats:
            hits = sorted(set(s.decode("latin1", "ignore") for s in re.findall(re.escape(pat) + rb"[ -~]{0,50}", data)))
            print(f"    {pat.decode()} -> {hits[:3]}")

    print("\n=== 2. BusyBox Applet & Binary Inventory (extracted/appfs1/bin) ===")
    bins = sorted(os.listdir(os.path.join(ws, "extracted/appfs1/bin")))
    print("  Count:", len(bins), "Tools:", ", ".join(bins))
    for missing in ["pidof", "pgrep", "renice", "ionice", "chown", "killall", "unzip", "python", "python3", "curl"]:
        print(f"  Check missing {missing:<10}: present={missing in bins}")

    print("\n=== 3. SystemManager ELF NEEDED & SMConfig Keys ===")
    sm = os.path.join(ws, "extracted/rootfs1/qt/AEDK/SystemManager/SystemManager")
    sm_bytes = open(sm, "rb").read()
    for key in [b"sm_config.ini", b"tpvlib", b"dynqml", b"qrc:/HomeScreen/HSMain.qml", b"res/HomeScreen/HSMain.qml"]:
        idx = sm_bytes.find(key)
        print(f"  SM string {key.decode()!r:<30} @ 0x{idx:06x}")

    print("\n=== 4. Custom Payload Validation ===")
    run_sh = os.path.join(repo, "custom_payload/patches/run.sh")
    subprocess.check_call(["sh", "-n", run_sh])
    run_code = "\n".join(l for l in open(run_sh).read().splitlines() if not l.lstrip().startswith("#"))
    for bad_cmd in ["pidof", "pgrep", "renice", "ionice", "chown", "killall", "unzip"]:
        assert not re.search(rf"\b{bad_cmd}\b", run_code), f"Invalid command {bad_cmd}"
    print(f"  [PASS] {os.path.relpath(run_sh, repo)}: sh -n + BusyBox applet compliance")

    user_js = os.path.join(repo, "custom_payload/nettv/user.js")
    subprocess.check_call(["node", "--check", user_js])
    print(f"  [PASS] {os.path.relpath(user_js, repo)}: node --check passed")

    qmls = sorted(glob.glob(os.path.join(repo, "custom_payload/qml_HomeScreen/**/*.qml"), recursive=True))
    for q in qmls:
        txt = open(q, encoding="utf-8").read()
        for i, l in enumerate(txt.splitlines(), 1):
            assert all(ord(c) <= 0xff for c in l), f"Non-Latin1 in {q}:{i}"
            assert "127.0.0.1" not in l and "8888" not in l and "TLS 1.3" not in l
        assert txt.count("{") == txt.count("}")
    print(f"  [PASS] {len(qmls)} custom QML files validated (Latin-1/ASCII safe, balanced braces)")


if __name__ == "__main__":
    main()
