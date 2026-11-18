# Hardware Photographic Documentation (`HARDWARE_PHOTOGRAPHIC_DOCUMENTATION`)

## 1. Current Acquisition Status (Strict Epistemic Disclosure)

**Status:** `0` physical mainboard photographs currently committed.

Consistent with our scientific integrity rules ([RESEARCH_SCOPE.md](../../RESEARCH_SCOPE.md)), physical chassis disassembly was **not** performed on the study unit:
- No external flash programmer or hot-air rework station was available to desolder or recover the NAND IC in case of hardware fault.
- Consequently, no raw mainboard silkscreen (`PCB rev`), SoC package markings (`MT5880xxxx`), DRAM IC codes, or SLC/MLC NAND chip markings have been visually photographed on this exact physical unit.
- Because the string `715G` / `715G7904M` yields **0 occurrences** across `extracted/uboot.bin`, `scratch/vmlinux.bin`, `extracted/appfs1`, `extracted/rootfs1`, and `roda`, assigning a board code solely from third-party repair-forum listings without direct board photography would violate evidence standards and is explicitly recorded as **UNVERIFIED**.

## 2. Standardized Acquisition Protocol (When Physical Teardown Is Performed)

Future contributors adding teardown imagery for an authentic `AOC LE32S5760/20` unit should place annotated, EXIF-scrubbed JPEG/PNG photographs in this directory using the naming convention and verification checklist below:

| Expected Filename | Target Photographic Subject | Required Callouts / Verification Target |
|---|---|---|
| `01_rear_label_model_serial_redacted.png` | Rear chassis label (serial/MAC redacted) | Confirm `LE32S5760/20`, power rating, manufacturing plant/date |
| `02_mainboard_full_top.png` | Full mainboard top overview | Confirm exact PCB silkscreen part number (verify or refute `715G7904M`), connector layout (`LVDS`, `PSU`, `IR/Key`, `Speakers`) |
| `03_soc_mt5880_heatsink_removed.png` | MediaTek SoC die/package after heatsink removal | Read exact part number (`MT5880...`), package revision, and date code; relate to `mt53xx_get_ic_version` |
| `04_nand_flash_ic_closeup.png` | TSOP-48 / BGA NAND Flash IC | Read vendor & part number (compare against kernel supported ID table: Hynix `H27U*`, Micron `MT29F*`, Samsung `K9GAG08U0E`, Toshiba `TC58NVG*`) |
| `05_dram_ics_dual_channel.png` | DDR3 SDRAM ICs adjacent to SoC | Verify chip count, bit width, and total RAM capacity (`512 MB` dual-channel DDR implied by `Preloader DRAM Channel A/B Calibration`) |
| `06_uart_service_port_pinout.png` | UART (`ttyMT0`) / VGA DDC / service header pads | Document TX/RX/GND pinout, logic voltage level (`3.3V` TTL), and pull-up population |
| `07_tcon_panel_connector.png` | LVDS/eDP connector & T-Con timing PCB | Document panel resolution & LVDS channel configuration |
| `08_wifi_module_usb_internal.png` | Internal USB Wi-Fi module (if populated) | Verify Ralink/MediaTek or Atheros chipset against `wifi_ko` drivers (`rt5572sta`, etc.) |

## 3. Image Hygiene Requirements

1. **Strip EXIF GPS / device metadata** before committing (`exiftool -all=`).
2. **Redact unique serial numbers, MAC addresses, PlayReady/Netflix ESNs, and HDCP keys** visible on barcode stickers.
3. Update [../HARDWARE_COMPONENT_INVENTORY.csv](../HARDWARE_COMPONENT_INVENTORY.csv) and [../MAINBOARD_ANALYSIS.md](../MAINBOARD_ANALYSIS.md) moving items from `UNVERIFIED` to `CONFIRMED` with explicit citation of the corresponding filename in this folder.
