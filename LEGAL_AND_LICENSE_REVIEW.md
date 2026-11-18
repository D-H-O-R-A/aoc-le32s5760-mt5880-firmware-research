# Legal and Open-Source License Review

## 1. Repository Licensing (`MIT`) vs. Analyzed Target Components

All original documentation, Python verification scripts, SVG diagrams, SBOM manifests, test suites, and original `custom_payload` configuration scripts authored for this research repository are released under the **MIT License** ([LICENSE](LICENSE)).

Analyzed third-party and OEM software inside the target firmware (not redistributed in this repository) spans mixed proprietary and copyleft/permissive licenses. Researchers and device auditors must observe their separation cleanly.

## 2. Licensing Inventory of Target Firmware Subsystems

| Subsystem | Examples in Target Firmware | Observed License(s) | Verification Evidence |
|---|---|---|---|
| **Linux Kernel & Standard Modules** | `Linux 3.0.13`, `fuse.ko`, `ntfs.ko`, `fusion.ko`, `met.ko`, `joydev.ko`, `usbhid.ko`, `rtnet5572sta.ko`, `rtutil5572sta.ko` | **GPLv2** | `.modinfo` `license=GPL` strings in ELF sections; standard kernel tree paths |
| **Proprietary Silicon Kernel Drivers** | `dtv_driver.ko`, `mtk_mmap.ko`, `rt5572sta.ko` | **Proprietary / Non-GPL** (`Proprietary`, `RALINK`, etc.) | `.modinfo` `license=Proprietary` on `dtv_driver.ko` & `mtk_mmap.ko` |
| **BusyBox & GNU System Libraries** | `BusyBox v1.15.3`, `glibc 2.12.2`, `libstdc++ 6.0.14` | **GPLv2** / **LGPLv2.1+** / **GPLv3 w/ GCC Runtime Exception** | Observed binaries & standard toolchain banners (`GCC 4.5.1`) |
| **Qt Application Framework** | `libQtCore.so.4.8.3`, `libQtDeclarative.so.4.8.3`, `libQtGui.so.4.8.3`, etc. | **LGPLv2.1 / GPLv3 / Commercial** (version 4.8.3) | `extracted/rootfs1/qt/lib/*` (exact OEM Qt commercial vs LGPL election unknown) |
| **Multimedia, Web & Middleware** | `DirectFB 1.4.1`, `OpenSSL 1.0.0d`, `libcurl 7.21.7`, `libxml2 2.7.8`, `expat 2.0.1`, `sqlite 3.7.2`, `zlib 1.2.3`, `c-ares`, `FFmpeg/libav*` (under `ginga/lib`), `Boost 1.44.0`, `Xerces-C 3.1` | **LGPL**, **MIT**, **OpenSSL/SSLeay**, **curl**, **Boost**, **Apache-2.0**, **Public Domain** (`SQLite`) | Detailed per-component catalog in [sbom/OPEN_SOURCE_LICENSES.md](sbom/OPEN_SOURCE_LICENSES.md) |
| **Commercial DRM / Browser Blobs** | `Opera` (`opera`, `libopera_hbbtv.so`), Netflix (`nrd-app`), PlayReady (`libplayready.so`), Widevine (`libWV*`), Marlin (`libmarlin.so`), Adobe AIR (`stagecraft`), Dolby MS10 | **Commercial Proprietary** | Not redistributed; excluded via [.gitignore](.gitignore) |

## 3. Compliance & Reverse-Engineering Legal Context

1. **Interoperability & Security Research:** Static inspection of locally extracted firmware images owned by the researcher falls within established reverse-engineering exemptions for interoperability, security auditing, and error analysis (cf. US DMCA 17 U.S.C. § 1201(f)/(j), EU Software Directive 2009/24/EC Art. 5(3)/Art. 6, and Brazilian Software Law nº 9.609/98 Art. 6).
2. **GPL Source Availability Note:** Although the target ships GPLv2 components (`Linux 3.0.13` with MediaTek `mach-mt53xx` / `dm-bht` changes, `BusyBox v1.15.3`, `LGPL glibc 2.12.2`), complete OEM OSS source tarballs for `AOC LE32S5760/20` (`V2.011_V0.2`) were not included inside `LE32S5760_V2.011_V0.2.zip` and were **not** obtained or mirrored here (`STATUS: MISSING_UPSTREAM_OSS_TARBALL`). See [sbom/OPEN_SOURCE_LICENSES.md](sbom/OPEN_SOURCE_LICENSES.md).
3. **No Secret or Key Redistribution:** All RSA private keys, AES production keys, and copyrighted binary blobs remain excluded from this repository.
