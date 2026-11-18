# Appendix B — Annotated ARMv7 / Thumb-2 Primary-Source Instruction Reference

This appendix serves as a self-contained primary-source disassembly dossier backing Chapters 1–7. Every virtual address, instruction mnemonic, immediate literal pool resolution, and GOT calculation is reproduced verbatim from [`evidence/02_secure_boot_chain_disasm.txt`](../evidence/02_secure_boot_chain_disasm.txt), [`evidence/03_upg_installer_disasm.txt`](../evidence/03_upg_installer_disasm.txt), and [`evidence/06_systemmanager_and_nettv_disasm.txt`](../evidence/06_systemmanager_and_nettv_disasm.txt), grouped into annotated functional basic blocks.

---

## B.1 Preloader Thumb-2 Secure Boot & HW-LZHS Engine (`extracted/uboot.bin`, Base `0xfb000000`)

Observed header & signature constants (`evidence/02_secure_boot_chain_disasm.txt`, lines 1–6):
- Preloader SW secure flag `@ 0xfb0053bc` (`file +0x53bc`): `1`
- LZHS header `@ +0x0a040`: `a8262000592406008400000000000000`
  - `decompressed_size = 2,107,048` B (`0x2026a8`), `compressed_size = 402,521` B (`0x62459`), `csum = 0x84`
- U-Boot RSA-2048 signature `@ +0x6c4b0..+0x6c5b0`: `405b8a78fbc01db4da0b1f386c7740ba8c3c9b2b6096b25db5be2232c3a5af31...`
- U-Boot RSA-2048 certificate `@ +0x6c5b0..+0x6c6b0`: `c1365b00d84dd3d65fe855f6a0864e8398345de66d180d21e629429627a1b595...`

### B.1.1 Main U-Boot Flash Loader & Halt Loop (`0xfb00048c..0xfb000532`, Thumb-2)

```arm
; Probe 0x100-byte LZHS header at flash offset 0xa000 -> DRAM 0x100000
  0xfb00048c: mov.w    r2, #0x100
  0xfb000490: mov.w    r0, #0x100000
  0xfb000494: mov.w    r1, #0xa000
  0xfb000498: strb.w   ip, [r3]
  0xfb00049c: bl       #0xfb00130c            ; NAND_DMA_Read(0x100000, 0xa000, 0x100)
  0xfb0004a0: mov      r1, r6
  0xfb0004a2: ldr      r0, [pc, #0x98]        ; [0xfb00053c] = 0xfb00506c
  0xfb0004a4: bl       #0xfb0003f8            ; UART log
  0xfb0004a8: ldr      r6, [r6]               ; r6 = decompressed_size (0x2026a8)
  0xfb0004aa: ldr      r0, [pc, #0x94]        ; [0xfb000540] = 0xfb005078
  0xfb0004ac: mov      r1, r6
  0xfb0004ae: bl       #0xfb0003f8
  0xfb0004b2: movs     r2, #0x44
  0xfb0004b4: str      r6, [r4]
  0xfb0004b6: movt     r2, #0x10              ; r2 = 0x100044 (&compressed_size)
  0xfb0004ba: movs     r3, #0x48
  0xfb0004bc: ldr      r2, [r2]               ; r2 = 0x62459
  0xfb0004be: movw     r1, #0xa050
  0xfb0004c2: movt     r3, #0x10              ; r3 = 0x100048 (&csum)
  0xfb0004c6: str      r1, [r4, #8]
  0xfb0004c8: ldr      r0, [pc, #0x78]        ; [0xfb000544] = 0xfb005084
  0xfb0004ca: str      r2, [r4, #4]
  0xfb0004cc: ldrb     r3, [r3]               ; r3 = 0x84
  0xfb0004ce: mov      r1, r3
  0xfb0004d0: strb     r3, [r5, #-0x1]!
  0xfb0004d4: bl       #0xfb0003f8

; Read full compressed payload + 0x300 trailing bytes (RSA signature/cert) -> 0x100000
  0xfb0004d8: ldr      r2, [r4, #4]
  0xfb0004da: mov.w    r0, #0x100000
  0xfb0004de: mov.w    r1, #0xa000
  0xfb0004e2: add.w    r2, r2, #0x300
  0xfb0004e6: bl       #0xfb00130c
  0xfb0004ea: movw     r3, #0x8074
  0xfb0004ee: movw     ip, #0x80e0
  0xfb0004f2: bfi      r3, r4, #0x10, #0x10
  0xfb0004f6: bfi      ip, r4, #0x10, #0x10
  0xfb0004fa: ldr.w    lr, [r3]
  0xfb0004fe: movs     r0, #0x50
  0xfb000500: movt     r0, #0x10              ; r0 = 0x100050 (stream)
  0xfb000504: mov.w    r1, #0xd00000          ; r1 = 0xd00000 (U-Boot DRAM entry)
  0xfb000508: mov      r2, r6                 ; r2 = 0x2026a8
  0xfb00050a: mov      r3, r5                 ; r3 = &csum
  0xfb00050c: str.w    lr, [ip]
  0xfb000510: bl       #0xfb00144c            ; verify + HW-LZHS + jump
  0xfb000514: cmp      r0, #2
  0xfb000516: beq      #0xfb00052a            ; RSA failure -> "not secure loader\n"
  0xfb000518: cbz      r0, #0xfb000522
  0xfb00051a: ldr      r0, [pc, #0x2c]        ; [0xfb000548] = 0xfb0050a8
  0xfb00051c: bl       #0xfb0005ac
  0xfb000520: b        #0xfb000520            ; INFINITE SELF-LOOP HALT
  0xfb000522: ldr      r0, [pc, #0x28]        ; [0xfb00054c] = 0xfb0050b8
  0xfb000524: bl       #0xfb0005ac
  0xfb000528: b        #0xfb000520
  0xfb00052a: ldr      r0, [pc, #0x24]        ; [0xfb000550] = 0xfb005094 ("not secure loader\n")
  0xfb00052c: bl       #0xfb0005ac
  0xfb000530: b        #0xfb000520            ; HALT FOREVER
  0xfb000532: nop
```

### B.1.2 Complete Hardware eFuse, RSA-2048 & HW-LZHS Decompressor (`0xfb00144c..0xfb00153a`)

