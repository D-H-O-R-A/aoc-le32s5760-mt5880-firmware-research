# Deep Reverse Engineering of the Linux 3.0.13 MT5880 Kernel

> **Module Inventory:** [KERNEL_MODULE_INVENTORY.csv](KERNEL_MODULE_INVENTORY.csv) | **Disassembly Proof:** [evidence/02_secure_boot_chain_disasm.txt](../evidence/02_secure_boot_chain_disasm.txt)

## 1. Kernel Binary Anatomy & Built-In Boot Defaults

Decompressing `kerA`/`kerB` (`2,638,124` B) yields `scratch/vmlinux.bin` (`4,432,612` B, `SHA256: c52a4aa8bcc21fc263a44c54fdebfe95ad1de53bf1137bd4f45d934e2c63c790`).

| Kernel Attribute | Empirically Extracted Value | Binary Verification |
|---|---|---|
| **Version Banner** | `Linux version 3.0.13 (roylo@TWCLS066) (gcc version 4.5.1 (GCC) ) #1 SMP PREEMPT Thu Aug 4 00:06:04 CST 2016` | `.rodata` string |
| **Virtual Base Address** | `0xc0008000` (after stripping `64`-B `uImage` header `0x27051956`, `load=0x7fc0`, `ep=0x8000`) | Re-anchored ARM branch & literal pool alignment |
| **Built-In Default `CMDLINE`** | `"console=ttyMT0,115200n1 root=/dev/ram"` | Extracted verbatim from `vmlinux.bin` |
| **`kallsyms` / `IKCONFIG` State** | `kallsyms_addresses=False`, `kallsyms_num_syms=False`, `__ksymtab_strings=False`, `IKCFG_ST=False` | Stripped/compiled-out (`CONFIG_KALLSYMS=n`, `CONFIG_IKCONFIG=n`); symbols resolved via function banners/strings & Capstone |
| **Compiled `mt53xx_*` Helpers (`7`)** | `mt53xx_bim_lock`, `mt53xx_get_ic_version`, `mt53xx_get_reserved_area`, `mt53xx_get_rodata_addr`, `mt53xx_get_rwdata_addr`, `mt53xx_timer_read`, `mt53xx_timer_read_ll` | Matched directly inside `vmlinux.bin` |
| **Compiled Source Paths** | `381` unique `/share/Release_code_use/Roy/release/vm_linux/chiling/kernel/linux-3.0/...` paths | Compiled `BUG()`/`WARN_ON()`/__FILE__ strings |

---

## 2. Dissected `NFSB` & `dm-verity` Enforcement Engine (`vmlinux.bin`)

Because `kallsyms` and `IKCONFIG` were stripped out to harden the retail kernel, function boundaries inside `vmlinux.bin` were recovered cleanly through string x-refs (`"<3>nfsb: header verification failed"`, `"<3>device-mapper: verity: Block hash does not match!"`, `0xc04292f0`/`0xc0429370`) and Capstone disassembly:

1. **`dm_mount_root_nfsb` (`0xc0009594`, `init/do_mounts_dm.c`):**
   - Intercepts root mount for `mtd6`/`mtd7` (`rfsA`/`rfsB`), allocating `/dev/nfsb` rather than trusting an unsigned initramfs switch.
2. **`populate_table_nfsb` (`0xc02243c4`, `drivers/md/dm-verity.c` + `dm-bht.c`):**
   - Reads the `231`-byte `struct nfsb_header_v2` (including `fs_size_sectors_be`, `"md5"`, and `root_hexdigest` ASCII hex) from sector `0` of `/dev/mtdblock*` (meaning userspace `dmsetup ... --table "0 0 verity /dev/mtdblock9"` intentionally passes `0 0` dummy bounds).
   - Emits kernel errors `nfsb: open %s failed`, `nfsb: create_dev failed`, `nfsb: check %s header fail`, and `nfsb: header verification failed` on tampering.
3. **`nfsb_rsa_check` (`0xc0028df8` — Full-Width Integer Verifier):**
   ```arm
   0xc0028ee0: mov   r2, #0x67       ; Signed NFSB metadata length (103 bytes)
   0xc0028f04: blx   r3              ; crypto_hash_update(&desc, &sg, 0x67)
   0xc0028f38: blx   r3              ; crypto_hash_final -> 32-byte SHA-256 digest
   0xc0028f5c: add   r1, r8, #0x67   ; hdr + 0x67 -> 128B Big-Endian RSA signature S
   0xc0028f64: bl    #0xc0189820     ; mpuint_setbytes(sig_mpi, S, 128)
   0xc0028f84: mov   r1, sb          ; e = 3 @ VA 0xc04292f0 (128B BE)
   0xc0028f88: mov   r2, fp          ; N = 1024-bit modulus @ VA 0xc0429370
   0xc0028f8c: bl    #0xc0189f2c     ; out = S^3 mod N (mpuint_modexp)
   0xc0029000: bl    #0xc01897c4     ; mpuint_equal(out, 0^96 || SHA256)
   ```
   - Crucially, `mpuint_equal` performs an **exact full `1024`-bit check** rather than permissive ASN.1 suffix scanning — completely defeating Bleichenbacher's classic $e=3$ signature forgery.

---

## 3. Custom Storage, Crypto & Hardware Subsystems Compiled In

- **`arch/arm/mach-mt53xx/{gpio6896.c, pdwnc_gpio6896.c}`:** GPIO & PDWNC standby integration with T8032.
- **`drivers/mtd/{mtdsdm.c, mtk_mtdpart.c}` & `nand/mtk_nand.c`:** MediaTek `PMTD`/`PSDM` partitions (`nand 1..30`) + hardware ECC + `NAND_AES_Encryption`/`Decryption`/`INIT` + `10` Hynix/Micron/Samsung/Toshiba NAND flash IDs.
- **`crypto/mtk_crypto.c`:** Hardware cipher/hash acceleration plumbed into Linux CryptoAPI alongside `fs/ubifs` (`dir.c`, `journal.c`, `tnc.c`).
- **`drivers/usb/host/{mtk_hcd.c, mtk_qmu.c}`:** Built-in MTK USB HCD & Queue Management Unit.
