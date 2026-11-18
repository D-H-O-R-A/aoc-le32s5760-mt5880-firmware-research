# Mainboard Analysis (`TPV MTK2K14PLF` / Hypothesized `715G7904M` Family)

> **Epistemic Notice:** The PCB part-number string `715G7904M` was introduced as a hypothesis in the physical chassis scope prompt. Comprehensive byte scans across `upgrade_loader.pkg`, `uboot.bin`, `vmlinux.bin`, `roda`, `appfs1`, and `rootfs1` return **0 occurrences** of `715G` or `715G7904M`. Accordingly, the exact silkscreen board code of the studied TV unit remains **UNCONFIRMED / UNVERIFIED** pending physical photography ([HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md)).

---

## 1. Firmware-Confirmed Board & ODM Identity

Although the PCB silkscreen code is unconfirmed from binary artifacts alone, the platform design identity is unambiguously stamped across multiple subsystems:

| Attribute | Observed Value | Binary / Script Evidence | Status |
|---|---|---|---|
| **Commercial Television Model** | `AOC LE32S5760/20` | Official distribution package `LE32S5760_V2.011_V0.2.zip`; UI model configuration | **CONFIRMED** |
| **ODM Manufacturer** | `TPV` / `TPVision` | `etc/profile` (`export SYS_ODM=TPV`, `export TPV_VERSION=000.001.205.145`); `dtv_driver.ko` `TPVision_2k13_d_custom.c` | **CONFIRMED** |
| **Platform Chassis Code** | `TPV_MTK2K14PLF` (`LT0` Latin America branch) | `ro_data` key filenames (`TPV_MTK2K14PLF_LT0_UPG_PubKey_Prod.pem`, etc.) | **CONFIRMED** |
| **Shared Philips Code Lineage** | `SYS_BRAND=Philips`, `Philips_2K13_ODM_pdwnc_ext.c`, `Philips_2K14...` UPG IDs | `extracted/appfs1/etc/profile`; `dtv_driver.ko`; `Autorun.upg` `#DH@FiRm` model header | **CONFIRMED** |
| **Target Broadcast Standard** | Brazilian `ISDB-Tb` / `Ginga` (`SBTVD`) | Full `rootfs1/ginga` stack (`libgingancl.so`, `libcommoncore.so`, CERTI build paths) | **CONFIRMED** |
| **PCB Silkscreen (`715G7904M`)** | Unconfirmed (`0` matches in firmware) | Not encoded in `uenv`, `cfig`, `vmlinux`, or `dtv_driver.ko` | **UNKNOWN / UNVERIFIED** |

---

## 2. Firmware-Implied Mainboard Subsystems

Even without opening the enclosure, the shipped kernel drivers and initialization scripts constrain which hardware subsystems exist on the mainboard:

1. **Dual-Channel DDR Memory Topology:** Preloader executes both `DRAM Channel A` and `DRAM Channel B` calibration during cold boot (`uboot.bin`), proving populated dual-bank/dual-channel DDR layout rather than single-channel population.
2. **Primary Raw NAND + Auxiliary NVM/EEPROM Storage:**
   - Primary boot and OS partitions (`mtd0..mtd30`) live on SLC/MLC raw NAND attached to the MT5880 NFI bus.
   - Presence of `nor/eeprom_hw.c` and `nor/storage.c` in `dtv_driver.ko`, combined with U-Boot dual-bank active slot selection logic (`libmtkapp.so @ 0x40ae80`), proves an auxiliary non-volatile parameter mechanism (I2C EEPROM and/or SPI NOR) for persistent boot-slot state and factory NVM calibration.
3. **Display Timing / Panel Data (`pqda`, `mtd17`):** `upgrade_loader.pkg` ships an dedicated `11,534,336`-byte `pqda` image mapped to `nand 17`. Together with QML layouts authored for `1280x720` OSD composition (`Background_1280x720.jpg`), the board drives a local LVDS/eDP flat panel via timing/picture-quality tables loaded out of `pqda`.
4. **Audio Stage (`adsp` + `aqda`):** Separate `adsp` (`mtd29`, `1,272,368` B) and `aqda` (`mtd18`, `131,216` B) partitions supply speaker equalization and Dolby MS10 audio routing parameters tailored to the chassis enclosure.
5. **Networking Interfaces:**
   - **Wired Ethernet (`eth0`):** Driven by `star_mac.ko` (`basic/modules/star_mac.ko`).
   - **Wireless LAN (`ra0`):** Driven strictly by the bundled Ralink `rt5572sta.ko` / `rtnet5572sta.ko` / `rtutil5572sta.ko` USB-Wi-Fi driver stack (`148F:5572`, `043E:7A13`, `043E:7A32`, `2001:3C1A`), routed via an internal USB port or external USB dongle depending on production SKU.
6. **Service UART Pads (`ttyMT0`):** `/etc/inittab` contains the commented-out line `#1:2345:respawn:/sbin/getty -n -L ttyMT0 115200 vt100 -l /sbin/autologin`, confirming `ttyMT0` (`115200` baud, `8N1`) as the mainboard SoC debug console. Physical pad locations on the PCB (dedicated header vs. VGA pin multiplexing) cannot be verified without board photography.

---

## 3. Why Attributing Unverified Board Schematics Is Prohibited

TPV produced numerous `715Gxxxx` mainboards across 2013–2016 Philips and AOC `MTK2K14` models with differing panel interfaces, Wi-Fi header wiring, SPI-NOR vs. EEPROM population, and power-supply rails. Without a photograph showing the physical white silkscreen on the studied `AOC LE32S5760/20` unit's PCB, treating `715G7904M` as anything more than an unverified external hypothesis would violate reproducibility standards.