```arm
  0xfb00144c: push     {r3, r4, r5, r6, r7, lr}
  0xfb00144e: mov      r7, r3
  0xfb001450: ldr      r3, [pc, #0xec]        ; [0xfb001540] = 0xf0008664 (eFuse register)
  0xfb001452: mov      r4, r0                 ; 0x100050 (compressed stream)
  0xfb001454: mov      r5, r1                 ; 0xd00000 (U-Boot entry)
  0xfb001456: mov      r6, r2                 ; 0x2026a8 (decompressed length)
  0xfb001458: ldr      r3, [r3]
  0xfb00145a: tst.w    r3, #0x100000          ; bit 20 = Secure Boot eFuse
  0xfb00145e: beq      #0xfb001480
  0xfb001460: ldr      r3, [pc, #0xe0]        ; [0xfb001544] = 0xfb0053bc (SW secure flag == 1)
  0xfb001462: ldr      r3, [r3]
  0xfb001464: cbz      r3, #0xfb001480
  0xfb001466: ldr      r3, [r4, #-0xc]        ; compressed size (0x62459)
  0xfb00146a: add.w    r0, r0, #0x10
  0xfb00146e: sub.w    r1, r4, #0x10          ; header + payload base (0x100040)
  0xfb001472: adds     r0, r0, r3
  0xfb001474: bic      r0, r0, #0xf           ; 16-byte aligned trailer offset (+0x6c4b0)
  0xfb001478: bl       #0xfb0034f0            ; BootROM RSA-2048 verify
  0xfb00147c: cmp      r0, #0
  0xfb00147e: bne      #0xfb001536            ; ret 2 -> "not secure loader" + halt

; Reset bus & program HW-LZHS peripheral (0xf0008078, 0xf00080b0..bc, 0xf00081d0)
  0xfb001480: ldr      r3, [pc, #0xc4]        ; [0xfb001548] = 0xf0008078
  0xfb001482: adds     r6, #8
  0xfb001484: ldr      r2, [r3]
  0xfb001486: bic      r2, r2, #0x300
  0xfb00148a: str      r2, [r3]
  0xfb00148c: orr.w    r3, r6, r5
  0xfb001490: tst.w    r3, #7
  0xfb001494: ldrb     r2, [r7]               ; expected 8-bit csum (0x84)
  0xfb001496: bne      #0xfb00153a
  0xfb001498: ldr      r3, [pc, #0xb0]        ; [0xfb00154c] = 0xf00081d0
  0xfb00149a: movs     r1, #0x18
  0xfb00149c: str      r1, [r3]
  0xfb00149e: ldr      r1, [r3]
  0xfb0014a0: ands     r0, r1, #0x20
  0xfb0014a4: bne      #0xfb00149e
  0xfb0014a6: ldr      r3, [pc, #0xa8]        ; [0xfb001550] = 0xf00080b0
  0xfb0014a8: mov.w    r1, #0x600
  0xfb0014ac: cmp.w    r4, #-0x8000000
  0xfb0014b0: str      r1, [r3]
  0xfb0014b2: sub.w    r1, r1, #0x200
  0xfb0014b6: str      r1, [r3]
  0xfb0014b8: bls      #0xfb0014c4
  0xfb0014ba: add.w    r1, r1, #0x1000
  0xfb0014be: str      r1, [r3]
  0xfb0014c0: movs     r3, #1
  0xfb0014c2: b        #0xfb0014ca
  0xfb0014c4: lsrs     r4, r4, #3
  0xfb0014c6: str      r1, [r3]
  0xfb0014c8: mov      r3, r0
  0xfb0014ca: ldr      r1, [pc, #0x88]        ; [0xfb001554] = 0xf00080b4
  0xfb0014cc: lsrs     r0, r5, #3
  0xfb0014ce: adds     r6, r6, r5
  0xfb0014d0: lsrs     r6, r6, #3
  0xfb0014d2: str      r4, [r1]               ; REG_SRC = 0x100050 >> 3
  0xfb0014d4: adds     r1, #4                 ; 0xf00080b8
  0xfb0014d6: str      r0, [r1]               ; REG_DST = 0xd00000 >> 3
  0xfb0014d8: adds     r1, #4                 ; 0xf00080bc
  0xfb0014da: str      r6, [r1]               ; REG_END
  0xfb0014dc: mov.w    r1, #0x1c00
  0xfb0014e0: cbnz     r3, #0xfb0014e6
  0xfb0014e2: mov.w    r1, #0xc00
  0xfb0014e6: ldr      r3, [pc, #0x68]        ; 0xf00080b0
  0xfb0014e8: ldr      r0, [pc, #0x64]        ; 0xf00080b0
  0xfb0014ea: str      r1, [r3]               ; Trigger HW-LZHS
  0xfb0014ec: movs     r3, #0
  0xfb0014ee: ldr      r1, [pc, #0x68]        ; [0xfb001558] = 0x40000001
  0xfb0014f0: b        #0xfb0014f8
  0xfb0014f2: adds     r3, #1
  0xfb0014f4: cmp      r3, r1
  0xfb0014f6: beq      #0xfb00153a
  0xfb0014f8: ldr.w    ip, [r0]
  0xfb0014fc: tst.w    ip, #0x100             ; bit 8 = HW completion flag
  0xfb001500: beq      #0xfb0014f2
  0xfb001502: ldr      r3, [pc, #0x48]        ; [0xfb00154c] = 0xf00081d0
  0xfb001504: movs     r1, #0
  0xfb001506: str      r1, [r3]
  0xfb001508: ldr      r4, [r3]
  0xfb00150a: ands     r4, r4, #0x20
  0xfb00150e: bne      #0xfb001508
  0xfb001510: ldr      r3, [pc, #0x3c]        ; [0xfb001550] = 0xf00080b0
  0xfb001512: ldr      r3, [r3]
  0xfb001514: and      r3, r3, #0xff          ; extract computed checksum byte
  0xfb001518: cmp      r3, r2                 ; compare against expected 0x84
  0xfb00151a: bne      #0xfb00153a
  0xfb00151c: ldr      r3, [pc, #0x3c]        ; [0xfb00155c] = 0xf0008074
  0xfb00151e: ldr      r2, [r3]
  0xfb001520: adds     r3, #0x78
  0xfb001522: str      r2, [r3]
  0xfb001524: subs     r3, #0xb8
  0xfb001526: str      r4, [r3]
  0xfb001528: mov.w    r2, #-1
  0xfb00152c: adds     r3, #4
  0xfb00152e: str      r2, [r3]
  0xfb001530: blx      r5                     ; Execute U-Boot at 0xd00000
  0xfb001532: mov      r0, r4
  0xfb001534: b        #0xfb00153c
  0xfb001536: movs     r0, #2                 ; return RSA error
  0xfb001538: b        #0xfb00153c
  0xfb00153a: movs     r0, #1                 ; return checksum/align error
```

---

## B.2 Linux Kernel `NFSB` Accessors, RSA-1024 Verifier & `dm-verity` (`vmlinux.bin`, Base `0xc0008000`)

`uImage` prefix (`64` bytes): `magic=0x27051956`, `size=4,432,548` B, `load=0x00007fc0`, `ep=0x00008000` (`evidence/02_secure_boot_chain_disasm.txt`, lines 167–786).

### B.2.1 Full Inline `nfsb_header` Getters (`0xc0028d44..0xc0028df4`)

```arm
; nfsb_fs_offset(): big-endian u32 @ [0x05..0x09] << 9 bytes (0x1000)
  0xc0028d44: ldrb     r2, [r0, #6]
  0xc0028d48: ldrb     r3, [r0, #5]
  0xc0028d4c: orr      r3, r3, r2, lsl #8
  0xc0028d50: ldrb     r2, [r0, #7]
  0xc0028d54: ldrb     r0, [r0, #8]
  0xc0028d58: orr      r3, r3, r2, lsl #16
  0xc0028d5c: orr      r0, r3, r0, lsl #24
  0xc0028d60: rev      r0, r0
  0xc0028d64: lsl      r0, r0, #9
  0xc0028d68: bx       lr

; nfsb_fs_size(): big-endian u32 @ [0x09..0x0d] << 9 bytes
  0xc0028d6c: ldrb     r2, [r0, #0xa]
  0xc0028d70: ldrb     r3, [r0, #9]
  0xc0028d74: orr      r3, r3, r2, lsl #8
  0xc0028d78: ldrb     r2, [r0, #0xb]
  0xc0028d7c: ldrb     r0, [r0, #0xc]
  0xc0028d80: orr      r3, r3, r2, lsl #16
  0xc0028d84: orr      r0, r3, r0, lsl #24
  0xc0028d88: rev      r0, r0
  0xc0028d8c: lsl      r0, r0, #9
  0xc0028d90: bx       lr

; nfsb_hash_size(): big-endian u32 @ [0x1e..0x22] << 9 bytes
  0xc0028d94: ldrb     r2, [r0, #0x1f]
  0xc0028d98: ldrb     r3, [r0, #0x1e]
  0xc0028d9c: orr      r3, r3, r2, lsl #8
  0xc0028da0: ldrb     r2, [r0, #0x20]
  0xc0028da4: ldrb     r0, [r0, #0x21]
  0xc0028da8: orr      r3, r3, r2, lsl #16
  0xc0028dac: orr      r0, r3, r0, lsl #24
  0xc0028db0: rev      r0, r0
  0xc0028db4: lsl      r0, r0, #9
  0xc0028db8: bx       lr

; nfsb_hash_type() / depth (2):
  0xc0028dbc: ldrb     r0, [r0, #0xd]
  0xc0028dc0: bx       lr

; nfsb_hash_algo() ("md5"):
  0xc0028dc4: add      r0, r0, #0xe
  0xc0028dc8: bx       lr

; nfsb_hash_block_sectors() (8 sectors = 4096B):
  0xc0028dcc: ldrb     r2, [r0, #0x23]
  0xc0028dd0: ldrb     r3, [r0, #0x22]
  0xc0028dd4: orr      r3, r3, r2, lsl #8
  0xc0028dd8: ldrb     r2, [r0, #0x24]
  0xc0028ddc: ldrb     r0, [r0, #0x25]
  0xc0028de0: orr      r3, r3, r2, lsl #16
  0xc0028de4: orr      r0, r3, r0, lsl #24
  0xc0028de8: rev      r0, r0
  0xc0028dec: bx       lr

; nfsb_hash_digest() ("666e1b26..." / "6cc5d821..."):
  0xc0028df0: add      r0, r0, #0x26
  0xc0028df4: bx       lr
```

### B.2.2 Full `nfsb_rsa_check` Function (`0xc0028df8..0xc0029044`)

