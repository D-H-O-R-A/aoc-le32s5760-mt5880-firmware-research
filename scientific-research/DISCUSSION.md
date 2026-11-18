# Discussion: Architectural Trade-Offs, Preservation Limits & Industry Implications

## 1. Security-vs-Maintenance Paradox in Early Smart TVs

The empirical decomposition of `AOC LE32S5760/20` illustrates a structural paradox common to 2012–2016 consumer Smart TVs:
1. **Rigid Protection Against Owner Modification:** MediaTek and TPV deployed multi-stage cryptography (OTP hardware eFuses, dual kernel RSA-2048 trailers, `NFSB` RSA-1024 + `36,281`-block `dm-bht` Merkle trees) specifically designed to prevent unauthorized custom firmware persistence (`DRM`/certification compliance).
2. **Neglected Runtime Defense & Maintenance:** Once verified code boots, all daemons—including the obsolete `OpenSSL 1.0.0d` / `libcurl 7.21.7` / Opera `Presto 6213` browser (`opcacrt6.pem` already holding `9` expired CAs at release time)—execute unsandboxed as `root` without `/etc/shadow`, while factory distribution `upgrade_loader.pkg#part:roda` leaked `LT0_UPG_PriKey_Prod.pem` (`SEC-02`).

## 2. Why Full Custom ROM Porting Is Unfeasible Without Hardware Recovery

Combined hardware and ABI constraints preclude running Chromium, modern Netflix (`NRD >= 2020`), or modern TLS `1.3` streaming apps inside this platform:
- **Boot Lock Risk Without Programmer:** Modifying `load`, `ker`, `rfs`, or `3rd` risks permanent brick (`0xfb000520` halt loop or unmountable root) that cannot be repaired via USB without an external NAND chip programmer and BGA/TSOP rework gear.
- **CPU/Memory/ABI Ceiling:** Rebuilding modern C++17+ browsers onto `GCC 4.5.1` / `glibc 2.12.2` / `Linux 3.0.13` ARMv7 within a tight embedded DRAM budget (~`512 MB` inferred) and fixed NAND partitions (`51.4 MB` / `97.7 MB`) hits insurmountable dependency and footprint walls (`dtv_driver.ko` `6.84 MB` proprietary binary blob locks the kernel to `3.0.13`).

## 3. Constructive Preservation Engineering (`mtd12` `/3rd_rw` Boundary)

Stopping destructive flash writes cleanly once the lock boundary is proven demonstrates **safe, reproducible preservation methodology**: moving customization cleanly to `<TAG>smth</TAG><METHOD>FILE</METHOD>` on `mtd12` (`/3rd_rw`) lets researchers explore `SystemManager` QML (`SMConfig` `dynqml`) and Opera Presto hardening (`opera_new.ini`, `urlfilter.ini`, ES5 `user.js`) with **zero modification to signed RO flash**, repurposing aging CE televisions safely as isolated HDMI displays or digital tuners rather than e-waste bricks.
