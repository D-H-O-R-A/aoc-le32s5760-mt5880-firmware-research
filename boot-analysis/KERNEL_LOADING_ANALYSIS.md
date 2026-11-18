# Kernel Loading, Decompression & `dm-verity` Root Verification Analysis

## 1. `kerA`/`kerB` Storage & U-Boot `uImage` Format

Both kernel banks (`mtd4` `kerA` and `mtd5` `kerB`) inside `upgrade_loader.pkg` are bit-identical (`2,638,124` bytes, `SHA256: dd670a548ae9546ecc91eacf7dc4de6a9d2ea457178af0afc68c27e1ad59dbe8`). Structure:

1. **Header (`0x00..0x3F`, `64` bytes):** Legacy U-Boot `uImage` header (`IH_MAGIC = 0x27051956`, `ih_size = 4,432,548` B decompressed, `ih_load = 0x00007fc0`, `ih_ep = 0x00008000`).
2. **Compressed Payload:** MediaTek **HW-LZHS** stream expanding `~2.63 MB` to `4,432,612` bytes (`scratch/vmlinux.bin`, which retains the `64`-byte `uImage` header ahead of `4,432,548` bytes of ARM32 kernel text/data).
3. **Authentication Trailers:** Dual `[256B RSA-2048 Signature + 256B Public Key Certificate]` blocks observed at raw offsets `0x25152c` and `0x283f2c`.

---

## 2. Virtual Address Alignment Discovery (`uImage - 0x40 -> 0xc0008000`)

During static disassembly ([docs/02](../docs/02_secure_boot_chain_preloader_tz_and_nfsb.md), [scripts/inspect_pkg_and_nfsb.py](../scripts/inspect_pkg_and_nfsb.py)), naive base mapping of `scratch/vmlinux.bin` at `0xc0008000` shifted every `.rodata` literal by `64` bytes (`0x40`). Stripping the leading `64`-byte `uImage` header (`vm = vm_raw[0x40:]`) restores bit-exact alignment with ARM32 MMU mapping (`PAGE_OFFSET = 0xc0000000`, `TEXT_OFFSET = 0x00008000`):

- `0xc04292f0`: `128`-byte Big-Endian RSA Exponent `e = 3`
- `0xc0429370`: `128`-byte Big-Endian RSA-1024 Modulus `N` (`1024` bits)
- `0xc0009594`: `dm_mount_root_nfsb`
- `0xc02243c4`: `populate_table_nfsb`
- `0xc0028df8`: `nfsb_rsa_check`

---

## 3. Kernel-Enforced `dm-verity` / `NFSB` Execution Path

Once `vmlinux` boots and mounts `mtd6`/`mtd7` (`rfsA`/`rfsB`), `init/do_mounts_dm.c` (`dm_mount_root_nfsb`) and `drivers/md/{dm-verity.c, dm-bht.c}` execute the following mandatory integrity chain:

```
  [kernel boot -> dm_mount_root_nfsb @ 0xc0009594]
         │
         ▼ Reads 231B (0xe7) NFSB header from mtdblock (rfsA/B or dmsetup for 3rdA/B)
  [nfsb_rsa_check @ 0xc0028df8]
         ├── SHA-256(hdr[0x00:0x67])
         ├── S = int.from_bytes(hdr[0x67:0xE7], 'big')
         ├── out = S^3 mod N   (e @ 0xc04292f0, N @ 0xc0429370, mpuint_modexp @ 0xc0189f2c)
         └── Exact compare: mpuint_equal(out, 0x00^96 || SHA256) @ 0xc0029000
                ├── MISMATCH -> returns -1 -> refuse SquashFS mount
                └── MATCH    -> populates 2-level dm-bht MD5 tree (dm_bht_populate)
                                  └── Every 4 KB read verified on-the-fly against root hexdigest!
```

This kernel-internal verification runs **regardless of how an image reaches flash** — whether via `upgrade_loader.pkg`, `Autorun.upg` (`METHOD=PMTD`), or direct NAND write — proving that without the kernel `kerA`/`kerB` RSA-2048 signing key **and** the `NFSB` RSA-1024 private key, unsigned rootfs/3rd SquashFS images cannot boot.