```arm
  0xc0028df8: push     {r4, r5, r6, r7, r8, sb, sl, fp, lr}
  0xc0028dfc: mov      r8, r0                 ; r8 = hdr (0xe7 bytes)
  0xc0028e00: sub      sp, sp, #0x1c
  0xc0028e04: mov      sb, r1                 ; sb = rsa_e (128B BE 3 @ 0xc04292f0)
  0xc0028e08: mov      fp, r2                 ; fp = rsa_N (128B BE @ 0xc0429370)
  0xc0028e0c: mov      r1, #8
  0xc0028e10: ldr      r0, [pc, #0x230]       ; *(0xc0029048)=0xc03a527e ("sha256")
  0xc0028e14: mov      r2, #0xe
  0xc0028e18: bl       #0xc017d7a8            ; crypto_alloc_hash("sha256")
  0xc0028e1c: cmn      r0, #0x1000
  0xc0028e20: mov      r6, r0
  0xc0028e24: bls      #0xc0028e4c
  0xc0028e28: mov      sl, #0
  0xc0028e2c: ldr      r0, [pc, #0x218]       ; *(0xc002904c)=0xc03a5285 ("<3>Failed to load transform for sha256: ")
  0xc0028e30: mov      r1, r6
  0xc0028e34: mov      r8, sl
  0xc0028e38: bl       #0xc0313cd4
  0xc0028e3c: mov      r7, sl
  0xc0028e40: mvn      r4, #0
  0xc0028e44: mov      r5, sl
  0xc0028e48: b        #0xc0029010
  0xc0028e4c: str      r0, [sp, #0x10]
  0xc0028e50: mov      sl, #0
  0xc0028e54: ldr      r0, [r0, #0x18]
  0xc0028e58: mov      r1, #0xd0
  0xc0028e5c: str      sl, [sp, #0x14]
  0xc0028e60: bl       #0xc00a2c2c
  0xc0028e64: subs     r5, r0, #0
  0xc0028e68: bne      #0xc0028e88
  0xc0028e6c: ldr      r0, [pc, #0x1dc]       ; *(0xc0029050)=0xc03a52b2 ("<3>Failed to allocate digest memory.\n")
  0xc0028e70: mov      sl, r5
  0xc0028e74: bl       #0xc0313cd4
  0xc0028e78: mov      r8, r5
  0xc0028e7c: mov      r7, r5
  0xc0028e80: mvn      r4, #0
  0xc0028e84: b        #0xc0029010
  0xc0028e88: add      r7, sp, #0x18
  0xc0028e8c: ldr      r3, [r7, #-8]!
  0xc0028e90: ldr      r3, [r3, #4]
  0xc0028e94: mov      r0, r7
  0xc0028e98: blx      r3                     ; crypto_hash_init
  0xc0028e9c: subs     r4, r0, #0
  0xc0028ea0: ldrne    r0, [pc, #0x1ac]       ; *(0xc0029054)=0xc03a52d8 ("<3>crypto_hash_init failure: %d\n")
  0xc0028ea4: bne      #0xc0028f14
  0xc0028ea8: ldr      r1, [pc, #0x1a8]       ; *(0xc0029058)=0xc0469f80 (mem_map)
  0xc0028eac: add      r3, r8, #0x40000000
  0xc0028eb0: lsr      r3, r3, #0xc
  0xc0028eb4: ldr      r2, [sp]
  0xc0028eb8: ldr      r1, [r1]
  0xc0028ebc: add      r3, r1, r3, lsl #5
  0xc0028ec0: ands     sl, r3, #3
  0xc0028ec4: beq      #0xc0028ed4
  0xc0028ec8: ldr      r0, [pc, #0x18c]       ; *(0xc002905c)=0xc03a52f9
  0xc0028ecc: mov      r1, #0x3f
  0xc0028ed0: bl       #0xc0031098
  0xc0028ed4: and      r2, r2, #3
  0xc0028ed8: mov      r0, r7
  0xc0028edc: orr      r3, r3, r2
  0xc0028ee0: mov      r2, #0x67              ; hash exact 103 bytes (hdr[0:0x67])
  0xc0028ee4: str      r3, [sp]
  0xc0028ee8: lsl      r3, r8, #0x14
  0xc0028eec: str      r2, [sp, #8]
  0xc0028ef0: mov      r1, sp
  0xc0028ef4: lsr      r3, r3, #0x14
  0xc0028ef8: str      r3, [sp, #4]
  0xc0028efc: ldr      r3, [sp, #0x10]
  0xc0028f00: ldr      r3, [r3, #8]
  0xc0028f04: blx      r3                     ; crypto_hash_update
  0xc0028f08: subs     r4, r0, #0
  0xc0028f0c: beq      #0xc0028f28
  0xc0028f10: ldr      r0, [pc, #0x148]       ; *(0xc0029060)=0xc03a535b ("<3>crypto_hash_update failure: %d\n")
  0xc0028f14: mov      r1, r4
  0xc0028f18: mov      r8, sl
  0xc0028f1c: bl       #0xc0313cd4
  0xc0028f20: mov      r7, sl
  0xc0028f24: b        #0xc0029010
  0xc0028f28: ldr      r3, [sp, #0x10]
  0xc0028f2c: mov      r0, r7
  0xc0028f30: mov      r1, r5
  0xc0028f34: ldr      r3, [r3, #0xc]
  0xc0028f38: blx      r3                     ; crypto_hash_final
  0xc0028f3c: subs     r4, r0, #0
  0xc0028f40: ldrne    r0, [pc, #0x11c]       ; *(0xc0029064)=0xc03a537e ("<3>crypto_hash_final failure: %d\n")
  0xc0028f44: bne      #0xc0028f14
  0xc0028f48: mov      r0, #0x80
  0xc0028f4c: bl       #0xc01894b8            ; mpi_alloc(128)
  0xc0028f50: subs     r7, r0, #0
  0xc0028f54: ldreq    r0, [pc, #0x10c]       ; *(0xc0029068)=0xc03a53a0 ("<3>Failed to allocate signature memory.\n")
  0xc0028f58: beq      #0xc0028f74
  0xc0028f5c: add      r1, r8, #0x67          ; hdr + 0x67 = 128-byte signature S
  0xc0028f60: mov      r2, #0x80
  0xc0028f64: bl       #0xc0189820            ; mpuint_setbytes(sig_mpi, hdr+0x67, 128)
  0xc0028f68: subs     r7, r0, #0
  0xc0028f6c: bne      #0xc0028f84
  0xc0028f70: ldr      r0, [pc, #0xf4]        ; *(0xc002906c)=0xc03a53c9 ("<3>Failed to set signature bytes.\n")
  0xc0028f74: bl       #0xc0313cd4
  0xc0028f78: mov      sl, r7
  0xc0028f7c: mov      r8, r7
  0xc0028f80: b        #0xc0029010
  0xc0028f84: mov      r1, sb                 ; e = 3
  0xc0028f88: mov      r2, fp                 ; N (1024-bit modulus)
  0xc0028f8c: bl       #0xc0189f2c            ; rsa_encryptdecrypt(sig_mpi, e, N) -> S^3 mod N
  0xc0028f90: subs     r8, r0, #0
  0xc0028f94: bne      #0xc0028fa8
  0xc0028f98: ldr      r0, [pc, #0xd0]        ; *(0xc0029070)=0xc03a53ec ("<3>rsa_encryptdecrypt failure\n")
  0xc0028f9c: mov      sl, r8
  0xc0028fa0: bl       #0xc0313cd4
  0xc0028fa4: b        #0xc0029010
  0xc0028fa8: bl       #0xc0189600            ; mpuint_trim(out_mpi)
  0xc0028fac: subs     r8, r0, #0
  0xc0028fb0: bne      #0xc0028fc4
  0xc0028fb4: ldr      r0, [pc, #0xb8]        ; *(0xc0029074)=0xc03a540b ("<3>mpuint_trim failure\n")
  0xc0028fb8: mov      sl, #0
  0xc0028fbc: bl       #0xc0313cd4
  0xc0028fc0: b        #0xc0029010
  0xc0028fc4: mov      r0, #0x20
  0xc0028fc8: bl       #0xc01894b8            ; mpi_alloc(32)
  0xc0028fcc: subs     sl, r0, #0
  0xc0028fd0: ldreq    r0, [pc, #0xa0]        ; *(0xc0029078)=0xc03a5423 ("<3>Failed to allocate digest integer memory.\n")
  0xc0028fd4: beq      #0xc0028ff0
  0xc0028fd8: mov      r1, r5                 ; r5 = sha256(hdr[0:0x67])
  0xc0028fdc: mov      r2, #0x20
  0xc0028fe0: bl       #0xc0189820            ; mpuint_setbytes(digest_mpi, sha256, 32)
  0xc0028fe4: subs     sl, r0, #0
  0xc0028fe8: bne      #0xc0028ff8
  0xc0028fec: ldr      r0, [pc, #0x88]        ; *(0xc002907c)=0xc03a5451 ("<3>Failed to set digest bytes.\n")
  0xc0028ff0: bl       #0xc0313cd4
  0xc0028ff4: b        #0xc0029010
  0xc0028ff8: mov      r0, r8
  0xc0028ffc: mov      r1, sl
  0xc0029000: bl       #0xc01897c4            ; mpuint_equal(out_mpi, digest_mpi)
  0xc0029004: cmp      r0, #0
  0xc0029008: movne    r4, #0                 ; EQUAL -> return 0 (PASS)
  0xc002900c: mvneq    r4, #0                 ; NOT EQUAL -> return -1 (FAIL)
  0xc0029010: mov      r0, sl
  0xc0029014: bl       #0xc0189530            ; mpuint_delete(digest_mpi)
  0xc0029018: mov      r0, r8
  0xc002901c: bl       #0xc0189530            ; mpuint_delete(out_mpi)
  0xc0029020: mov      r0, r7
  0xc0029024: bl       #0xc0189530            ; mpuint_delete(sig_mpi)
  0xc0029028: mov      r0, r5
  0xc002902c: bl       #0xc00a1a0c            ; kfree(digest_buf)
  0xc0029030: mov      r0, r6
  0xc0029034: mov      r1, r6
  0xc0029038: bl       #0xc017d280            ; crypto_free_tfm
  0xc002903c: mov      r0, r4
  0xc0029040: add      sp, sp, #0x1c
  0xc0029044: pop      {r4, r5, r6, r7, r8, sb, sl, fp, pc}
```

