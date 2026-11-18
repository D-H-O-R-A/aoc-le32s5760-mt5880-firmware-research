# Filesystem Service Dependency & IPC Map

> **Visual Dependency Diagram:** [diagrams/SOFTWARE_DEPENDENCIES.svg](../diagrams/SOFTWARE_DEPENDENCIES.svg)

## 1. Service Startup Dependency Chain (`/sbin/init` -> `SystemManager`)

Inspecting `appfs1/etc/inittab`, `appfs1/etc/init.d/rcS`, `appfs1/etc/rc.d/rc.local`, `appfs1/etc/scripts/*.sh`, and `appfs1/basic/autorun.sh` reconstructs the exact service startup graph:

```
[/sbin/init (BusyBox v1.15.3)]
  ├── respawns -> /sbin/mnet_down.script   (monitors /tmp/interface_down -> ifconfig down)
  └── sysinit  -> /etc/init.d/rcS
        ├── source /etc/profile            (9 LD_LIBRARY_PATHs, TRUSTZONE=enable, SYS_BRAND=Philips)
        ├── /bin/mount -avt nonfs,nosmbfs  (mounts proc, sysfs, tmpfs on /tmp, /opt, /var/run)
        ├── [optional] busybox readahead `cat /etc/readahead_early` &
        └── /etc/rc.d/rc.local
              ├── sh /etc/scripts/init_all.sh
              │     ├── mount_3rd.sh (or dmverity_mount_3rda/3rdb -> /3rd via dm-1)
              │     ├── mount_perm.sh (ubiattach -m 11 -d 2 -> /perm)
              │     └── ins_usb_core_mod.sh + ins_wifi_mod.sh + ins_basic_mod.sh
              ├── sh /etc/scripts/ubi_mount_3rd_rw.sh (ubiattach -m 12 -d 4 -> /3rd_rw)
              ├── sh /etc/scripts/mount_ro_data.sh    (ubiattach -m 13 -d 3 -> /ro_data)
              └── sh /basic/autorun.sh
                    ├── insmod /basic/dtv_driver.ko & /basic/fusion.ko
                    └── exec /basic/dtv_svc &
                          ├── initializes /3rd_rw/nettv (unless customer_version exists)
                          ├── launches Qt SystemManager -> HSMain.qml (+ SMConfig dynqml hook)
                          └── launches on-demand: Opera (/3rd/nettv/opera), Netflix (nrd-app), Ginga, dialserver
```

---

## 2. Inter-Process Communication (IPC) & Shared-Library Dependencies

| Consumer Process | IPC / Library Interface | Provider Component |
|---|---|---|
| **SystemManager (Qt UI)** | DirectFB / Fusion IPC (`fusion.ko` `/dev/fusion/*`) & `libmtkapp.so` / `libapp_if_rpc.so` | `dtv_svc` hardware control & upgrade engine |
| **SystemManager -> Opera** | `libnettv_proxy.so` <-> `libnettv.so` (`_imnettv_copydata`, `browser.out`) | Merges `/3rd_rw/nettv` overrides into `/tmp/opera_home` |
| **DIAL Server (`dialserver`)** | HTTP REST on loopback (`http://localhost:56789/dialData?...`) & SSDP multicast on LAN | Triggers YouTube / Netflix launches via `SystemManager` / Opera |
| **Ginga Middleware (SBTVD)** | `libgingacoreccipcservices.so`, `libbalglue.so`, `libcommoncore-loader.so`, `libcurl.so.4` (`OpenSSL 1.0.0d`) | Broadcast ISDB-Tb interactive Java/NCL/Lua apps |
| **Software Upgrade (`libmtkapp.so`)** | Calls `libdtv_common.so` (`dlm_locate_codefile_hdr`, `x_dlm_integrity_check`) + `c_fm_erase_flash_part` + `nor/eeprom_hw.c` | Reads `/ro_data` `.pem`/`.key`/`.iv` & erases/writes `/dev/mtd*` |
| **Network Control** | `/tmp/interface_down` trigger file watched every `0.5s` by `mnet_down.script`; `udhcpc` + `dibbler-client` (`/etc/scripts/dhcpv6.sh`) | Drops/configures `eth0` and `ra0` |
