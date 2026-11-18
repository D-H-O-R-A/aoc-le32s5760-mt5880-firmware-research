# Kernel Driver & Loadable Module Mapping (`MT5880`)

> **CSV Catalog:** [KERNEL_MODULE_INVENTORY.csv](KERNEL_MODULE_INVENTORY.csv)

## 1. Shipped `.ko` Loadable Kernel Modules (`12` Verified Binaries)

All `12` kernel modules inside `extracted/appfs1` carry `vermagic=3.0.13 SMP preempt mod_unload ARMv7 `. Notice `fusion.ko` appears in two distinct builds (`/basic/fusion.ko` `47,312` B and `/home/fusion.ko` `50,264` B).

| Subsystem | Module File | Size (B) | License | Hardware / Functional Role |
|---|---|---|---|---|
| **Core DTV SoC Engine** | `basic/dtv_driver.ko` | `6,846,712` | `Proprietary` | Monolithic MT5880 peripheral driver (display framebuffer, A/V decode, IR remote, NOR/EEPROM, PDWNC standby, tuner) |
| **DMA Memory Mapper** | `basic/modules/mtk_mmap.ko` | `3,220` | `Proprietary` | Contiguous/DMA memory mapping helper between userland `dtv_svc`/`libmtkapp` and A/V buffers |
| **DirectFB IPC** | `basic/fusion.ko` (+ `home/fusion.ko`) | `47,312` / `50,264` | `GPL` | Multi-application DirectFB 1.4.1 Shared Memory / IPC (`Denis Oliver Kropp <dok@directfb.org>`) |
| **USB Wi-Fi (Ralink/MTK)** | `basic/wifi_ko/rt5572sta.ko` + `rtnet5572sta.ko` + `rtutil5572sta.ko` | `1,655,384` + `57,840` + `46,312` | Unmarked / `GPL` | RT5572 dual-band USB WLAN stack; `rtnet5572sta.ko` lists VID:PID aliases `148F:5572`, `043E:7A13`, `043E:7A32`, `2001:3C1A` |
| **Storage Filesystems** | `basic/modules/ntfs.ko`, `fuse.ko` | `104,264`, `71,776` | `GPL` | Tuxera/Altaparmakov NTFS driver + FUSE (enabling userland `libntfs-3g.so.76.0.0` USB RW support) |
| **USB Human Interface** | `basic/modules/usbhid.ko`, `joydev.ko` | `30,172`, `12,912` | `GPL` | USB HID keyboard/mouse/gamepad support for browser/Smart TV UI input |
| **PMU Profiler** | `basic/modules/met.ko` | `22,640` | `GPL` | MediaTek `MET PMU Sampler` (`CJ Tsai`) performance counter profiler (unused in default production UI) |

### Scripted vs. Actually Shipped Modules (Discrepancy Notice)
Boot scripts in `etc/scripts/` (`ins_eth_mod.sh`, `ins_usb_sub_mod.sh`, `ins_wifi_mod.sh`, `ins_fs_mod.sh`) reference several conditional `.ko` names (`star_mac.ko`, `mtk-hcd.ko`, `xhci-hcd.ko`, `scsi_mod.ko`, `sd_mod.ko`, `usb-storage.ko`, `fat.ko`, `vfat.ko`, Atheros `ath_*.ko`, Realtek `8712u.ko`/`8192cu.ko`) wrapped in `if [ -f ... ]` guards. Cross-checking `FILESYSTEM_INVENTORY.csv` proves only the **`12` `.ko` files listed above** actually exist in the extracted `appfs1` tree (while SCSI/USB-core/FAT/HCD/Ethernet support is either compiled directly into `vmlinux.bin` — confirmed for `mtk_hcd.c`, `sd.c`, `fat/*.c`, `nand/*.c` — or absent for unused Wi-Fi chipset SKUs).

---

## 2. Internal Source Structure of Proprietary `dtv_driver.ko`

The `6.84 MB` `dtv_driver.ko` module leaks `8` source file paths revealing MediaTek and TPV hardware integration:

| Embedded Source Path in `dtv_driver.ko` | Hardware / Subsystem Mapped |
|---|---|
| `.../5880_driver/drv_cust/TPV/Philips_2K13_ODM_pdwnc_ext.c` | TPV / Philips 2K13/2K14 standby GPIO & power-down extensions |
| `.../5880_driver/drv_cust/TPV/TPVision_2k13_d_custom.c` | TPVision custom board/panel/peripheral board table |
| `.../5880_driver/ir6896/irrc_if.c` | Infrared remote protocol decoder / controller interface |
| `.../5880_driver/ir6896/irrx_if.c` | Hardware IR receiver (`IRRX`) interrupt/register driver |
| `.../5880_driver/nor/eeprom_hw.c` | Hardware EEPROM / NOR flash read/write primitives |
| `.../5880_driver/nor/storage.c` | Non-volatile configuration block abstraction (bank/NVM storage) |
| `.../5880_driver/pdwnc6896/pdwnc_hw.c` | MT5880 `PDWNC` standby & T8032 mailbox hardware controller |
| `.../mt5880/linux/native/mt53xx_fb/mt53_fb.c` | MediaTek MT53xx/MT5880 native framebuffer (`/dev/fb*`) driver |

Because `dtv_driver.ko` declares `license=Proprietary` and encapsulates panel timing, A/V pipeline, tuner control, and PDWNC IOCTLs, replacing `vmlinux` cleanly on a custom kernel without binary-compatible MediaTek headers breaks video, audio, and standby power control even if boot locks were absent.