### B.2.3 Complete `dm_mount_root_nfsb` & `populate_table_nfsb` (`0xc00095d4..0xc000998c` & `0xc0224404..0xc0224654`)

```arm
; dm_mount_root_nfsb (protects rfsA/rfsB /dev/mtdblock6/7):
  0xc00095d4: ldr      r3, [pc, #0x3b4]       ; *(0xc0009990)=0xc046a8d4
  0xc00095d8: push     {r4, r5, r6, r7, r8, sb, sl, fp, lr}
  0xc00095dc: mov      r5, r0                 ; root dev_t
  0xc00095e0: sub      sp, sp, #0x34
  0xc00095e4: ldr      r0, [r3, #0x20]
  0xc00095e8: cmp      r0, #0
  0xc00095ec: beq      #0xc0009604
  0xc00095f0: mov      r1, #0xd0
  0xc00095f4: bl       #0xc00a26f0            ; kmem_cache_alloc(0xe7 NFSB hdr)
  0xc00095f8: subs     r4, r0, #0
  0xc00095fc: bne      #0xc0009614
  0xc0009600: b        #0xc000960c
  0xc0009604: mov      r4, #0x10
  0xc0009608: b        #0xc0009614
  0xc000960c: ldr      r0, [pc, #0x380]       ; *(0xc0009994)=0xc03a50a9 ("Failed to allocate NFSB header struct.")
  0xc0009610: b        #0xc00097a8
  0xc0009614: ldr      r0, [pc, #0x37c]       ; *(0xc0009998)=0xc03a50d0 ("<6>Checking for NFSB mount.\n")
  0xc0009618: bl       #0xc0313cd4
  0xc000961c: ldr      r0, [pc, #0x378]       ; *(0xc000999c)=0xc03a50ed ("/dev/nfsb")
  0xc0009620: bl       #0xc00b2698            ; sys_unlink("/dev/nfsb")
  0xc0009624: lsr      r2, r5, #0x14
  0xc0009628: and      r3, r5, #0xff
  0xc000962c: ldr      r0, [pc, #0x368]       ; "/dev/nfsb"
  0xc0009630: movw     r1, #0x6180
  0xc0009634: orr      r2, r3, r2, lsl #8
  0xc0009638: ldr      r3, [pc, #0x360]       ; 0x000fff00
  0xc000963c: and      r3, r5, r3
  0xc0009640: orr      r2, r2, r3, lsl #12
  0xc0009644: bl       #0xc00b2564            ; create_dev("/dev/nfsb", root_dev)
  0xc0009648: cmp      r0, #0
  0xc000964c: bge      #0xc000965c
  0xc0009650: ldr      r0, [pc, #0x34c]       ; "<3>nfsb: create_dev failed\n"
  0xc0009654: bl       #0xc0313cd4
  0xc0009658: b        #0xc00097a4
  0xc000965c: mov      r1, #0
  0xc0009660: ldr      r0, [pc, #0x334]       ; "/dev/nfsb"
  0xc0009664: mov      r2, r1
  0xc0009668: bl       #0xc00a535c            ; filp_open("/dev/nfsb", O_RDONLY)
  0xc000966c: subs     sl, r0, #0
  0xc0009670: bge      #0xc0009684
  0xc0009674: ldr      r1, [pc, #0x320]       ; "/dev/nfsb"
  0xc0009678: ldr      r0, [pc, #0x328]       ; "<3>nfsb: open %s failed\n"
  0xc000967c: bl       #0xc0313cd4
  0xc0009680: b        #0xc000979c
  0xc0009684: mov      r1, r4
  0xc0009688: bl       #0xc0029080            ; nfsb_read_header(fp, hdr)
  0xc000968c: cmn      r0, #1
  0xc0009690: bne      #0xc00096a4
  0xc0009694: ldr      r1, [pc, #0x300]       ; "/dev/nfsb"
  0xc0009698: ldr      r0, [pc, #0x30c]       ; "<3>nfsb: check %s header fail\n"
  0xc000969c: bl       #0xc0313cd4
  0xc00096a0: b        #0xc0009794
  0xc00096a4: mov      r0, #0x80
  0xc00096a8: bl       #0xc01894b8            ; mpi_alloc(128)
  0xc00096ac: subs     r7, r0, #0
  0xc00096b0: ldreq    r0, [pc, #0x2f8]       ; "<3>out of memory\n"
  0xc00096b4: beq      #0xc00096d0
  0xc00096b8: ldr      r1, [pc, #0x2f4]       ; *(0xc00099b4)=0xc04292f0 (128B BE exponent e = 3)
  0xc00096bc: mov      r2, #0x80
  0xc00096c0: bl       #0xc0189820            ; mpuint_setbytes(e_mpi, 0xc04292f0, 128)
  0xc00096c4: subs     r7, r0, #0
  0xc00096c8: bne      #0xc00096d8
  0xc00096cc: ldr      r0, [pc, #0x2e4]       ; "<3>mpuint_setbytes failed\n"
  0xc00096d0: bl       #0xc0313cd4
  0xc00096d4: b        #0xc000978c
  0xc00096d8: mov      r0, #0x80
  0xc00096dc: bl       #0xc01894b8            ; mpi_alloc(128)
  0xc00096e0: subs     r8, r0, #0
  0xc00096e4: ldreq    r0, [pc, #0x2c4]       ; "<3>out of memory\n"
  0xc00096e8: beq      #0xc0009720
  0xc00096ec: ldr      r1, [pc, #0x2c8]       ; *(0xc00099bc)=0xc0429370 (128B BE modulus N)
  0xc00096f0: mov      r2, #0x80
  0xc00096f4: bl       #0xc0189820            ; mpuint_setbytes(n_mpi, 0xc0429370, 128)
  0xc00096f8: subs     r8, r0, #0
  0xc00096fc: ldreq    r0, [pc, #0x2b4]       ; "<3>mpuint_setbytes failed\n"
  0xc0009700: beq      #0xc0009720
  0xc0009704: mov      r0, r4
  0xc0009708: mov      r1, r7
  0xc000970c: mov      r2, r8
  0xc0009710: bl       #0xc0028df8            ; nfsb_rsa_check(hdr, e_mpi, n_mpi)
  0xc0009714: subs     r6, r0, #0
  0xc0009718: beq      #0xc0009730            ; 0 -> PASS
  0xc000971c: ldr      r0, [pc, #0x29c]       ; *(0xc00099c0)=0xc03a505c ("<3>nfsb: header verification failed\n")
  0xc0009720: bl       #0xc0313cd4
  0xc0009724: mov      r0, r8
  0xc0009728: bl       #0xc0189530
  0xc000972c: b        #0xc000978c
  0xc0009730: ldr      r1, [pc, #0x264]       ; "/dev/nfsb"
  0xc0009734: ldr      r0, [pc, #0x288]       ; *(0xc00099c4)=0xc03a5081 ("<6>%s: NFSB header found and verified.\n")
  0xc0009738: bl       #0xc0313cd4
  0xc000973c: mov      r0, r8
  0xc0009740: bl       #0xc0189530            ; free n_mpi
  0xc0009744: mov      r0, r7
  0xc0009748: bl       #0xc0189530            ; free e_mpi
  0xc000974c: mov      r0, sl
  0xc0009750: bl       #0xc00a3fc0            ; filp_close
  0xc0009754: mov      r0, r4
  0xc0009758: str      r6, [sp, #0x2c]
  0xc000975c: str      r6, [sp, #0x28]
  0xc0009760: bl       #0xc0028d44            ; nfsb_fs_offset() -> r8 (4096B)
  0xc0009764: mov      r8, r0
  0xc0009768: mov      r0, r4
  0xc000976c: bl       #0xc0028d6c            ; nfsb_fs_size()   -> sl
  0xc0009770: add      r1, sp, #0x2c
  0xc0009774: mov      sl, r0
  0xc0009778: mov      r0, r6
  0xc000977c: bl       #0xc02203ac            ; dm_create(&md)
  0xc0009780: cmp      r0, #0
  0xc0009784: beq      #0xc00097b8
  0xc0009788: b        #0xc00097ac
  0xc000978c: mov      r0, r7
  0xc0009790: bl       #0xc0189530
  0xc0009794: mov      r0, sl
  0xc0009798: bl       #0xc00a3fc0
  0xc000979c: ldr      r0, [pc, #0x1f8]       ; "/dev/nfsb"
  0xc00097a0: bl       #0xc00b2698
  0xc00097a4: ldr      r0, [pc, #0x21c]       ; "No NFSB image found."
  0xc00097a8: bl       #0xc0313b4c
  0xc00097ac: ldr      r0, [pc, #0x218]       ; "<3>Failed to create mapped device\n"
  0xc00097b0: bl       #0xc0313cd4
  0xc00097b4: b        #0xc0009974
  0xc00097b8: ldr      r0, [sp, #0x2c]
  0xc00097bc: bl       #0xc0221188
  0xc00097c0: mov      r1, #1
  0xc00097c4: bl       #0xc0194360
  0xc00097c8: mov      r1, #1
  0xc00097cc: add      r0, sp, #0x28
  0xc00097d0: mov      r2, r1
  0xc00097d4: ldr      r3, [sp, #0x2c]
  0xc00097d8: bl       #0xc0221d44            ; dm_table_create(&t, FMODE_READ)
  0xc00097dc: cmp      r0, #0
  0xc00097e0: beq      #0xc00097f4
  0xc00097e4: ldr      r0, [pc, #0x1e4]       ; "<3>Failed to create table\n"
  0xc00097e8: mov      r6, #0
  0xc00097ec: bl       #0xc0313cd4
  0xc00097f0: b        #0xc000996c
  0xc00097f4..0xc0009810: alloc 256B target params buf r7
  0xc0009814: mov      r0, r4
  0xc0009818: lsr      sb, r8, #9             ; sb = fs_offset_sectors (8)
  0xc000981c: lsr      r8, sl, #9             ; r8 = fs_size_sectors (100112)
  0xc0009820: mov      r6, r7
  0xc0009824: bl       #0xc0028dbc            ; nfsb_hash_type() (2)
  0xc0009828: mov      r2, r0
  0xc000982c: mov      r0, r4
  0xc0009830: str      r2, [sp, #0x24]
  0xc0009834: bl       #0xc0028dc4            ; nfsb_hash_algo() ("md5")
  0xc0009838: mov      fp, r0
  0xc000983c: mov      r0, r4
  0xc0009840: bl       #0xc0028dcc            ; nfsb_hash_block_sectors() (8)
  0xc0009844: mov      sl, r0
  0xc0009848: mov      r0, r4
  0xc000984c: bl       #0xc0028df0            ; nfsb_hash_digest() ("6cc5d821...")
  0xc0009850: ldr      r2, [sp, #0x24]
  0xc0009854: mov      r1, #0x100
  0xc0009858: ldr      r3, [pc, #0x13c]       ; *(0xc000999c)=0xc03a50ed ("/dev/nfsb")
  0xc000985c: str      sb, [sp]               ; arg2: payload_start sec = 8
  0xc0009860: add      sb, r8, sb             ; hash_start = fs_size_sectors + fs_offset_sectors
  0xc0009864: str      r2, [sp, #0xc]         ; arg5: bht_depth = 2
  0xc0009868: str      r0, [sp, #0x18]        ; arg8: root_digest
  0xc000986c: mov      r0, r7
  0xc0009870: ldr      r2, [pc, #0x15c]       ; *(0xc00099d4)=0xc03a5166 ("%s %u %s %u %u %s %u %s")
  0xc0009874: stmib    sp, {r3, sb}           ; arg3: hash_dev, arg4: hash_start
  0xc0009878: asr      sb, r8, #0x1f
  0xc000987c: str      fp, [sp, #0x10]        ; arg6: "md5"
  0xc0009880: str      sl, [sp, #0x14]        ; arg7: block_sectors = 8
  0xc0009884: bl       #0xc01a1c30            ; snprintf(params, 256, "%s %u %s %u %u %s %u %s", ...)
  0xc0009888: ldr      r0, [sp, #0x28]
  0xc000988c: mov      r2, #0
  0xc0009890: ldr      r1, [pc, #0x140]       ; *(0xc00099d8)=0xc03a517e ("verity")
  0xc0009894: mov      r3, #0
  0xc0009898: strd     r8, sb, [sp]
  0xc000989c: str      r7, [sp, #8]
  0xc00098a0: bl       #0xc0221ff8            ; dm_table_add_target(t, "verity", 0, fs_size_sec, params)
  0xc00098a4: cmp      r0, #0
  0xc00098a8: ldrne    r0, [pc, #0x12c]       ; "<3>Failed to add NFSB target to the table\n"
  0xc00098ac: bne      #0xc0009908
  0xc00098b0: ldr      r0, [sp, #0x28]
  0xc00098b4: bl       #0xc0222290            ; dm_table_complete(t)
  0xc00098b8: cmp      r0, #0
  0xc00098bc: ldrne    r0, [pc, #0x11c]       ; "<3>Failed to complete NFSB table\n"
  0xc00098c0: bne      #0xc0009908
  0xc00098c4: ldr      r0, [sp, #0x2c]
  0xc00098c8: mov      r1, #2
  0xc00098cc: bl       #0xc0220d04            ; dm_suspend(md, DM_SUSPEND_LOCKFS_FLAG)
  0xc00098d0: cmp      r0, #0
  0xc00098d4: ldrne    r0, [pc, #0x108]       ; "<3>Failed to suspend the device pre-bind\n"
  0xc00098d8: bne      #0xc0009908
  0xc00098dc: ldr      r0, [sp, #0x2c]
  0xc00098e0: ldr      r1, [sp, #0x28]
  0xc00098e4: bl       #0xc0220b28            ; dm_swap_table(md, t)
  0xc00098e8: cmp      r0, #0
  0xc00098ec: ldrne    r0, [pc, #0xf4]        ; "<3>Failed to bind the device to the table\n"
  0xc00098f0: bne      #0xc0009908
  0xc00098f4: ldr      r0, [sp, #0x2c]
  0xc00098f8: bl       #0xc0220f3c            ; dm_resume(md)
  0xc0009948: ldr      r0, [pc, #0xa0]        ; *(0xc00099f0)=0xc03a5247 ("<6>dm: target '%s' of size %llu on %s...")
  0xc0009964: bl       #0xc0313cd4

; populate_table_nfsb (0xc0224404..0xc0224658): handles `dmsetup ... "0 0 verity /dev/mtdblock9"`
  0xc0224404: push     {r4, r5, r6, r7, r8, sb, sl, fp, lr}
  0xc0224408: add      r2, r1, r2
  0xc022440c: sub      sp, sp, #0x134
  0xc0224410: mov      sb, r0                 ; dm_table* t
  0xc0224414: mov      r6, r1                 ; dm_ioctl* param
  0xc0224418: str      r2, [sp, #0x3c]
  0xc022441c: ldr      r2, [r1, #0x14]        ; target_count
  0xc0224420: ldr      r3, [r1, #0x10]
  0xc0224424: cmp      r2, #0
  0xc0224428: movne    r2, r1
  0xc022442c: movne    sl, #0
  0xc0224430: addne    r5, sp, #0x40
  0xc0224434: bne      #0xc0224638
  0xc0224480: add      r8, r4, #0x18          ; dm_target_spec.target_type
  0xc0224484: ldr      r1, [pc, #0x1d8]       ; *(0xc0224664)=0xc03a517e ("verity")
  0xc0224488: mov      r0, r8
  0xc022448c: mov      r2, #7
  0xc0224490: bl       #0xc019f4cc            ; strcmp(target_type, "verity")
  0xc0224494: cmp      r0, #0
  0xc0224498: bne      #0xc0224600            ; standard non-NFSB target if not "verity"
  0xc022449c: ldr      r2, [r4, #8]           ; target_spec.sector_start + length lo/hi
  0xc02244a0: ldr      r3, [r4, #0xc]
  0xc02244a4: orrs     r3, r2, r3
  0xc02244a8: bne      #0xc0224600            ; standard verity if caller passed explicit nonzero length!
  0xc02244ac: add      r0, sp, #0x12c
  0xc02244b0: add      r1, sp, #0x128
  0xc02244b4: mov      r2, r7
  0xc02244b8: bl       #0xc0221edc            ; split userspace param "/dev/mtdblock9"
  0xc02244d0: ldr      r3, [sp, #0x128]
  0xc02244d4: mov      r0, r5
  0xc02244d8: ldr      r1, [r3]
  0xc02244dc: bl       #0xc0028bd0            ; read + RSA-1024 check NFSB header from /dev/mtdblock9!!
  0xc02244f4: mov      r0, r5
  0xc02244f8: bl       #0xc0028d44            ; nfsb_fs_offset() >> 9
  0xc02244fc: lsr      r0, r0, #9
  0xc0224500: str      r0, [sp, #0x34]
  0xc0224504: mov      r0, r5
  0xc0224508: bl       #0xc0028d6c            ; nfsb_fs_size() >> 9
  0xc022450c: ldr      lr, [pc, #0x15c]
  0xc0224510: lsr      r0, r0, #9
  0xc022451c: str      r0, [sp, #0x38]
  0xc0224520: strd     r2, r3, [r4]
  0xc0224524: mov      r2, r0
  0xc0224528: asr      r3, r2, #0x1f
  0xc022452c: strd     r2, r3, [r4, #8]       ; patch dm_target_spec.length = fs_size_sectors
  0xc0224558: bl       #0xc0028dbc            ; nfsb_hash_type()
  0xc0224564: bl       #0xc0028dc4            ; nfsb_hash_algo()
  0xc0224574: bl       #0xc0028dcc            ; nfsb_hash_block_sectors()
  0xc0224584: bl       #0xc0028df0            ; nfsb_hash_digest()
  0xc0224598: add      ip, lr, r3             ; hash_start = fs_size_sec + fs_offset_sec (190144)
  0xc02245c0: ldr      r2, [pc, #0xac]        ; *(0xc0224674)=0xc03a5166 ("%s %u %s %u %u %s %u %s")
  0xc02245c4: stmib    sp, {fp, ip}
  0xc02245c8: bl       #0xc01a1c30            ; format complete verity params string
  0xc02245e4: bl       #0xc0221ff8            ; dm_table_add_target(t, ...)
  0xc0224648: bl       #0xc0222290            ; dm_table_complete(t)
```

