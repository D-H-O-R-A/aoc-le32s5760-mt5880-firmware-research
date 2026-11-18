# Open-Source & Proprietary License Compliance Review

> **Related Governance Document:** [../LEGAL_AND_LICENSE_REVIEW.md](../LEGAL_AND_LICENSE_REVIEW.md)

## 1. License Distribution Across Tracked Target Components

| License Family (SPDX Identifier) | Identified Firmware Components | Compliance Status / Observations |
|---|---|---|
| **`GPL-2.0-only` / `GPL-2.0-or-later`** | `Linux 3.0.13` kernel, `BusyBox v1.15.3`, `fuse.ko`, `ntfs.ko`, `fusion.ko`, `met.ko`, `joydev.ko`, `usbhid.ko`, `rtnet5572sta.ko`, `rtutil5572sta.ko`, `ntfs-3g`, `iptables 1.4.15` | Copyleft binaries ship inside `rfsA`/`3rdA`; no OEM GPL corresponding source tarball was bundled inside `LE32S5760_V2.011_V0.2.zip` (**MISSING_OEM_SOURCE_OFFER_IN_ZIP**). |
| **`LGPL-2.1-only` / `LGPL-2.1-or-later`** | `glibc 2.12.2`, `Qt 4.8.3` (likely LGPL or commercial; exact election undocumented), `alsa-lib 1.0.24.1`, `libfuse 2.8.4`, `DirectFB 1.4.1`, `libdevmapper 1.02`, `libmicrohttpd`, `FFmpeg/libav*` (`ginga/lib`) | Dynamically linked `.so` libraries; `Qt` uses shared linkage alongside `Opera` & proprietary `dtv_svc`. |
| **`MIT` / `BSD` / `Zlib` / `curl` / `OpenSSL` / `BSL-1.0` / `Apache-2.0` / `blessing`** | `libxml2 2.7.8` (`MIT`), `expat 2.0.1` (`MIT`), `c-ares` (`MIT`), `libwebp` (`BSD-3`), `zlib 1.2.3` (`Zlib`), `libcurl 7.21.7` (`curl`), `OpenSSL 1.0.0d` (`OpenSSL`), `Boost 1.44.0` (`BSL-1.0`), `Xerces-C 3.1` (`Apache-2.0`), `SQLite 3.7.2` (`blessing`), `libtomcrypt`/`libtommath` (`Public Domain/WTFPL`) | Permissive licenses requiring attribution notices (many shipped notices omitted in headless flash FS). |
| **`Proprietary / NOASSERTION`** | `dtv_driver.ko` (`Proprietary`), `mtk_mmap.ko` (`Proprietary`), `rt5572sta.ko`, `Opera Presto 6213`, Netflix `nrd-app`, `PlayReady`, `Widevine`, `Marlin`, `Adobe AIR Stagecraft`, `Spotify` | Strictly proprietary; none of these binaries or DRM keys are redistributed in Git. |

---

## 2. Copyleft Kernel Boundary Note (`dtv_driver.ko` vs. `GPL`)

Inspecting `.modinfo` records across all `12` kernel modules ([KERNEL_MODULE_INVENTORY.csv](../kernel-analysis/KERNEL_MODULE_INVENTORY.csv)) confirms that MediaTek cleanly segregates:
- **GPL modules** (`fusion.ko`, `fuse.ko`, `ntfs.ko`, `usbhid.ko`, `joydev.ko`, `met.ko`, `rtnet5572sta.ko`, `rtutil5572sta.ko`), vs.
- **Proprietary modules** (`dtv_driver.ko`, `mtk_mmap.ko`), which taint the kernel on load with non-GPL symbols. Note also `rt5572sta.ko` omits a `license=` tag cleanly inside its parsed `.modinfo` match while companion wrapper `rtnet5572sta.ko` marks `license=GPL`.
