# Complete Boot Sequence Diagram (`Silicon` -> `Qt SystemManager`)

> **Vector Diagram:** [diagrams/BOOT_CHAIN.svg](../diagrams/BOOT_CHAIN.svg)

```mermaid
sequenceDiagram
    autonumber
    participant T8032 as T8032 Standby MCU (PDWNC)
    participant ROM as Mask BootROM (Silicon)
    participant PRE as Preloader (SRAM 0xfb000000)
    participant UB as U-Boot (DRAM)
    participant KER as Linux 3.0.13 (0xc0008000)
    participant INIT as BusyBox Init / rc.local
    participant TV as dtv_svc & SystemManager

    T8032->>ROM: Power-on / IR Remote wakeup -> release ARM reset
    Note over ROM: Magic "MTK/DTV/ROMCODE/NANDBOOT/V01.00"
    ROM->>PRE: Load load[0..0xa040] into internal SRAM
    PRE->>T8032: Handshake ("Preloader T8032 ack !")
    PRE->>PRE: Dual-Channel DRAM A/B Calibration + NAND ExNID
    PRE->>PRE: Read OTP eFuse MMIO (0xf0008664 & 0x100000)
    PRE->>PRE: BootROM RSA-2048 verify U-Boot (+0x6c4b0) [bl 0xfb0034f0]
    alt RSA-2048 Signature Mismatch
        PRE-->>PRE: Print "not secure loader\n" & SPIN FOREVER (0xfb000520)
    else Signature Valid
        PRE->>UB: HW-LZHS decompress (0xf00080b0) & jump to U-Boot
        UB->>UB: Read uenv & EEPROM bank flag -> choose Bank A or B
        UB->>UB: Verify kerA/kerB dual RSA-2048 trailers (0x25152c / 0x283f2c)
        UB->>KER: HW-LZHS decompress uImage (load=0x7fc0, ep=0x8000)
        KER->>KER: dm_mount_root_nfsb @ 0xc0009594 -> nfsb_rsa_check (e=3)
        KER->>KER: Verify 12,514 rfsA/B blocks via 2-level dm-bht MD5
        KER->>INIT: Mount / (SquashFS RO) & exec /sbin/init
        INIT->>INIT: rcS -> rc.local -> dmsetup verity mtd9/10 (/3rd: 23,767 blks)
        INIT->>INIT: ubiattach mtd11 (/perm), mtd12 (/3rd_rw UBIFS), mtd13 (/ro_data)
        INIT->>INIT: insmod dtv_driver.ko, star_mac.ko, rt5572sta.ko, fusion.ko
        INIT->>TV: Launch dtv_svc -> SystemManager (Qt 4.8.3) -> libnettv (Opera 6213)
    end
```

## Key Dependency & Timing Constraints

- `/etc/inittab` disables `ttyMT0` getty (`#1:2345:respawn:...`) and continuously respawns `/sbin/mnet_down.script` (`eth0`/`ra0` interface monitor).
- `appfs1/etc/init.d/rcS` starts optional `busybox readahead` from `/etc/readahead_early` (if present) before synchronously handing over to `/etc/rc.d/rc.local`.
- User-customizable writable persistence begins only **after** `ubi_mount_3rd_rw.sh` attaches `mtd12` (`ubi4:3rd_rw`) and `dtv_svc` inspects `/3rd_rw/upgrade/customer_version` (`0x036190`).