---

## B.3 DLM Container & Installer State Machine (`libmtkapp.so` & `libdtv_common.so`)

Verifying [`evidence/03_upg_installer_disasm.txt`](../evidence/03_upg_installer_disasm.txt) (lines 1–416):

### B.3.1 `libmtkapp.so` String Anchors & `PMTD[0..20]` Table (`0x5b0b54..0x5b0c0c`)

```text
  0x5ae80c: b'nand_%d'
  0x5b0ba4: b'mtd10'
  0x5aedf8: b'smth'
  0x5af0f0: b'tar zxf %s -C %s 2>/dev/null'
  0x5af0c0: b'/ro_data/smarthome/'
  0x554e08: b'mkdir %s'
  0x5ae918: b'Upgrade NG'
  0x5afbd4: b'Upgrade Successful'

  PMTD[ 0]..PMTD[13] @ 0x5b0b54..0x5b0bbc : 'mtd0' .. 'mtd13'
  PMTD[14]..PMTD[20] @ 0x5b0bc4..0x5b0c0c : 'mtdsdm14' .. 'mtdsdm20'
```

### B.3.2 Full `sub_404f28` Device Path Builder (`0x404f28..0x405040`)

```arm
  0x404f28: push     {r4, r5, r6, r7, r8, lr}
  0x404f2c: mov      r8, r0                 ; out_dev_path buffer
  0x404f30: mov      r6, r1                 ; METHOD enum (0=PART, 1=PMTD, 2=PSDM, 4=EEP)
  0x404f34: mov      r7, r2                 ; partition index (<PATH2>)
  0x404f38: sub      sp, sp, #0x68
  0x404f3c: add      r5, sp, #0x5c
  0x404f40: ldr      r4, [pc, #0x104]       ; GOT rel
  0x404f50: bl       #0x10b3b4              ; memset(tmp, 0, 12)
  0x404f54: cmp      r6, #0
  0x404f58: add      r4, pc, r4
  0x404f5c: beq      #0x404fa4              ; r6 == 0 (PART) -> "/dev/nand_%d" (BROKEN: -22 ENOENT!)
  0x404f60: cmp      r6, #1
  0x404f64: beq      #0x404fd4              ; r6 == 1 (PMTD) -> PMTD[r7] ("/dev/mtd10")
  0x404f68: cmp      r6, #2
  0x404f6c: beq      #0x404fbc              ; r6 == 2 (PSDM) -> "/dev/sdm%d"
  0x404f70: cmp      r6, #4
  0x404f74: bne      #0x405008              ; else log error @ line 0xaf3 and return -1
  0x404f88: bl       #0xfc0fc               ; snprintf("eeprom_%d", r7)
  0x404f94: bl       #0xfcb10               ; strcpy("/dev/", dev)
  ...
  0x404fd4: ldr      r1, [pc, #0x80]
  0x404fe4: bl       #0x10ce48              ; init PMTD[0..22] array on stack
  0x404fe8: cmp      r7, #0x16              ; bounds check <= 22
  0x404fec: bhi      #0x405028
  0x404ffc: ldr      r1, [r7, #-0x68]       ; PMTD[r7]
  0x405000: bl       #0xff624               ; strcpy(tmp, PMTD[r7])
  0x405004: b        #0x404f8c
```

