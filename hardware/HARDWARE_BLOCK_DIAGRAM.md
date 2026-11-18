# Hardware Architecture Block Diagram (`AOC LE32S5760/20` / `MT5880`)

> **Scalar Vector Diagram:** [diagrams/HARDWARE_ARCHITECTURE.svg](../diagrams/HARDWARE_ARCHITECTURE.svg)  
> **Component Evidence Matrix:** [HARDWARE_COMPONENT_INVENTORY.csv](HARDWARE_COMPONENT_INVENTORY.csv)

## 1. Interactive Mermaid Architecture View

```mermaid
flowchart LR
    subgraph EXT_MEM ["Memory & Storage (Bus Confirmed, Exact ICs Unknown Until Teardown)"]
        DRAM["Dual-Channel DDR SDRAM\n(Ch A + Ch B Calibrated\n~512 MB Inferred)"]
        NAND["Raw NAND Flash (NFI)\n10 Candidate IDs in vmlinux\n(mtd0..mtd30: cfig + UBI + NFSB)"]
        EEPROM["EEPROM / NOR NVM\n(nor/eeprom_hw.c, storage.c\nBank Flags & Factory NVM)"]
    end

    subgraph SOC ["MediaTek MT5880 SoC (ARMv7-A SMP — CONFIRMED)"]
        CPU["ARMv7-A SMP Core\nARM32 + Thumb-2 + VFPv3\nPL310/L2x0 + GIC + PMU"]
        SEC["Mask BootROM + eFuse\n0xf0008664 & 0x100000\nHW-LZHS 0xf00080b0\nmtk_crypto / TrustZone"]
        COPROC["Embedded Co-Processors\nT8032 (8051 Standby MCU)\nAudio DSP (adsp + aqda)"]
        IO["Controllers & Display\nmt53_fb.c (DirectFB 1.4.1)\nstar_mac NIC | MTK_HCD + xHCI\ngpio6896 | UART ttyMT0"]
    end

    subgraph PERIPH ["Board Peripherals & Epistemic Boundaries"]
        NET["RJ45 eth0 + USB Wi-Fi\n(Ralink rt5572sta:\n148F:5572 / 043E:7A13/32 / 2001:3C1A)"]
        USB["USB Host Ports\nFAT32 / NTFS-3G / HID\n(Autorun.upg Delivery)"]
        PANEL["Panel LVDS / T-Con & Tuner\npqda (11.5 MB) + ISDB-Tb Ginga\n[Exact Panel/Tuner ICs: UNKNOWN]"]
        PCB["Mainboard PCB Silkscreen\nHypothesized: 715G7904M\n[0 hits in FW: UNVERIFIED]"]
    end

    DRAM <-->|"Dual-Channel DDR Bus"| CPU
    NAND <-->|"NFI Bus + HW ECC/AES"| SEC
    EEPROM <-->|"I2C/SPI (dtv_driver)"| COPROC
    CPU <--> SEC
    CPU <--> COPROC
    CPU <--> IO
    IO <-->|"MII/RMII & USB"| NET
    IO <-->|"USB HCD / QMU"| USB
    IO -.->|"Unverified Physical Layout"| PANEL
    SOC -.->|"Teardown Pending"| PCB
```

## 2. Node-to-Artifact Traceability Summary

- **Solid nodes** correspond to subsystems backed by disassembled machine instructions (`uboot.bin`, `vmlinux.bin`), module `.modinfo` metadata (`KERNEL_MODULE_INVENTORY.csv`), or `cfig` PKG tables (`FIRMWARE_METADATA.json`).
- **Dashed boundaries** (`PANEL`, `PCB`) explicitly flag hardware attributes requiring visual photography in [HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md).
