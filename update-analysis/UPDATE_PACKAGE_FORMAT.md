# Update Package Format (`Autorun.upg` & `upgrade_loader.pkg`)

## 1. Binary Layout of `Autorun.upg` (`#DH@FiRm` DLM Format)

Reconstructed from ARM32 disassembly of `libdtv_common.so` (`dlm_locate_codefile_hdr`, `x_dlm_download_by_tag`) and verified programmatically via [scripts/verify_upg_container.py](../scripts/verify_upg_container.py) & [scripts/build_safe_rw_upg.py](../scripts/build_safe_rw_upg.py):

| Offset Range | Size | Cryptographic Wrapping | Fields & Validation |
|---|---|---|---|
| `0x0000..0x007F` | `128` B | Plaintext (Unsigned) | Null-padded outer filename (`"Autorun.upg\0..."`) |
| `0x0080..0x00EF` | `112` B | AES-128-CBC (`K=0x94102909*4`, `IV=0`) | `+0x00` vendor (4B), `+0x04` magic (`"#DH@FiRm"`), `+0x0C` prod_id (60B), `+0x48` `body_len` (u32 LE), `+0x4C` `flags` (u32 LE), `+0x50` model (32B) |
| `0x00F0..0x010F` | `32` B | AES-128-CBC (`K=0x94102909*4`, `IV=0`) | Decrypted `[:16]` must equal `MD5(data[0x80:0xF0] + b"\x00"*32 + data[0x110:-256])` |
| `0x0110..end-256` | Variable | Mixed Plaintext Header + AES-128-CBC Metadata | Repeating chunks `[4B Tag | 4B flags | 4B size | 16B AES("reserved mtk inc") | 32B AES(SHA256(payload)) | payload]` |
| `end-256..end` | `256` B | RSA-2048 PKCS#1 v1.5 | Signs raw `SHA-256(data[0x80:-256])` verified against `/ro_data/*PubKey*.pem` |

---

## 2. Manifest Schema (`ixml` Chunk) & Payload Tags (`smth`, `3rdp`, etc.)

The first chunk (`Tag = "ixml"`) carries UTF-8 XML instructing `libmtkapp.so` how to write subsequent tagged chunks:

```xml
<UPGRADE>
  <SW>
    <TAG>smth</TAG>
    <METHOD>FILE</METHOD>
    <PATH>/3rd_rw</PATH>
  </SW>
</UPGRADE>
```

| `<METHOD>` Enum (`sub_404f28`) | Register Branch | Target Path Constructed by `libmtkapp.so` | Notes |
|---|---|---|---|
| `PART` (`r6 == 0`) | `0x404fa4` | `"/dev/nand_%d"` (e.g., `"/dev/nand_10"`) | **Broken on MT5880 kernel** -> returns `-22 ENOENT` (`8`-second `...` abort) |
| `PMTD` (`r6 == 1`) | `0x404fd4` | Indexes `PMTD` table (`"mtd0"`..`"mtd13"`) | Resolves `/dev/mtd10`, `/dev/mtd12`, etc. cleanly |
| `PSDM` (`r6 == 2`) | `0x404fbc` | `"sdm%d"` | Alternate SDM block device path |
| `FILE` | Archive extract handler | Extracts POSIX `ustar` `.tar.gz` (`smth` chunk) directly into `<PATH>` (`/3rd_rw`) | Lock-compliant for writable UBIFS customizations |