### B.3.3 `sub_4074c0` & `sub_407d4c` Safe `METHOD=FILE` Extractor (`0x4074f8..0x408190`)

```arm
; sub_4074c0 (archive tool selector):
  0x407504: ldr      r1, [pc, #0xa4]        ; -> 0x5af0c0: b'/ro_data/smarthome/'
  0x407524: ldr      r1, [pc, #0x88]        ; -> 0x5af0f0: b'tar zxf %s -C %s 2>/dev/null'
  0x407544: ldr      r0, [pc, #0x70]        ; -> 0x5af110: b"[PHM_UPG] <%s> tar from '%s' to '%s'\n"
  0x407590: ldr      r1, [pc, #0x2c]        ; -> 0x5af0d4: b'busybox unzip -oq %s -d %s'

; sub_407d4c (cleanup + mkdir + tar dispatch):
  0x407db8: ldr      r1, [pc, #0x8cc]       ; -> 0x554970: b'rm -rf %s'
  0x407e80: ldr      r2, [pc, #0x820]       ; -> 0x5aecc8: b'/tmp/upgrade'
  0x407e90: ldr      r1, [pc, #0x814]       ; -> 0x554e08: b'mkdir %s'
  0x4080a4: ldr      r1, [pc, #0x624]       ; -> 0x5aede0: b'demo'
  0x4080c0: ldr      r1, [pc, #0x60c]       ; -> 0x567368: b'logo'
  0x4080dc: ldr      r1, [pc, #0x5f4]       ; -> 0x5aedf8: b'smth'
  0x40815c: ldr      r1, [pc, #0x548]       ; -> 0x554e08: b'mkdir %s' (non-recursive!)
```

### B.3.4 `libmtkapp.so` Raw 33-Byte Key Loader & `3rdp` Dual-Bank Skip (`0x4060d0..0x4061b0`, `0x40ae50..0x40af20`)

