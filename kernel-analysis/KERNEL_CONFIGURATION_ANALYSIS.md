# Kernel Build Configuration Reconstruction (`Linux 3.0.13-mt5880`)

## 1. Methodological Constraint (`CONFIG_IKCONFIG=n`, `CONFIG_KALLSYMS=n`)

Binary search of `scratch/vmlinux.bin` proves both `IKCFG_ST` (`/proc/config.gz`) and kernel symbol tables (`kallsyms_addresses`, `kallsyms_num_syms`, `__ksymtab_strings`) were compiled out (`n`). Configuration flags below are strictly inferred from compiled `.c`/`.h` source path strings (`381` total), built-in console/printk banners, and `.ko` `.modinfo` attributes.

---

## 2. Evidence-Verified Kernel Configuration Matrix

| Subtree / Kconfig Option | Reconstructed State | Verifiable Binary Anchor |
|---|---|---|
| `CONFIG_ARM=y`, `CONFIG_CPU_V7=y` | **CONFIRMED (`=y`)** | `ARMv7 Processor` banner; `.ARM.attributes` `v7-A`, `vermagic ARMv7` |
| `CONFIG_SMP=y`, `CONFIG_PREEMPT=y`, `CONFIG_VFP=y` | **CONFIRMED (`=y`)** | `#1 SMP PREEMPT`, `kernel/smp.c`, `arch/arm/vfp/vfpmodule.c` |
| `CONFIG_HIGHMEM=y`, `CONFIG_CACHE_L2X0=y` | **CONFIRMED (`=y`)** | `arch/arm/mm/highmem.c`, `cache-l2x0.c`, `<5>Memory: %luk/%luk available... %luK highmem` |
| `CONFIG_CMDLINE` (Built-In Fallback) | **CONFIRMED** | Exact literal `"console=ttyMT0,115200n1 root=/dev/ram"` |
| `CONFIG_IKCONFIG` & `CONFIG_KALLSYMS` | **CONFIRMED (`=n`)** | Absence of `IKCFG_ST`, `kallsyms_addresses`, and `__ksymtab_strings` in `vmlinux.bin` |
| `CONFIG_MODULES=y`, `CONFIG_MODULE_UNLOAD=y` | **CONFIRMED (`=y`)** | `kernel/module.c`, `vermagic mod_unload`, `12` shipped `.ko` files |
| `CONFIG_BLK_DEV_DM=y`, `CONFIG_DM_VERITY=y` | **CONFIRMED (`=y`)** | `init/do_mounts_dm.c`, `drivers/md/{dm.c, dm-ioctl.c, dm-bht.c, dm-verity.c}` |
| `CONFIG_SQUASHFS=y`, `CONFIG_UBIFS_FS=y` | **CONFIRMED (`=y`)** | Built-in SquashFS + `fs/ubifs/{dir.c, journal.c, tnc.c}` (`mtd6`/`9`/`11`/`12`/`13`) |
| `CONFIG_EXT2_FS=y`, `CONFIG_EXT3_FS=y`, `CONFIG_EXT4_FS=y`, `CONFIG_VFAT_FS=y` | **CONFIRMED (`=y`)** | Built-in `fs/ext{2,3,4}/*`, `fs/jbd*/*`, `fs/fat/*` |
| `CONFIG_FUSE_FS=m`, `CONFIG_NTFS_FS=m`, `CONFIG_HID_SUPPORT=m` | **CONFIRMED (`=m`)** | Built as `fuse.ko`, `ntfs.ko`, `usbhid.ko`, `joydev.ko` |
| `CONFIG_MTD_NAND=y` + MediaTek `mtk_nand` / `mtk_mtdpart` / `mtdsdm` | **CONFIRMED (`=y`)** | `drivers/mtd/{mtk_mtdpart.c, mtdsdm.c, nand/mtk_nand.c}` |
| `CONFIG_NET=y`, `CONFIG_INET=y`, `CONFIG_IPV6=y`, `CONFIG_NETFILTER=y`, `CONFIG_NF_NAT=y` | **CONFIRMED (`=y`)** | `net/ipv4/*`, `net/ipv6/*` (`sit.c`, `xfrm6_*`), `net/ipv4/netfilter/nf_nat_*`, `net/wireless/wext-core.c` |
| `CONFIG_CRYPTO=y` + `mtk_crypto` | **CONFIRMED (`=y`)** | `crypto/{mtk_crypto.c, ablkcipher.c, aead.c, scatterwalk.c}` |
| `CONFIG_SECURITY_SELINUX` / `APPARMOR` | **DISABLED / ABSENT** | Zero LSM policy trees in rootfs; core `security.h` stub only |
| `CONFIG_STRICT_DEVMEM`, `CONFIG_CC_STACKPROTECTOR`, `CONFIG_KASAN` | **UNKNOWN (`KASAN` unavailable in 3.0.13) / UNVERIFIABLE** | No `IKCONFIG` or runtime `/dev/mem` probe |
