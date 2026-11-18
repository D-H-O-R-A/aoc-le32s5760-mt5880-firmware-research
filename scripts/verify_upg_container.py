#!/usr/bin/env python3
"""
Standalone offline verifier for Philips/TPV MTK2K14PLF Autorun.upg containers.
Takes --upg plus public verification materials (PubKey_Prod.pem and TV ro_data AES files).
Never embeds or requires any private signing keys.
"""

import argparse
import hashlib
import io
import os
import struct
import subprocess
import tarfile
import tempfile
import xml.etree.ElementTree as ET


MTK_INTERNAL_KEY = bytes.fromhex("09291094" * 4)
ZERO_IV = b"\x00" * 16
APPEND_MAGIC = b"reserved mtk inc"


def aes_128_cbc_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        in_p = os.path.join(td, "in.bin")
        out_p = os.path.join(td, "out.bin")
        with open(in_p, "wb") as f:
            f.write(data)
        subprocess.check_call(
            ["openssl", "enc", "-d", "-aes-128-cbc", "-nopad", "-K", key.hex(), "-iv", iv.hex(), "-in", in_p, "-out", out_p],
            stderr=subprocess.DEVNULL,
        )
        return open(out_p, "rb").read()


def verify_container(upg_path: str, pub_pem: str, aes_key_path: str, aes_iv_path: str) -> None:
    data = open(upg_path, "rb").read()
    prod_key_md5 = hashlib.md5(open(aes_key_path, "rb").read()).digest()
    prod_iv_md5 = hashlib.md5(open(aes_iv_path, "rb").read()).digest()

    prefix = data[:0x80].split(b"\x00")[0].decode("ascii", "replace")
    print(f"File: {upg_path} ({len(data)} bytes)")
    print(f"  Outer 128B prefix: {prefix!r}")

    with tempfile.TemporaryDirectory() as td:
        sig_p = os.path.join(td, "sig.bin")
        with open(sig_p, "wb") as f:
            f.write(data[-256:])
        dec_sig = subprocess.check_output(
            ["openssl", "pkeyutl", "-verifyrecover", "-pubin", "-inkey", pub_pem, "-in", sig_p],
            stderr=subprocess.DEVNULL,
        )
    exp_sha = hashlib.sha256(data[0x80:-256]).digest()
    assert dec_sig == exp_sha, "RSA-2048 signature mismatch"
    print(f"  [PASS] RSA-2048 PKCS#1 v1.5 signature matches SHA256(data[0x80:-256]) = {exp_sha.hex()}")

    hdr = aes_128_cbc_decrypt(data[0x80:0xF0], MTK_INTERNAL_KEY, ZERO_IV)
    vendor = hdr[0x00:0x04].split(b"\x00")[0].decode("ascii", "replace")
    magic = hdr[0x04:0x0c]
    prod_str = hdr[0x0c:0x48].split(b"\x00")[0].decode("ascii", "replace")
    claimed_len, flags = struct.unpack_from("<II", hdr, 0x48)
    model = hdr[0x50:0x70].split(b"\x00")[0].decode("ascii", "replace")
    assert magic == b"#DH@FiRm", f"Unexpected DLM magic: {magic!r}"
    assert claimed_len == len(data) - 0x80 - 256, f"Length mismatch: {claimed_len}"
    print(f"  [PASS] DLM Header AES-128-CBC (09291094*4): vendor={vendor!r}, magic={magic!r}, id={prod_str!r}, model={model!r}, body_len={claimed_len}, flags=0x{flags:x}")

    dec_md5 = aes_128_cbc_decrypt(data[0xF0:0x110], MTK_INTERNAL_KEY, ZERO_IV)
    comp_md5 = hashlib.md5(data[0x80:0xF0] + (b"\x00" * 32) + data[0x110:-256]).digest()
    assert dec_md5[:16] == comp_md5, "DLM Body MD5 mismatch"
    print(f"  [PASS] Body MD5 matches MD5(enc_hdr + 0x00*32 + chunks) = {comp_md5.hex()}")

    pos = 0x110
    end = len(data) - 256
    chunks = {}
    while pos < end:
        tag = data[pos:pos + 4]
        cflags, sz = struct.unpack_from("<II", data, pos + 4)
        magic_dec = aes_128_cbc_decrypt(data[pos + 12:pos + 28], prod_key_md5, prod_iv_md5)
        sha_dec = aes_128_cbc_decrypt(data[pos + 28:pos + 60], prod_key_md5, prod_iv_md5)
        assert magic_dec == APPEND_MAGIC, f"Chunk {tag!r} magic mismatch: {magic_dec!r}"
        payload = data[pos + 60:pos + 60 + sz]
        calc_sha = hashlib.sha256(payload).digest()
        assert sha_dec == calc_sha, f"Chunk {tag!r} SHA-256 mismatch"
        chunks[tag.decode("ascii")] = payload
        print(f"  [PASS] Chunk {tag.decode()!r}: flags={cflags}, len={sz}, magic='reserved mtk inc', sha256={calc_sha.hex()}")
        pos += 60 + sz
    assert pos == end, f"Unparsed trailing bytes: {end - pos}"

    if "ixml" in chunks:
        xml_txt = chunks["ixml"].decode("utf-8")
        print("\n--- Decoded 'ixml' Manifest ---")
        print(xml_txt.strip())
        root = ET.fromstring(xml_txt)
        method = root.findtext("SW/METHOD")
        tag_name = root.findtext("SW/TAG")
        path = root.findtext("SW/PATH")
        print(f"  Parsed <SW>: TAG={tag_name!r}, METHOD={method!r}, PATH={path!r}")

    if "smth" in chunks:
        with tarfile.open(fileobj=io.BytesIO(chunks["smth"]), mode="r:gz") as tf:
            print("\n--- Payload Tarball Entries ---")
            for m in tf.getmembers():
                assert not m.name.startswith("/") and ".." not in m.name, f"Unsafe tar member {m.name}"
                print(f"  {'d' if m.isdir() else '-'} {m.uname}:{m.gname} {m.size:6d} {m.name}")


def main() -> None:
    p = argparse.ArgumentParser(description="Verify MTK/TPV Autorun.upg container")
    p.add_argument("--upg", required=True)
    p.add_argument("--pubkey", required=True)
    p.add_argument("--aes-key", required=True)
    p.add_argument("--aes-iv", required=True)
    args = p.parse_args()
    verify_container(args.upg, args.pubkey, args.aes_key, args.aes_iv)


if __name__ == "__main__":
    main()
