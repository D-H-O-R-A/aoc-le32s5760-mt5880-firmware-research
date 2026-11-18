# Component Dependency Analysis (`LD_LIBRARY_PATH` & ABI Supply Chain)

> **Dependency Vector Graph:** [diagrams/SOFTWARE_DEPENDENCIES.svg](../diagrams/SOFTWARE_DEPENDENCIES.svg)

## 1. Multi-Path Dynamic Linker Graph (`etc/profile`)

Reviewing `/etc/profile` reveals why the runtime userland carries overlapping copies of third-party libraries across `/lib`, `/basic/lib`, `/3rd/lib`, and `/3rd/ginga/lib`:

```text
LD_LIBRARY_PATH resolution order:
  /basic
  -> /basic/lib
  -> /basic/lib/alsa-lib-1.0.24.1/lib
  -> /3rd/lib
  -> /3rd/AdobeAIR/stagecraft-2.5.1.340/lib
  -> /3rd/flash_lite/lib
  -> /3rd/yahoo_widget
  -> /3rd/lib/iconv/lib
  -> /3rd/netflix/flash-app/lib
  -> /3rd/gtkdfb/lib
  -> /3rd/libxml2/libxml2-2.7.8/lib
  -> /3rd/mtal
  -> /3rd/browser_engine
  -> /3rd/bin/wpa_supplicant/ralink
```

Because `/basic/lib` precedes `/3rd/*` in `LD_LIBRARY_PATH`, core system libraries in `rfsA` (`OpenSSL 1.0.0d`, `libcurl 4.2.0`, `libexpat 1.5.2`) override or compete with duplicate builds inside `3rd/ginga/lib` (compiled separately by Fundação CERTI against `/home/local/CERTI/vtz/Projects/envision_middleware_clean/third_party/curl-7.21.7/../openssl-1.0.0d`) unless binaries encode explicit `RPATH` entries!

---

## 2. Transitive Supply-Chain Bottlenecks

1. **`OpenSSL 1.0.0d` Single Point of TLS Failure:** Shared across `libcurl 7.21.7`, `QtNetwork 4.8.3` (`QT_NO_OPENSSL` check or OpenSSL backend), `Ginga`, `dialserver`/DRM helpers, and `dtv_svc`. Upgrading `OpenSSL` independently inside `/3rd_rw` **cannot** transparently upgrade `1.0.0d` consumers because `OpenSSL 1.1.x`/`3.x` broke ABI compatibility (`SONAME libcrypto.so.1.0.0` vs `.1.1`/`.3`) and opaque struct access (`EVP_MD_CTX`, `X509_STORE`).
2. **`glibc 2.12.2` + `GCC 4.5.1` ABI Ceiling:** Any modern prebuilt ARM binary compiled against `glibc >= 2.17` (`GLIBC_2.17` symbol versioning, e.g., modern Chromium, Node.js, modern `ffmpeg`/`curl`) immediately fails dynamic loading against `/lib/libc-2.12.2.so` (`ELF` symbol mismatch), requiring static linking (which breaks `512 MB` RAM budgets and NAND `50-97 MB` SquashFS limits).
3. **`zlib 1.2.3` & `libpng 1.2.43` Cross-Cut:** Every GUI (`SystemManager`), web engine (`Opera`), Java/Lua runtime (`Ginga`), and media thumbnailer relies directly or transitively on the same 2005–2010 compression/image parsers.