```arm
; Key loader (0x4060d0..0x4061b0):
  0x4060d0: bl       #0xfca38               ; c_dlm_set_rsa_public_key(...PubKey_Prod.pem)
  0x4060e4: bl       #0x405eb0              ; get_file_size("...AES_Prod.key") -> 33 bytes (hex + '\n')
  0x406108: bl       #0x107e50              ; malloc(33)
  0x406120: bl       #0x108180              ; fread(key_buf, 1, 33, fp)
  0x406134: bl       #0x10dea4              ; fclose
  0x40613c: bl       #0x405eb0              ; get_file_size("...AES_Prod.iv") -> 33 bytes
  0x40615c: bl       #0x107e50              ; malloc(33)
  0x406174: bl       #0x108180              ; fread(iv_buf, 1, 33, fp)
  0x406188: bl       #0x10dea4              ; fclose
  0x40619c: bl       #0x10d118              ; c_dlm_set_aes_key_iv(key_buf, 33, iv_buf, 33)

; _phm_upg_model_start_upgrade bank switch skip (0x40ae50..0x40aeec):
  0x40ae5c: ldrb     r3, [r5, #0x67d]       ; ENABLE flag
  0x40ae68: ldrb     r3, [r5, #0x67c]       ; match flag
  0x40ae74: ldr      r3, [r5, #0x570]       ; METHOD
  0x40ae78: cmp      r3, #2
  0x40ae7c: bhi      #0x40b7f4
  0x40ae94: bl       #0xfcef4               ; strncmp(tag, "3rdp", 4)
  0x40ae98: cmp      r0, #0
  0x40ae9c: beq      #0x40aed8              ; SKIP bank-toggle flags when tag == "3rdp"!
  0x40aea0: ldr      r3, [r5, #0x678]       ; 0=kern, 1=rfs, 2=logo, 3=sign
  0x40aeac: streq    r3, [sp, #0x18]        ; bank toggle A
  0x40aeb8: streq    r3, [sp, #0x24]        ; bank toggle B
```

### B.3.5 `libdtv_common.so` Full `dlm_locate_codefile_hdr` & `x_dlm_download_by_tag` (`0x098b60..0x098cdc` & `0x0995b4..0x099694`)

```arm
; dlm_locate_codefile_hdr (constructs K_mtk = 0x94102909*4, decrypts & validates #DH@FiRm):
  0x098b60: push     {r4, r5, r6, r7, r8, sb, sl, fp, lr}
  0x098b64: movw     r3, #0x2909
  0x098b68: ldr      r4, [pc, #0x20c]
  0x098b6c: sub      sp, sp, #0x4c
  0x098b70: add      r5, sp, #0x34
  0x098b74: movt     r3, #0x9410            ; r3 = 0x94102909 (09 29 10 94 LE)
  0x098b78: ldr      r7, [pc, #0x200]
  0x098b7c: add      sl, sp, #0x24
  0x098b80: add      r4, pc, r4             ; r4 = GOT
  0x098b84: add      r6, sp, #0x44
  0x098b88: mov      sb, r0
  0x098b8c: mov      fp, r1
  0x098b90: add      r7, r4, r7
  0x098b94: mov      r1, #0
  0x098b98: ldr      ip, [r7, #4]
  0x098b9c: mov      r2, #0x10
  0x098ba0: str      r3, [sp, #0x44]
  0x098ba4: mov      r0, sl
  0x098ba8: add      r3, r5, #8
  0x098bac: str      ip, [sp, #0x10]
  0x098bb0: add      ip, r5, #4
  0x098bb4: str      r3, [sp, #0x18]
  0x098bb8: str      ip, [sp, #0x14]
  0x098bbc: bl       #0x379d0               ; memset(IV_mtk, 0, 16)
  0x098bc0: add      ip, r5, #0xc
  0x098bc4: mov      r1, r6
  0x098bc8: mov      r2, #4
  0x098bcc: mov      r0, r5
  0x098bd0: str      ip, [sp, #0x1c]
  0x098bd4: bl       #0x3845c               ; memcpy key[0..4]   = 09 29 10 94
  0x098bd8: mov      r1, r6
  0x098bdc: mov      r2, #4
  0x098be0: ldr      r0, [sp, #0x14]
  0x098be4: bl       #0x3845c               ; memcpy key[4..8]   = 09 29 10 94
  0x098be8: mov      r1, r6
  0x098bec: mov      r2, #4
  0x098bf0: ldr      r0, [sp, #0x18]
  0x098bf4: bl       #0x3845c               ; memcpy key[8..12]  = 09 29 10 94
  0x098bf8: mov      r2, #4
  0x098bfc: mov      r1, r6
  0x098c00: ldr      r0, [sp, #0x1c]
  0x098c04: bl       #0x3845c               ; memcpy key[12..16] = 09 29 10 94
  0x098c08: mov      r0, sb
  0x098c0c: mov      r1, fp
  0x098c10: mov      r2, #0x90              ; attempt probe from offset 0x00 (0x70 + 0x20)
  0x098c14: bl       #0x97600
  0x098c18: subs     r8, r0, #0
  0x098c1c: beq      #0x98c2c
  0x098c20: mov      r0, r8
  0x098c24: add      sp, sp, #0x4c
  0x098c28: pop      {r4, r5, r6, r7, r8, sb, sl, fp, pc}
  0x098c2c: ldr      r0, [pc, #0x150]
  0x098c30: add      r0, r4, r0
  0x098c34: bl       #0x367e8
  0x098c38: ldr      r3, [pc, #0x148]
  0x098c3c: mov      r2, #0x70
  0x098c40: ldr      r1, [r7, #4]
  0x098c44: add      ip, r4, r3
  0x098c48: mov      r0, ip
  0x098c4c: str      ip, [sp, #0xc]
  0x098c50: bl       #0x34dcc
  0x098c54: ldr      r0, [r7, #4]
  0x098c58: mov      r3, r5                 ; K_mtk
  0x098c5c: mov      r1, r8
  0x098c60: mov      r2, #0x70              ; 112-byte encrypted DLM header
  0x098c64: str      sl, [sp]               ; IV = 0
  0x098c68: str      r8, [sp, #4]
  0x098c6c: bl       #0x37370               ; dlm_aes_decrypt
  0x098c70: ldr      ip, [sp, #0xc]
  0x098c74: mov      r2, #0x70
  0x098c78: ldr      r1, [r7, #4]
  0x098c7c: mov      r0, ip
  0x098c80: bl       #0x34dcc
  0x098c84: ldr      r3, [sp, #0x10]
  0x098c88: mov      r2, #8
  0x098c8c: add      r0, r3, #4             ; hdr + 4
  0x098c90: ldr      r3, [pc, #0xf4]
  0x098c94: add      r3, r4, r3             ; "#DH@FiRm"
  0x098c98: mov      r1, r3
  0x098c9c: str      r3, [sp, #0x10]
  0x098ca0: bl       #0x3a8a4               ; memcmp(hdr+4, "#DH@FiRm", 8)
  0x098ca4: cmp      r0, #0
  0x098ca8: ldreq    r3, [pc, #0xe0]
  0x098cac: ldreq    r3, [r4, r3]
  0x098cb0: streq    r8, [r3]
  0x098cb4: beq      #0x98c20               ; matched at 0x00 -> return
  0x098cb8: ldr      r0, [pc, #0xd4]
  0x098cbc: add      r0, r4, r0
  0x098cc0: bl       #0x367e8
  0x098cc4: mov      r0, sb
  0x098cc8: mov      r1, fp
  0x098ccc: mov      r2, #0x110             ; retry past 128B prefix ("Autorun.upg")
  0x098cd0: bl       #0x97600
  0x098cd4: subs     r8, r0, #0
  0x098cd8: bne      #0x98c20

; x_dlm_download_by_tag (derives MD5(33B key), MD5(33B iv), verifies chunk header):
  0x0995b4: ldr      r3, [pc, #0x648]
  0x0995b8: ldr      fp, [r4, r3]
  0x0995bc: ldr      r3, [fp]
  0x0995c0: cmp      r3, #0
  0x0995c4: beq      #0x995f8
  0x0995c8: add      r7, r7, #0x1c
  0x0995cc: mov      r0, r7
  0x0995d0: bl       #0x38390               ; MD5_Init(&ctx_key)
  0x0995d4: ldr      r3, [pc, #0x62c]
  0x0995d8: mov      r0, r7
  0x0995dc: ldr      r1, [fp]               ; uc_aes_key (raw 33 bytes!)
  0x0995e0: ldr      r3, [r4, r3]
  0x0995e4: ldr      r2, [r3]               ; i4_aes_key_len (33)
  0x0995e8: bl       #0x39efc               ; MD5_Update
  0x0995ec: mov      r0, r5
  0x0995f0: mov      r1, r7
  0x0995f4: bl       #0x37214               ; MD5_Final -> K_tv (16B)
  0x0995f8: ldr      r3, [pc, #0x60c]
  0x0995fc: ldr      r7, [r4, r3]
  0x099600: ldr      r3, [r7]
  0x099604: cmp      r3, #0
  0x099608: beq      #0x99640
  0x09960c: add      r3, r4, sb
  0x099610: add      fp, r3, #0x1c
  0x099614: mov      r0, fp
  0x099618: bl       #0x38390               ; MD5_Init(&ctx_iv)
  0x09961c: ldr      r3, [pc, #0x5ec]
  0x099620: mov      r0, fp
  0x099624: ldr      r1, [r7]               ; uc_aes_iv (raw 33 bytes!)
  0x099628: ldr      r3, [r4, r3]
  0x09962c: ldr      r2, [r3]               ; i4_aes_iv_len (33)
  0x099630: bl       #0x39efc               ; MD5_Update
  0x099634: mov      r0, r8
  0x099638: mov      r1, fp
  0x09963c: bl       #0x37214               ; MD5_Final -> IV_tv (16B)
  0x099640: mov      ip, #0
  0x099644: add      r7, sl, #0xc           ; chunk descriptor +0x0C (magic)
  0x099648: mov      r1, ip
  0x09964c: mov      r2, #0x10              ; 16 bytes
  0x099650: mov      r3, r5                 ; K_tv
  0x099654: mov      r0, r7
  0x099658: stm      sp, {r8, ip}           ; IV_tv
  0x09965c: bl       #0x37370               ; decrypt magic field
  0x099660: ldr      r1, [pc, #0x5ac]
  0x099664: mov      r0, r7
  0x099668: mov      r2, #0x10
  0x09966c: add      r1, r4, r1             ; "reserved mtk inc"
  0x099670: bl       #0x3a8a4               ; memcmp == "reserved mtk inc"
  0x099674: subs     r7, r0, #0
  0x099678: bne      #0x99d84               ; invalid chunk marker -> fail
  0x09967c: add      r0, sl, #0x1c          ; chunk descriptor +0x1C (SHA-256)
  0x099680: mov      r1, r7
  0x099684: mov      r2, #0x20              ; 32 bytes
  0x099688: mov      r3, r5                 ; K_tv
  0x09968c: str      r8, [sp]               ; fresh IV_tv!
  0x099690: str      r7, [sp, #4]
  0x099694: bl       #0x37370               ; decrypt expected payload SHA-256
```

