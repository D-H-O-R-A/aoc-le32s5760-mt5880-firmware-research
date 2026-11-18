# Kernel Build Configuration Reconstruction (`Linux 3.0.13-mt5880`)

## 1. Methodological Constraint: Absent `/proc/config.gz` (`CONFIG_IKCONFIG=n`)

Inspection of `scratch/vmlinux.bin` confirms `IKCFG_ST` is **not** embedded (`ikconfig_embedded: false` in [FIRMWARE_METADATA.json](../firmware-forensics/FIRMWARE_METADATA.json)). Consequently, `.config` symbols cannot be extracted with `extract-ikconfig`; instead, kernel configuration options below are reconstructed strictly from compiled-in C source paths (`381` `__FILE__` strings), symbol literals, and `.ko` `.modinfo` headers. Unobservable scalar tunables remain marked **UNKNOWN**.

---

## 2. Reconstructed Kernel Configuration Matrix

| Subtree / Kconfig Option (Inferred Option) | State | Primary Binary / Script Evidence |
|---|---|---|
| `CONFIG_ARM=y`, `CONFIG_CPU_V7=y` | **CONFIRMED (`=y`)** | `vermagic=3.0.13 SMP preempt mod_unload ARMv7`, `arch/arm/mm/cache-l2x0.c` |
| `CONFIG_SMP=y` | **CONFIRMED (`=y`)** | `vermagic` contains `SMP`; `kernel/smp.c`, `lib/cpu_rmap.c` compiled in |
| `CONFIG_PREEMPT=y` | **CONFIRMED (`=y`)** | `vermagic` contains `preempt` |
| `CONFIG_VFP=y` | **CONFIRMED (`=y`)** | `arch/arm/vfp/vfpmodule.c` compiled in |
| `CONFIG_HIGHMEM=y`, `CONFIG_CACHE_L2X0=y` | **CONFIRMED (`=y`)** | `arch/arm/mm/highmem.c`, `mm/highmem.c`, `arch/arm/mm/cache-l2x0.c` |
| `CONFIG_MODULES=y`, `CONFIG_MODULE_UNLOAD=y` | **CONFIRMED (`=y`)** | `kernel/module.c`, `vermagic` `mod_unload`, 12 external `.ko` loaded via `insmod` |
| `CONFIG_MODVERSIONS` | **LIKELY `=n`** | None of `Module.symvers` CRCs forced beyond `vermagic` in sample `.modinfo` (exact state inferred) |
| `CONFIG_IKCONFIG` | **CONFIRMED (`=n`)** | Absence of `IKCFG_ST` gzip signature anywhere in `vmlinux.bin` |
| `CONFIG_BLK_DEV_DM=y`, `CONFIG_DM_VERITY=y` | **CONFIRMED (`=y`)** | `drivers/md/{dm.c, dm-ioctl.c, dm-bht.c, dm-verity.c}`, `init/do_mounts_dm.c` |
| `CONFIG_SQUASHFS` (`=y` or built-in) | **CONFIRMED (`=y`)** | Rootfs mounts `squashfs` without an external `squashfs.ko` module |
| `CONFIG_MTD=y`, `CONFIG_MTD_NAND=y`, `CONFIG_MTD_UBI=y`, `CONFIG_UBIFS_FS=y` | **CONFIRMED (`=y`)** | `drivers/mtd/nand/mtk_nand.c`, `mtd_blkdevs.c`, `fs/ubifs/{dir.c, journal.c, tnc.c}` |
| `CONFIG_EXT2_FS=y`, `CONFIG_EXT3_FS=y`, `CONFIG_EXT4_FS=y`, `CONFIG_VFAT_FS=y` | **CONFIRMED (`=y`)** | `fs/ext2/*`, `fs/ext3/*`, `fs/ext4/*`, `fs/fat/*` present in built-in `vmlinux.bin` |
| `CONFIG_FUSE_FS=m`, `CONFIG_NTFS_FS=m` | **CONFIRMED (`=m`)** | Built as `appfs1/basic/modules/fuse.ko` and `ntfs.ko`; FAT/VFAT/MSDOS listed in `ins_fs_mod.sh` |
| `CONFIG_USB_SUPPORT=y` + HCD (`mtk_hcd` built-in/mod) | **CONFIRMED** | Built-in `drivers/usb/core/{hcd.c, hub.c}` & `mtk_hcd.c`/`mtk_qmu.c` + external `mtk-hcd.ko`/`xhci-hcd.ko` scripts |
| `CONFIG_NET=y`, `CONFIG_INET=y`, `CONFIG_IPV6=y` | **CONFIRMED (`=y`)** | `net/ipv4/*`, `net/ipv6/{af_inet6.c, sit.c, tcp_ipv6.c, xfrm6_*}` compiled in |
| `CONFIG_NETFILTER=y`, `CONFIG_NF_CONNTRACK=y`, `CONFIG_NF_NAT=y` | **CONFIRMED (`=y`)** | `net/netfilter/*`, `net/ipv4/netfilter/nf_nat_*`; userspace `iptables-1.4.15` shipped |
| `CONFIG_SECURITY` / `SELINUX` / `APPARMOR` | **NO ENFORCING LSM CONFIRMED** | Only core `include/linux/security.h` header path exists; no SELinux/AppArmor init or policy files in rootfs |
| `CONFIG_STRICT_DEVMEM` / `CONFIG_STACKPROTECTOR` | **UNKNOWN** | Not deterministically inferable without `IKCONFIG` or runtime `/dev/mem` test |

---

## 3. Toolchain & ABI Profile

- **Cross-Compiler:** `gcc version 4.5.1 (GCC)` (`vmlinux.bin` + `glibc libc-2.12.2.so`). Note that an older build artifact in `appfs1/lib/libz.so.1.2.3` records `GCC for MediaTek 4.4.2-20100324` (`GCC 4.4.2`), showing mixed MediaTek prebuilt library artifacts sharing the same ARM EABI ABI.
- **Loadable Module Compatibility:** Because every shipped `.ko` embeds `vermagic=3.0.13 SMP preempt mod_unload ARMv7 `, compiling third-party out-of-tree kernel modules requires matching kernel structs (`task_struct`, `net_device`, `usb_driver`), `SMP`, `PREEMPT`, and ARMv7 ABI compiled with GCC 4.5.x — and even then cannot bypass locked `dtv_driver.ko` dependencies or `rfsA` signature verification.
