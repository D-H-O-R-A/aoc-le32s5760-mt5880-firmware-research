# Bootloader Research (`Preloader` + `U-Boot` + `uenv`)

> **Primary Artifacts:** `extracted/uboot.bin` (`1,314,592` B, `SHA256: 88bfd15c...`) | `extracted/uenv` (`2,384` B, `SHA256: baa332db...`) | [evidence/02_secure_boot_chain_disasm.txt](../evidence/02_secure_boot_chain_disasm.txt)

## 1. Two-Phase Structure of the `load` (`1,314,592`-Byte) Partition

Unlike vanilla embedded boards running plain U-Boot SPL, the MediaTek MT5880 `load` partition packs both a Thumb-2 SRAM Preloader and a compressed ARM32 U-Boot payload with cryptographic verification glue:

1. **Offset `0x000000 .. 0x00a03F` (`41,024` B) — Thumb-2 Preloader (`Base 0xfb000000`):**
   - Contains MediaTek BootROM signature string `"MTK/DTV/ROMCODE/NANDBOOT/V01.00"` and `"Start Pmain"`.
   - Executes Dual-Channel DDR calibration (`DRAM Channel A Calibration` / `DRAM Channel B Calibration`) and Extended NAND ID setup (`ExNID=0x00001676/00000004/00000056`).
   - Synchronizes with the 8051 standby controller (`"Preloader T8032 ack !"` / `"T8032 NO ack!"`).
   - Runs **HW-LZHS decompression** (`MMIO 0xf00080b0`) and **BootROM Secure Boot RSA-2048 verification**.
2. **Offset `0x00a040 .. 0x140f1F` — Compressed U-Boot Image + Signature Trailer (`+0x6c4b0`):**
   - Houses the main U-Boot ARM32 binary responsible for environment parsing (`uenv`), A/B bank selection (`kerA`/`kerB`, `rfsA`/`rfsB`, `3rdA`/`3rdB`), USB factory rescue (`upgrade_loader.pkg` detection at cold boot), and launching the Linux `uImage`.

---

## 2. Disassembly Proof of Preloader Secure-Boot Check & Brick Trap

Excerpt verified via Capstone (`evidence/02_secure_boot_chain_disasm.txt`, Thumb-2 base `0xfb000000`):

```arm
  0xfb001450: ldr      r3, [pc, #0xec]        ; Loads MMIO 0xf0008664 (OTP eFuse status)
  0xfb001458: ldr      r3, [r3]               ; Read fused silicon configuration word
  0xfb00145a: tst.w    r3, #0x100000          ; Test bit 20: hardware Secure Boot OTP fuse
  0xfb00145e: beq      #0xfb001480            ; Skip only if unfused dev/eng silicon
  0xfb001460: ldr      r3, [pc, #0xe0]        ; Loads *(0xfb001544) = 0xfb0053bc (SW sec flag)
  0xfb001462: ldr      r3, [r3]
  0xfb001464: cbz      r3, #0xfb001480
  ...
  0xfb001478: bl       #0xfb0034f0            ; Calls BootROM RSA-2048 signature verification (+0x6c4b0)
  0xfb00147c: cmp      r0, #0
  0xfb00147e: bne      #0xfb001536            ; On failure -> returns error code 2 to caller:

; Caller error handler (0xfb00052a..0xfb000530):
  0xfb00052a: ldr      r0, [pc, #0x24]        ; "not secure loader\n" @ 0xfb005094
  0xfb00052c: bl       #0xfb0005ac            ; UART tx output
  0xfb000530: b        #0xfb000520            ; Jumps to 0xfb000520 (b #0xfb000520 -> INFINITE HALT)
```

### Security Implication
Because OTP bit 20 at `0xf0008664` is one-time-programmable hardware silicon and `0xfb0053bc == 1` in the stock image, **replacing U-Boot with an unsigned custom build causes immediate halt on cold reset** before USB or TFTP recovery runs — making hardware NAND reprogamming via chip desoldering/clip the only escape from a bad `load` write.

---

## 3. Unstripped `uenv` Relocation Object (`2,384` B)

Inspecting PKG chunk `uenv` (`offset 0x0c12d0ed`, `mtd1`) shows an unstripped ARM32 relocatable ELF (`ET_REL`) compiled from `chiling/uboot/board/mt5880/env.c` (`GCC 4.5.1`). Key preserved symbols include:
- `global_magic`
- `global_kernel_dram_size`
This confirms how the U-Boot board port stores environment defaults separately from writable NAND environment runtime updates, while `appfs1/etc/scripts/{auto_launch.sh, manual_launch.sh}` call `/bin/fw_printenv - bootargs manual_launch` / `+ bootargs manual_launch` to inspect/toggle boot arguments when unlocked.
