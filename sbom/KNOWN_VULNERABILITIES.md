# Known Vulnerability Exposure Analysis (`Legacy SBOM CVE Audit`)

> **Epistemic Constraint:** Static firmware version matching identifies **historical upstream CVE ranges** affecting shipped library versions (`2005–2012` era codebases compiled in `2016`). Because upstream source patch status (backports vs. vanilla builds) and runtime network call-site reachability cannot be dynamically verified without OEM source code or live fuzzing, CVEs below are strictly labeled **Upstream Version Match (Patch Backport / Reachability Unverified)**.

---

## 1. High-Priority Legacy Component CVE Mapping

| Component | Shipped Version | Confirmed Reference CVEs Affecting Upstream Version Series | Technical Risk Class | Observed File |
|---|---|---|---|---|
| **OpenSSL** | `1.0.0d` (Feb 2011; fixed `CVE-2011-0014`) | Post-`1.0.0d` `1.0.0` branch advisories (fixed later up to `1.0.0r`): `CVE-2015-0285`, `CVE-2015-0286`, `CVE-2015-0287`, `CVE-2015-0288`, `CVE-2015-0289`, `CVE-2015-0291`, `CVE-2015-0292`, `CVE-2015-0293`, `CVE-2015-3195`, `CVE-2016-0704` *(Note: Heartbleed `CVE-2014-0160` affected `1.0.1–1.0.1f`, NOT `1.0.0d`)* | ASN.1 memory corruption, TLS fallback/oracle flaws, DoS | `appfs1/basic/lib/libssl.so.1.0.0` |
| **Linux Kernel** | `3.0.13` (Dec 2011; EoL) | `CVE-2012-3375` (`fs/eventpoll.c` `epoll_ctl` `ELOOP` DoS), `CVE-2013-0313` (EVM `sockfs` NULL deref) + hundreds of post-2011 local/network bugs | Kernel DoS / privilege escalation primitives | `scratch/vmlinux.bin` |
| **`glibc`** | `2.12.2` (Dec 2010) | `CVE-2011-0536` (`elf/dl-object.c` untrusted search path) + pre-backport resolver bugs depending on patch state | Dynamic loader / resolver memory flaws | `appfs1/lib/libc-2.12.2.so` |
| **`libcurl`** | `7.21.7` (2011) | Over `80` cumulative curl advisories spanning `7.21.x` lifecycle (e.g., `CVE-2019-5436` TFTP heap overflow and subsequent TLS/cookie/wildcard flaws) | Client HTTP/FTP/TLS parsing memory corruption | `rootfs1/ginga/lib/libcurl.so.4.2.0` |
| **`libxml2`** | `2.7.8` (Nov 2010) | `CVE-2010-4494` (XPath double-free), `CVE-2010-4008` (out-of-bounds read), `CVE-2012-0841` (hash collision DoS), `CVE-2012-2807` | Crafted XML / SOAP / UPnP RCE or DoS (`dial`/`dlna`) | `rootfs1/lib/libxml2.so.2.7.8` |
| **`expat`** | `2.0.1` (Jun 2007) | `CVE-2009-3720` (malformed UTF-8 XML DoS) + decade of XML entity/integer overflow patches pre-`2.4+` | Crafted XML parser crash / DoS | `appfs1/basic/lib/libexpat.so.1.5.2` |
| **`zlib`** | `1.2.3` (Jul 2005) | `CVE-2016-9840`, `CVE-2016-9841`, `CVE-2016-9842` (pointer arithmetic UB/corruption), `CVE-2022-37434` (`inflate` heap overflow on large extra fields) | Decompression heap overflow across HTTP/PNG | `appfs1/lib/libz.so.1.2.3` |
| **`BusyBox`** | `1.15.3` (2009) | Legacy applet parsing issues affecting pre-1.35 lines (e.g., `udhcp`/`awk`/`netstat` classes such as `CVE-2022-28391` in unpatched shells/net utilities) | Applet / DHCP script parsing risks | `appfs1/bin/busybox` |

---

## 2. Contextual Mitigation Notes

1. **Exploitability Depends on Reachability:** For example, `CVE-2010-4494` (`libxml2`) only becomes remotely triggerable if untrusted LAN/WAN XML reaches vulnerable XPath APIs inside `libqtdlna.so`, `opera`, or `ginga`, while `CVE-2012-3375` (`epoll_ctl`) requires local code execution first.
2. **Defense-in-Depth Impact (`SEC-01`):** Because every daemon runs as `root` (`UID 0`) without SELinux/AppArmor, **any** reachable memory corruption across `libxml2`, `expat`, `zlib`, `libcurl`, or `OpenSSL` bypasses application boundaries completely unless network interfaces are segmented on an isolated VLAN.
