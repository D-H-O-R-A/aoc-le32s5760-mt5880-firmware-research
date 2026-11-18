# Hardware Architecture Block Diagram (`AOC LE32S5760/20` / `MT5880`)

> **Scalar Vector Diagram:** [diagrams/HARDWARE_ARCHITECTURE.svg](../diagrams/HARDWARE_ARCHITECTURE.svg)  
> **Component Evidence Matrix:** [HARDWARE_COMPONENT_INVENTORY.csv](HARDWARE_COMPONENT_INVENTORY.csv)

## 1. Interactive Mermaid Architecture View

```mermaid
flowchart LR
    subgraph EXT_MEM ["Memory & Storage (Bus Confirmed, Exact ICs Unknown Until Teardown)"]
        DRAM["Dual-Channel DDR3 SDRAM\n(Ch A+B Calibrated 0xf00046xx..48xx\nKernel = 0x21fb9000 / 543.72 MiB\nTotal Soldered DDR > 543.7 MiB)"]
        NAND["Raw NAND Flash (NFI)\n10 Candidate IDs in vmlinux\n(mtd0..mtd30: cfig + UBI + NFSB)"]
        EEPROM["EEPROM / NOR NVM\n(/dev/eeprom_0, _3, _4 in dtv_driver.ko\nBank Flags & Factory NVM)"]
    end

    subgraph SOC ["MediaTek MT5880 SoC (ARM Cortex-A9 SMP + VFP — CONFIRMED)"]
        CPU["ARM Cortex-A9 SMP Core (ARMv7-A)\n451_vfp_ca9 + Thumb-2 + VFPv3\nNo SDIV/UDIV + PL310/L2x0 + GIC + PMU"]
        SEC["Mask BootROM + OTP eFuse\n0xf0008664 & 0x100000\nHW-LZHS 0xf00080b0\nmtk_crypto / TrustZone Reserve"]
        COPROC["Embedded Co-Processors & Audio\nT8032 (8051 Standby MCU)\nadsp (1.27 MB) + aqda (131 KB)"]
        IO["Controllers & Scanout (/3rd/Img_Sgx empty)\nmt53_fb.c (DirectFB 1.4.1)\nstar_mac NIC | MTK_HCD + xHCI\nir6896 | pdwnc6896 | UART ttyMT0"]
    end

    subgraph PERIPH ["Board Peripherals & Epistemic Boundaries"]
        NET["RJ45 eth0 + USB Wi-Fi\n(Ralink rt5572sta:\n148F:5572 / 043E:7A13/32 / 2001:3C1A)"]
        USB["USB Host Ports\nFAT32 / NTFS-3G / HID\n(Autorun.upg Delivery)"]
        PANEL["Panel LVDS / T-Con & Tuner\npqda (11.5 MB) + ISDB-Tb Ginga\n[Exact Panel/Tuner ICs: UNKNOWN]"]
        PCB["Mainboard PCB Silkscreen\nHypothesized: 715G7904M\n[0 hits in FW: UNVERIFIED]"]
    end

    DRAM <-->|"Dual-Channel DDR Bus"| CPU
    NAND <-->|"NFI Bus + HW ECC/AES"| SEC
    EEPROM <-->|"I2C/SPI (/dev/eeprom_0,3,4)"| COPROC
    CPU <--> SEC
    CPU <--> COPROC
    CPU <--> IO
    IO <-->|"MII/RMII & USB"| NET
    IO <-->|"USB HCD / QMU"| USB
    IO -.->|"Unverified Physical Layout"| PANEL
    SOC -.->|"Teardown Pending"| PCB
```

## 2. Node-to-Artifact Traceability & Measurement Revision History

- **Solid nodes** correspond to subsystems backed directly by disassembled instructions (`uboot.bin`, `vmlinux.bin`), unstripped `uenv` `.data`/`.ARM.attributes` DWARF symbols (`global_kernel_dram_size = 0x21fb9000`), `DT_RPATH` compiler provenance (`451_vfp_ca9`), module `.modinfo` metadata (`KERNEL_MODULE_INVENTORY.csv`), or `cfig` PKG tables (`FIRMWARE_METADATA.json`).
- **DRAM Estimate Refinement (`~512 MB` -> `> 543.7 MiB`):** Initial high-level documentation inferred `~512 MB` from early 2014 TV class sizing. Subsequent extraction of `uenv` `.data` (`env.c`, `global_kernel_dram_size = 0x21fb9000` = `570,134,528` B = `543.72 MiB`) superseded that approximation, proving soldered DRAM is strictly larger than `543.72 MiB` once `mt53xx_get_reserved_area` DMA/video/TrustZone buffers are included ([MEMORY_ARCHITECTURE.md](MEMORY_ARCHITECTURE.md)).
- **Dashed boundaries** (`PANEL`, `PCB`) explicitly flag hardware attributes requiring visual photography in [HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/](HARDWARE_PHOTOGRAPHIC_DOCUMENTATION/README.md).
