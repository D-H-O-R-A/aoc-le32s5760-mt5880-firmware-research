# Proposed Emulation Environment Specification (Blueprint & Local Status)

## 1. Local Host Verification Status

| Tool / Component | Status in Analysis Environment | Notes |
|---|---|---|
| **Python `3.x` (`Capstone`, `hashlib`, `struct`)** | **INSTALLED & EXECUTED** | Executed all 7 proof scripts + inventory/SBOM/comparison suites |
| **OpenSSL CLI & Node.js** | **INSTALLED & EXECUTED** | Verified RSA-2048/AES-128-CBC signatures & `custom_payload` ES5 JS syntax |
| **GNU `binutils` (`readelf`, `objdump`)** | **INSTALLED** | Inspected ELF headers & sections |
| **`qemu-arm-static` / `qemu-system-arm`** | **NOT INSTALLED / NOT EXECUTED** | No QEMU ARM binaries in local container; user-mode & full-system QEMU specs below are architectural blueprints only |

---

## 2. Reproducible User-Mode Emulation Blueprint (For Off-Host ARM Lab Hosts)

Researchers deploying QEMU on an external Linux workstation can prepare a sysroot from the extracted firmware without executing untrusted network binaries natively:

1. **Extract & Strip `NFSB` Headers:**
   - Remove the leading `231`-byte (`0xe7`) `NFSB` header from `rfsA` (`mtd6`) and `3rdA` (`mtd9`), unpack via `unsquashfs`, and merge `rootfs1` at `<sysroot>/3rd`.
   - **Never copy FIFO `dev/initctl` or raw host `/dev` into untrusted scripts blindly**; create static dummy nodes (`/dev/null`, `/dev/zero`, `/dev/urandom`) inside the sysroot.
2. **Emulate Static Library Paths (`/etc/profile` Mirror):**
   - Supply `QEMU_LD_PREFIX=<sysroot>` and `LD_LIBRARY_PATH` mirroring all `9` paths in `appfs1/etc/profile` (`/basic:/basic/lib:/3rd/lib:/3rd/qt/lib:/3rd/nettv:/3rd/ginga/lib`).
3. **Mock Hardware / DRM / Key Mounts:**
   - Map `/ro_data`, `/3rd_rw`, and `/perm` cleanly to host temporary directories (`chmod -R u+rw`) so `libdtv_common.so` and `libnettv.so` can resolve config file reads without triggering kernel MTD `ioctl` panics.
4. **Stub Hardware `ioctl` Calls via `LD_PRELOAD`:**
   - Intercept `open("/dev/mtd*")`, `open("/dev/fb0")`, `open("/dev/fusion*")`, and `dtv_driver.ko` custom `ioctl()` numbers, returning deterministic benign descriptors (`-1 ENODEV` or mocked structs) while logging call arguments cleanly (`Fuzzing / protocol inspection only`).