---

## B.4 Userland Control Flow: `SystemManager`, `dtv_svc` & `libnettv.so` (`evidence/06`)

### B.4.1 `SystemManager` `main`, `SMConfig` & `dynqml` Branches (`0x1619e4`, `0x16e428`, `0x1db58c`, `0x1db7a4`)

```arm
; SystemManager main base directory store:
  0x1619e4: push     {r4, r5, r6, r7, r8, sb, sl, lr}
  0x161a00: ldr      r0, [r6]               ; argv[0] ("/3rd/qt/AEDK/SystemManager/SystemManager")
  0x161a14: bl       #0x16ee4               ; QFileInfo(argv[0])
  0x161a44: bl       #0x17e44               ; dir()
  0x161a54: bl       #0x175ec               ; absolutePath()
  0x161a58: ldr      r0, [pc, #0x6d8]       ; *(0x162138)->0x910aac global appDir

; SMConfig constructor:
  0x16e434: bl       #0x16ab8               ; load global appDir
  0x16e458: ldr      r1, [pc, #0x474]       ; *(0x16e8d4)->0x258878 b'/sm_config.ini'
  0x16e478: bl       #0x18468               ; concat -> "/3rd/qt/AEDK/SystemManager/sm_config.ini"

; dynqml selector:
  0x1db58c: bl       #0x16e958              ; query SMConfig [tpvlib] dynqml
  0x1db590: cmp      r0, #0
  0x1db594: bne      #0x1db7a4              ; dynqml==true -> filesystem QML branch
  0x1db598: ldr      r0, [pc, #0x978]       ; *(0x1dbf18)->0x25e824 b'qrc:/HomeScreen/HSMain.qml'
  0x1db5fc: ldr      r1, [pc, #0x918]       ; *(0x1dbf1c)->0x25e840 b'2closeHS(int)'
  0x1db61c: ldr      r1, [pc, #0x900]       ; *(0x1dbf24)->0x25e860 b'2launch(int)'
  ...
  0x1db7ac: bl       #0x16ab8               ; appDir
  0x1db7d0: ldr      r1, [pc, #0x79c]       ; *(0x1dbf74)->0x25e808 b'/res/HomeScreen/HSMain.qml'
```

### B.4.2 `dtv_svc` `sys_start.c` Provisioning Guard (`0x036190..0x036314`)

```arm
  0x036190: ldr      r0, [pc, #0x364]       ; *(0x364fc)->0x3316bc b'sh /etc/scripts/mount_3rd_rw.sh'
  0x036194: ldr      r6, [pc, #0x364]       ; *(0x36500)->0x3316dc b'/dev/mtd12'
  0x03619c: bl       #0x319e8               ; execute shell mount
  0x0361cc: ldr      sl, [pc, #0x330]       ; *(0x36504)->0x3316e8 b'/3rd_rw'
  0x0361d4: ldr      sb, [pc, #0x32c]       ; *(0x36508)->0x3316f0 b'/3rd_rw/upgrade/customer_version'
  0x03628c: bl       #0x30a40               ; open("/3rd_rw/upgrade/customer_version")
  0x036290: cmp      r0, #0
  0x036294: beq      #0x363c0               ; exists -> KEEP /3rd_rw/nettv intact across boots!
  0x036298: cmn      r0, #6
  0x03629c: bne      #0x35e20
  0x0362a0: ldr      r0, [pc, #0x264]       ; *(0x3650c)->0x331714 b'rm -rf /3rd_rw/nettv/opera;'
  0x0362a8: bl       #0x34618
  0x0362b4: ldr      r0, [pc, #0x254]       ; *(0x36510)->0x331730 b'mkdir -p /3rd_rw/nettv/opera;'
  0x0362bc: bl       #0x34618
  0x0362c8: ldr      r0, [pc, #0x244]       ; *(0x36514)->0x331750 b'cp -rf /3rd/nettv/opera/* /3rd_rw/nettv/opera;'
  0x0362d0: bl       #0x34618
  0x0362dc: bl       #0x32564               ; sync()
  0x036300: bl       #0x30a40               ; create /3rd_rw/upgrade/customer_version
```

### B.4.3 `libnettv.so` `_imnettv_copydata` INI & Cert Override (`0x188b48..0x188d1c`)

```arm
  0x188b4c: ldr      r0, [pc, #0x5ec]       ; *(0x189140)->0x249c1b b'mkdir /tmp/opera_home'
  0x188b50: bl       #0xa4cd4
  0x188b54: ldr      r0, [pc, #0x5e8]       ; *(0x189144)->0x249c31 b'cp -f /usr/opera/opera_home/*  /tmp/opera_home'
  0x188b58: bl       #0xa4cd4
  0x188ba8: ldr      r0, [pc, #0x5a0]       ; *(0x189150)->0x249cca b'rm -f /mnt/browser/opssl6.dat'
  0x188bac: bl       #0xa4cd4
  0x188bb0: ldr      r0, [pc, #0x59c]       ; *(0x189154)->0x249ce8 b'cp -f /mnt/browser/op*.dat  /tmp/opera_home; sync'
  0x188bb4: bl       #0xa4cd4
  0x188bf8: ldr      r0, [pc, #0x55c]       ; *(0x18915c)->0x249d6e b'cp -f /mnt/browser/op*.pem  /tmp ; sync'
  0x188bfc: bl       #0xa4cd4
  0x188c40: ldr      r0, [pc, #0x51c]       ; *(0x189164)->0x249ddf b'chmod 666 /tmp/opera_home/* '
  0x188c44: bl       #0xa4cd4
  0x188c58: ldr      r0, [pc, #0x508]       ; *(0x189168)->0x249dfc b'[%d:%s]> [P]========>>YTLB certification support, opera.ini R/W\n'
  0x188c74: ldr      r0, [pc, #0x4f0]       ; *(0x18916c)->0x249e3d b'/3rd_rw/nettv/opera_new.ini'
  0x188c7c: bl       #0xa6744               ; access("/3rd_rw/nettv/opera_new.ini", F_OK)
  0x188c80: cmp      r0, #0
  0x188c84: bne      #0x188d10              ; absent -> retain default stock opera.ini
  0x188cb4: ldr      r0, [pc, #0x4b8]       ; *(0x189174)->0x249eb0 b'cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync'
  0x188cb8: bl       #0xa4cd4               ; system()
  0x188cc0: ldr      r0, [pc, #0x4b0]       ; *(0x189178)->0x249ef3 b'chmod 666 /tmp/opera_home/opera.ini'
  0x188cc4: bl       #0xa4cd4               ; system()
  0x188d10: ldr      r0, [pc, #0x464]       ; *(0x18917c)->0x249f17 b'7,NETTV'
```
