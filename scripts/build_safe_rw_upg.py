#!/usr/bin/env python3
"""
Clean parameterizable builder for safe /3rd_rw/nettv Autorun.upg payloads.
Does not hardcode or bundle vendor private signing keys; requires explicit paths via CLI.
"""

import argparse
import hashlib
import io
import os
import shutil
import struct
import subprocess
import tarfile
import tempfile


MTK_INTERNAL_KEY = bytes.fromhex("09291094" * 4)
ZERO_IV = b"\x00" * 16
APPEND_MAGIC = b"reserved mtk inc"


def aes_128_cbc_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        in_p, out_p = os.path.join(td, "in.bin"), os.path.join(td, "out.bin")
        open(in_p, "wb").write(data)
        subprocess.check_call(
            ["openssl", "enc", "-e", "-aes-128-cbc", "-nopad", "-K", key.hex(), "-iv", iv.hex(), "-in", in_p, "-out", out_p],
            stderr=subprocess.DEVNULL,
        )
        return open(out_p, "rb").read()


def rsa_sign_raw_sha256(digest32: bytes, priv_pem: str) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        in_p, out_p = os.path.join(td, "h.bin"), os.path.join(td, "s.bin")
        open(in_p, "wb").write(digest32)
        subprocess.check_call(["openssl", "pkeyutl", "-sign", "-inkey", priv_pem, "-in", in_p, "-out", out_p], stderr=subprocess.DEVNULL)
        return open(out_p, "rb").read()


def pack_chunk(tag4: bytes, payload: bytes, prod_key_md5: bytes, prod_iv_md5: bytes) -> bytes:
    enc_magic = aes_128_cbc_encrypt(APPEND_MAGIC, prod_key_md5, prod_iv_md5)
    enc_sha = aes_128_cbc_encrypt(hashlib.sha256(payload).digest(), prod_key_md5, prod_iv_md5)
    return tag4 + struct.pack("<II", 0, len(payload)) + enc_magic + enc_sha + payload


def build_tarball(nettv_dir: str, stock_userjs_dir: str | None) -> bytes:
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "browser"), exist_ok=True)
        os.makedirs(os.path.join(root, "download"), exist_ok=True)
        os.makedirs(os.path.join(root, "custom", "userjs"), exist_ok=True)
        shutil.copy2(os.path.join(nettv_dir, "opera_new.ini"), os.path.join(root, "opera_new.ini"))
        shutil.copy2(os.path.join(nettv_dir, "urlfilter.ini"), os.path.join(root, "custom", "urlfilter.ini"))
        shutil.copy2(os.path.join(nettv_dir, "user.css"), os.path.join(root, "custom", "user.css"))
        if stock_userjs_dir and os.path.isdir(stock_userjs_dir):
            for fn in sorted(os.listdir(stock_userjs_dir)):
                src = os.path.join(stock_userjs_dir, fn)
                if os.path.isfile(src) and fn != "user.js":
                    shutil.copy2(src, os.path.join(root, "custom", "userjs", fn))
        shutil.copy2(os.path.join(nettv_dir, "user.js"), os.path.join(root, "custom", "userjs", "user.js"))

        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tf:
            def _norm(ti: tarfile.TarInfo) -> tarfile.TarInfo:
                ti.uid = ti.gid = 0
                ti.uname = ti.gname = "root"
                ti.mtime = 1700000000
                ti.mode = 0o755 if ti.isdir() else 0o644
                return ti
            for rel in ["opera_new.ini", "browser", "download", "custom"]:
                tf.add(os.path.join(root, rel), arcname=rel, filter=_norm)
        return buf.getvalue()


def main() -> None:
    p = argparse.ArgumentParser(description="Build brick-safe /3rd_rw/nettv Autorun.upg")
    p.add_argument("--payload-dir", required=True, help="Directory with opera_new.ini, urlfilter.ini, user.css, user.js")
    p.add_argument("--stock-userjs", default=None, help="Optional stock userjs directory to preserve TV helpers")
    p.add_argument("--privkey", required=True, help="Signing RSA-2048 private PEM")
    p.add_argument("--aes-key", required=True, help="AES key file (33 bytes raw)")
    p.add_argument("--aes-iv", required=True, help="AES IV file (33 bytes raw)")
    p.add_argument("--out", required=True, help="Output Autorun.upg path")
    args = p.parse_args()

    prod_key_md5 = hashlib.md5(open(args.aes_key, "rb").read()).digest()
    prod_iv_md5 = hashlib.md5(open(args.aes_iv, "rb").read()).digest()
    tgz = build_tarball(args.payload_dir, args.stock_userjs)
    xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<UPGRADE>\n'
        b'  <SYS_INFO>\n'
        b'    <MANUFACTURER>TPV</MANUFACTURER>\n'
        b'    <MODEL>LE32S5760/20</MODEL>\n'
        b'    <SERIAL_NUM>000000</SERIAL_NUM>\n'
        b'    <MODE>UPG</MODE>\n'
        b'    <VERSION>002.001.205.146</VERSION>\n'
        b'  </SYS_INFO>\n'
        b'  <SW>\n'
        b'    <TAG>smth</TAG>\n'
        b'    <METHOD>FILE</METHOD>\n'
        b'    <PATH>/3rd_rw/nettv</PATH>\n'
        b'    <FILE_NAME>smth</FILE_NAME>\n'
        b'    <VERSION>002.001.205.146</VERSION>\n'
        b'    <ENABLE>YES</ENABLE>\n'
        b'  </SW>\n'
        b'</UPGRADE>\n'
    )
    chunks = pack_chunk(b"ixml", xml, prod_key_md5, prod_iv_md5) + pack_chunk(b"smth", tgz, prod_key_md5, prod_iv_md5)
    hdr = bytearray(0x70)
    hdr[0:4] = b"TPV\x00"
    hdr[4:12] = b"#DH@FiRm"
    hdr[12:44] = b"IDTV0801_002224_9_001_23_001_225"
    struct.pack_into("<II", hdr, 0x48, 0x90 + len(chunks), 0)
    hdr[0x50:0x5c] = b"LE32S5760/20"
    enc_hdr = aes_128_cbc_encrypt(bytes(hdr), MTK_INTERNAL_KEY, ZERO_IV)
    md5_dig = hashlib.md5(enc_hdr + b"\x00" * 32 + chunks).digest()
    enc_md5 = aes_128_cbc_encrypt(md5_dig + b"\x00" * 16, MTK_INTERNAL_KEY, ZERO_IV)
    signed = enc_hdr + enc_md5 + chunks
    sig = rsa_sign_raw_sha256(hashlib.sha256(signed).digest(), args.privkey)
    open(args.out, "wb").write(b"Autorun.upg".ljust(0x80, b"\x00") + signed + sig)
    print(f"Built {args.out}: {0x80 + len(signed) + len(sig)} bytes")


if __name__ == "__main__":
    main()
