# Deep Reverse Engineering of the Linux 3.0.13 MT5880 Kernel

> **Module Inventory:** [KERNEL_MODULE_INVENTORY.csv](KERNEL_MODULE_INVENTORY.csv) | **Disassembly Traces:** [evidence/02_secure_boot_chain_disasm.txt](../evidence/02_secure_boot_chain_disasm.txt)

## 1. Kernel Identity & Memory Image Anatomy

Decompressing `kerA`/`kerB` yields `scratch/vmlinux.bin` (`4,432,612` bytes, `SHA256: c52a4aa8bcc21fc263a44c54fdebfe95ad1de53bf1137bd4f45d934e2c63c790`).

| Property | Observed Value | Evidence Source |
|---|---|---|
| **Exact Banner** | `Linux version 3.0.13 (roylo@TWCLS066) (gcc version 4.5.1 (GCC) ) #1 SMP PREEMPT Thu Aug 4 00:06:04 CST 2016` | `scratch/vmlinux.bin` `.rodata` |
| **Container Prefix** | `64`-byte U-Boot `uImage` header (`IH_MAGIC=0x27051956`, `ih_size=4,432,548`, `load=0x00007fc0`, `ep=0x00008000`) | First `0x40` bytes of `vmlinux.bin` |
| **Virtual Base Address** | `0xc0008000` (after stripping `0x40`-byte `uImage` header) | Cross-validated via `.rodata` string pointers |
| **Architecture & SMP** | `ARMv7-A` Little Endian (`ARM32`), `SMP`, `PREEMPT`, `VFPv3`, `HIGHMEM`, `cache-l2x0` | `.modinfo` `vermagic` + `arch/arm/*` paths |
| **`CONFIG_IKCONFIG`** | Disabled (`IKCFG_ST` absent from binary) | Direct binary search in `FIRMWARE_METADATA.json` |
| **Embedded Source Paths** | `381` unique `/share/Release_code_use/.../linux-3.0/...` file paths | Compiled `BUG()` / `WARN_ON()` / `__FILE__` literals |

---

## 2. Core Custom Subsystems Dissected Inside `vmlinux.bin`

### 2.1 `arch/arm/mach-mt53xx/` Machine & Power Management Layer
Unlike upstream ARM boards (`mach-versatile`, `mach-omap2`), the kernel embeds MediaTek's unified DTV board port `arch/arm/mach-mt53xx/` sharing the `6896`/`5880` register framework:
- `arch/arm/mach-mt53xx/gpio6896.c`: SoC-wide GPIO multiplexing and digital TV pin control.
- `arch/arm/mach-mt53xx/pdwnc_gpio6896.c`: Power-Down Control (`PDWNC`) standby GPIOs cooperating with the T8032 8051 co-processor (`dtv_driver.ko` `pdwnc6896/pdwnc_hw.c`).
- Exported SoC primitives observed in kernel strings/symbols: `mt53xx_get_ic_version`, `mt53xx_get_reserved_area`, `mt53xx_get_rodata_addr`, `mt53xx_get_rwdata_addr`, `mt53xx_timer_read`, `mt53xx_timer_read_ll`, `mt53xx_bim_lock`.

### 2.2 Storage Stack (`drivers/mtd/mtk_mtdpart.c`, `nand/mtk_nand.c`, `fs/ubifs`)
MediaTek heavily customizes the Linux MTD/NAND subsystem:
- `drivers/mtd/mtk_mtdpart.c` and `drivers/mtd/mtdsdm.c`: Custom partitioning (`cfig` / `PMTD` / `PSDM`) mapping `mtd0..mtd30`.
- `drivers/mtd/nand/mtk_nand.c`: Supports hardware ECC (`NAND_ECC_MODE`), inline hardware AES hooks (`NAND_AES_INIT`, `NAND_AES_Encryption`, `NAND_AES_Decryption`), and `10` compiled flash IC IDs (Hynix, Micron, Samsung, Toshiba).
- `fs/ubifs/{dir.c, journal.c, tnc.c}`: Native UBIFS support mounting `ubi2:perm` (`mtd11`), `ubi3:ro_data` (`mtd13`), and `ubi4:3rd_rw` (`mtd12`).

### 2.3 Security & Block Verification (`dm_mount_root_nfsb`, `nfsb_rsa_check`, `dm-bht`, `mtk_crypto`)
The most critical departure from vanilla Linux 3.0.13 is the tight coupling between kernel block-device mounting and RSA-1024 cryptography:
- `init/do_mounts_dm.c`: Invokes `dm_mount_root_nfsb` (`0xc0009594`) directly during root mount rather than relying on an unverified initramfs.
- `drivers/md/dm-verity.c` + `drivers/md/dm-bht.c`: ChromeOS/Google-derived `dm-bht` 2-level MD5 Merkle tree implementation paired with MediaTek's `populate_table_nfsb` (`0xc02243c4`).
- `nfsb_rsa_check` (`0xc0028df8`): Uses kernel internal multi-precision unsigned integer arithmetic (`mpuint_setbytes @ 0xc0189820`, `mpuint_modexp @ 0xc0189f2c`, `mpuint_trim @ 0xc0189600`, `mpuint_equal @ 0xc01897c4`) to enforce full `1024`-bit equality against $0^{96} \parallel \text{SHA-256}$, defeating Bleichenbacher $e=3$ trailing-garbage padding forgeries.
- `crypto/mtk_crypto.c`: MediaTek hardware cryptographic acceleration integrated into the Linux kernel CryptoAPI (`crypto/ablkcipher.c`, `aead.c`, `scatterwalk.c`).
