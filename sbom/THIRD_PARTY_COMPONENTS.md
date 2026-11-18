# Third-Party Components Inventory (`SBOM` Analysis)

> **Machine-Readable SBOMs:** [SBOM.spdx.json](SBOM.spdx.json) (`SPDX-2.3`, `27` packages) | [SBOM.cdx.json](SBOM.cdx.json) (`CycloneDX 1.5`, `26` components)

## 1. Verified Core Third-Party Components

Every version listed below was directly observed from shared library filenames, linker banners, or embedded ELF version strings inside `extracted/appfs1`, `extracted/rootfs1`, and `scratch/vmlinux.bin`. Where only SONAME ABI digits were observable without a point-release string, uncertainty is explicitly marked (`INFERRED_SONAME`).

| Component | Observed Version | Status | Primary Evidence Artifact | Role in Firmware |
|---|---|---|---|---|
| **Linux Kernel** | `3.0.13` (`#1 SMP PREEMPT`) | Confirmed | `scratch/vmlinux.bin` | Core ARMv7-A OS kernel (`mach-mt53xx` BSP) |
| **GNU C Library (`glibc`)** | `2.12.2` | Confirmed | `appfs1/lib/libc-2.12.2.so` | C runtime (`GCC 4.5.1` built) |
| **GNU `libstdc++`** | `6.0.14` | Confirmed | `appfs1/lib/libstdc++.so.6.0.14` | C++ standard runtime (`Qt`, `Ginga`, `Opera`, `Netflix`) |
| **BusyBox** | `1.15.3` (`2012-06-06`) | Confirmed | `appfs1/bin/busybox` | Embedded shell (`ash`), `init`, core CLI applets |
| **OpenSSL** | `1.0.0d` | Confirmed | `appfs1/basic/lib/libssl.so.1.0.0` + `libcurl` build path | TLS/crypto across `curl`, `ginga`, `dtv_svc`, DRM |
| **`curl` / `libcurl`** | `7.21.7` | Confirmed | `rootfs1/ginga/lib/libcurl.so.4.2.0` (`libcurl/7.21.7`) | HTTP/HTTPS transfers |
| **Qt Application Framework** | `4.8.3` | Confirmed | `rootfs1/qt/lib/libQtCore.so.4.8.3` (+Gui/Declarative/Network/Script/Sql/Xml) | Smart TV `SystemManager` QML (`QtQuick 1.1`) shell |
| **DirectFB & Fusion** | `1.4.1` | Confirmed | `appfs1/lib/libdirectfb-1.4.so.0` + `fusion.ko` | Hardware-accelerated OSD compositing & IPC |
| **`libxml2`** | `2.7.8` | Confirmed | `rootfs1/lib/libxml2.so.2.7.8` | XML parsing (`ginga`, `dlna`, upgrade XML) |
| **`expat`** | `2.0.1` | Confirmed | `appfs1/basic/lib/libexpat.so.1.5.2` (`expat_2.0.1`) | Lightweight XML parsing (`Qt` / `fontconfig` / middleware) |
| **`zlib`** | `1.2.3` | Confirmed | `appfs1/lib/libz.so.1.2.3` | Inflate/deflate compression across codecs & HTTP |
| **`libpng`** | `1.2.43` | Confirmed | `appfs1/lib/libpng12.so.0.1.2.43` | PNG rendering (`SystemManager` QML / Opera / Ginga) |
| **`sqlite`** | `3.7.2` | Confirmed | `appfs1/basic/lib/libsqlite_3_7_2.so` | Embedded local database storage |
| **`alsa-lib`** | `1.0.24.1` | Confirmed | `appfs1/basic/lib/alsa-lib-1.0.24.1/` | Audio PCM / mixer control |
| **`libfuse`** | `2.8.4` | Confirmed | `appfs1/basic/lib/libfuse.so.2.8.4` | Userspace FUSE layer for USB filesystems |
| **`ntfs-3g`** | ABI `76` (`libntfs-3g.so.76.0.0`) | Inferred (`SONAME`) | `appfs1/basic/lib/libntfs-3g.so.76.0.0` | USB NTFS read/write support |
| **Boost C++** | `1.44.0` | Confirmed | `rootfs1/ginga/lib/libboost_*.so.1.44.0` | Ginga ISDB-Tb C++ middleware |
| **Apache Xerces-C++** | `3.1` | Confirmed | `rootfs1/lib/libxerces-c-3.1.so` | Schema-validating XML parser for Ginga / DRM |
| **`FreeType`** | `libfreetype.so.6.6.1` / `6.6.2` | Inferred (`SONAME`) | `appfs1/lib` & `rootfs1/ginga/lib` | TrueType font rendering |
| **`libjpeg`** | `62.0.0` (IJG `6b` ABI) | Confirmed | `appfs1/lib/libjpeg.so.62.0.0` | JPEG decoding |
| **`libiconv`** | `2.4.0` / `2.5.0` | Inferred (`SONAME`) | `rootfs1/lib/libiconv.so.2.4.0` & `ginga/lib` | Character set transcoding |
| **`LVM2 device-mapper`** | `1.02` | Confirmed | `appfs1/lib/libdevmapper.so.1.02` + `dmsetup` | Userspace setup of `dm-verity` `dm-1` (`/3rd`) |
| **`c-ares`**, **`libmicrohttpd`**, **`libwebp`**, **`FFmpeg`**, **`Live555`**, **`libtomcrypt`**, **`libtommath`**, **`Thrift`**, **`iptables`** | Various (`so2.0.0`, `so10`, `4.0.1`, `libavcodec 53`, `iptables 1.4.15`, etc.) | Mixed | Listed cleanly in `FILESYSTEM_INVENTORY.csv` | Asynchronous DNS, DIAL HTTP, WebP images, media decode, crypto math |
| **Proprietary Commercial SDKs** | Opera `Presto 6213`, Netflix `NRD`, PlayReady, Widevine, Marlin, Adobe AIR `2.5.1.340`, Spotify `libspotify.so.12`, Dolby MS10 | Confirmed Presence | Excluded binaries mapped in `SBOM.spdx.json` (`NOASSERTION` license) | Closed vendor applications & DRM engines |
