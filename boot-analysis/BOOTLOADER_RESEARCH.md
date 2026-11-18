# Bootloader Research (`Preloader` + `U-Boot` + Unstripped DWARF `uenv`)

> **Artifacts:** `extracted/uboot.bin` (`1,314,592` B, `SHA256: 88bfd15c...`) | `upgrade_loader.pkg#part:uenv` (`2,384` B, `SHA256: baa332db...`) | [evidence/02](../evidence/02_secure_boot_chain_disasm.txt)

## 1. Two-Stage Bootloader Anatomy (`load`: `1,314,592` Bytes)

| Offset (`load` / `uboot.bin`) | Region | ISA / Mode | Verified Technical Role |
|---|---|---|---|
| `0x000000 .. 0x00a03F` (`41,024` B) | **Thumb-2 SRAM Preloader** (`VA 0xfb000000`) | ARM Thumb-2 | Mask BootROM `"MTK/DTV/ROMCODE/NANDBOOT/V01.00"` loader (`Start Pmain`). Handshakes with 8051 co-processor (`"Preloader T8032 ack !"` / `"T8032 NO ack!"`), runs Dual-Channel DDRPHY DQS calibration (`"DRAM Channel A/B Calibration"`, MMIO `0xf0004xxx`), reads Extended NAND IDs (`ExNID=0x00001676/00000004/00000056`), tests OTP eFuse `0xf0008664`, invokes BootROM RSA-2048 (`0xfb0034f0`), and runs **HW-LZHS** decompression (`0xf00080b0`). |
| `0x00a040 .. 0x140f1F` | **Main U-Boot + RSA Trailer (`+0x6c4b0`)** | Compressed -> ARM32 SDRAM | Parses environment (`uenv`), checks EEPROM active bank flag (`A` vs `B`), verifies `kerA`/`kerB` RSA-2048 trailers (`0x25152c`, `0x283f2c`), and jumps to `uImage` (`ep=0x8000`). |

---

## 2. Disassembly Proof of Preloader OTP Gate & Irrecoverable Brick Trap

Capstone Thumb-2 disassembly (`evidence/02_secure_boot_chain_disasm.txt`, base `0xfb000000`):

```arm
  0xfb001450: ldr      r3, [pc, #0xec]        ; *(0xfb001540) = 0xf0008664 (OTP eFuse status MMIO)
  0xfb001458: ldr      r3, [r3]               ; Read fused hardware silicon configuration word
  0xfb00145a: tst.w    r3, #0x100000          ; Bit 20 == 1 -> Retail Secure Boot permanently fused
  0xfb00145e: beq      #0xfb001480            ; Skip only on unfused engineering silicon
  0xfb001460: ldr      r3, [pc, #0xe0]        ; *(0xfb001544) = 0xfb0053bc (SW sec flag == 1 in stock)
  0xfb001462: ldr      r3, [r3]
  0xfb001464: cbz      r3, #0xfb001480
  ...
  0xfb001478: bl       #0xfb0034f0            ; Calls BootROM RSA-2048 check (trailer @ +0x6c4b0)
  0xfb00147c: cmp      r0, #0
  0xfb00147e: bne      #0xfb001536            ; Failure returns status 2 to caller:

; Caller failure handler:
  0xfb00052a: ldr      r0, [pc, #0x24]        ; 0xfb005094 -> "not secure loader\n"
  0xfb00052c: bl       #0xfb0005ac            ; Prints error to UART0 (ttyMT0 @ 115200n1)
  0xfb000530: b        #0xfb000520            ; Jumps to 0xfb000520 -> INFINITE BRICK LOOP!
```

Because `load` runs *before* USB storage initialization and has no mirrored backup partition (`mtd0` only), corrupting U-Boot or replacing it with an unsigned image hard-bricks the board until raw NAND erasure/programming outside the SoC.

---

## 3. Forensic Anatomy of Unstripped DWARF `uenv` (`2,384` B Relocatable ELF)

Inspecting `upgrade_loader.pkg#part:uenv` (`mtd1`, `readelf -h -S -s -A --debug-dump=info`) proves MediaTek accidentally shipped an unstripped `ET_REL` object containing full DWARF v2 debug sections (`.debug_info`, `.debug_line`, `.debug_str`) alongside an `8`-byte `.data` section:

| `readelf` Metadata Field | Exact Observed Value | Forensic Meaning |
|---|---|---|
| **Compiler & Source Path** | `GNU C 4.5.1`; `env.c` + `drv_lib/mt5880/inc/x_typedef.h` (`.../chiling/uboot/board/mt5880`) | Confirms exact U-Boot BSP path & GCC `4.5.1` compiler |
| **ARM EABI Attributes** | `Tag_CPU_name: "7-A"`, `Tag_THUMB_ISA_use: Thumb-2`, `Tag_ABI_optimization_goals: Aggressive Size`, **`Tag_DIV_use: Not allowed`** | Proves ARMv7 without HW `SDIV`/`UDIV` (matching Cortex-A9) & `-Os` size optimization |
| **`.data` @ `+0x00` (`global_magic`)** | `0x53965368` (`UINT32`) | U-Boot MT5880 environment magic sentinel |
| **`.data` @ `+0x04` (`global_kernel_dram_size`)** | **`0x21fb9000`** (`570,134,528` B = **`543.72 MiB`**) | Exact Linux kernel DRAM window passed cleanly from U-Boot to kernel! |
| **`.text` Size** | `0x00000000` (`0` bytes) | Pure global `.data` struct object linked/injected cleanly as `mtd1` metadata |
