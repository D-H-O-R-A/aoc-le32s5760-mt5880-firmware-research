# Appendix A — Verified Cryptographic, Binary, Merkle-Tree & Configuration Evidence

This appendix reproduces the complete machine-generated outputs of [`scripts/inspect_pkg_and_nfsb.py`](../scripts/inspect_pkg_and_nfsb.py), [`scripts/verify_upg_container.py`](../scripts/verify_upg_container.py), [`scripts/inspect_runtime_engines.py`](../scripts/inspect_runtime_engines.py), and [`scripts/inspect_dmbht_and_boot_scripts.py`](../scripts/inspect_dmbht_and_boot_scripts.py), alongside the complete remediated `custom_payload/patches/run.sh` and `custom_payload/nettv/opera_new.ini` configuration artifacts delivered on `/3rd_rw/nettv`. All blocks below are verbatim recordings emitted by `./scripts/run_all_proofs.sh`.

---

## A.1 Full PKG Partition Table, `cfig`, Kernel Trailers & `NFSB` RSA-1024 Proof (`evidence/01_pkg_and_nfsb_proof.txt`)

```text
=== MTK PKG Partition Table (upgrade_loader.pkg, 323840461 bytes) ===
Idx  Tag    HeaderOff    PayloadOff   SizeBytes    SizeMB  
------------------------------------------------------------
1    3rdB   0x00000098   0x000000a4   97738752      93.21 MB
2    3rdA   0x05d360a4   0x05d360b0   97738752      93.21 MB
3    roda   0x0ba6c0b0   0x0ba6c0bc   5767168        5.50 MB
4    cfig   0x0bfec0bc   0x0bfec0c8   237            0.00 MB
5    load   0x0bfec1b5   0x0bfec1c1   1314592        1.25 MB
6    uenv   0x0c12d0e1   0x0c12d0ed   2384           0.00 MB
7    adsp   0x0c12da3d   0x0c12da49   1272368        1.21 MB
8    aqda   0x0c264479   0x0c264485   131216         0.13 MB
9    pqda   0x0c284515   0x0c284521   11534336      11.00 MB
10   rfsB   0x0cd84521   0x0cd8452d   51466240      49.08 MB
11   rfsA   0x0fe9952d   0x0fe99539   51466240      49.08 MB
12   kerB   0x12fae539   0x12fae545   2638124        2.52 MB
13   kerA   0x13232671   0x1323267d   2638124        2.52 MB
14   usig   0x134b67a9   0x134b67b5   512            0.00 MB
15   chtD   0x134b69b5   0x134b69c1   65536          0.06 MB
16   chtC   0x134c69c1   0x134c69cd   65536          0.06 MB

=== Embedded NAND Partition Map ('cfig') ===
START -> uenv -> nand -> 1 -> kerA -> nand -> 4 -> kerB -> nand -> 5 -> rfsA -> nand -> 6 -> rfsB -> nand -> 7 -> 3rdA -> nand -> 9 -> 3rdB -> nand -> 10 -> perm -> nand -> 11 -> 3rdw -> nand -> 12 -> roda -> nand -> 13 -> game -> nand -> 14 -> pqda -> nand -> 17 -> aqda -> nand -> 18 -> ddb -> nand -> 26 -> chtC -> nand -> 27 -> chtD -> nand -> 28 -> adsp -> nand -> 29 -> Seur -> nand -> 30 -> END

=== Kernel Image (kerA, 2638124 bytes) ===
  uImage magic: 0x27051956 (0x27051956 = U-Boot uImage)
  Trailer @ 0x25152c..0x25154c: 520ed5dbf9a534ee7adee78a2275a11c141a78d32307f63cfa56082ad312719d
  Trailer @ 0x283f2c..0x283f4c: 4efd77b7d80e4da2b87f0dfeba36d69a941b8ee5855b3de843f2a1fc63057e9e

=== Kernel Image (kerB, 2638124 bytes) ===
  uImage magic: 0x27051956 (0x27051956 = U-Boot uImage)
  Trailer @ 0x25152c..0x25154c: 520ed5dbf9a534ee7adee78a2275a11c141a78d32307f63cfa56082ad312719d
  Trailer @ 0x283f2c..0x283f4c: 4efd77b7d80e4da2b87f0dfeba36d69a941b8ee5855b3de843f2a1fc63057e9e

=== Linux Kernel Embedded NFSB RSA-1024 Key (vmlinux.bin @ VA 0xc0008000, uImage hdr stripped) ===
  uImage Header : magic=0x27051956, payload_size=4432548 B, load=0x00007fc0, ep=0x00008000
  Exponent @ VA 0xc04292f0 (128B BE): e = 3
  Modulus  @ VA 0xc0429370 (128B BE): 1024 bits
  N[:32] = b00a75021d8a006cbb285990f78a8cf517f075b5efbd7dea7009c530045e5202
  N[-32:] = 7d4ebf1ff427ff4e5d14712e38c38285035cea722dd3617fdffdb249f1eb8ab1

=== Mathematical Verification of NFSB Headers (pow(sig, e, N) == 0^96 || SHA256(hdr[0:0x67])) ===
  [3rdB] @ 0x000000a4: magic=NFSB v2, tree_hash='md5', hdr_sha256=7f8488da5bcdda386be1047c91f8bdb50848600d69ee8878c09db130f8277beb
           RSA_dec_upper96_zero=True, RSA_exact_match=True
  [3rdA] @ 0x05d360b0: magic=NFSB v2, tree_hash='md5', hdr_sha256=7f8488da5bcdda386be1047c91f8bdb50848600d69ee8878c09db130f8277beb
           RSA_dec_upper96_zero=True, RSA_exact_match=True
  [rfsB] @ 0x0cd8452d: magic=NFSB v2, tree_hash='md5', hdr_sha256=b9226006f291e7f3c42103e9eb8f90dbc20ffe95125497ba4a6540daa135794d
           RSA_dec_upper96_zero=True, RSA_exact_match=True
  [rfsA] @ 0x0fe99539: magic=NFSB v2, tree_hash='md5', hdr_sha256=b9226006f291e7f3c42103e9eb8f90dbc20ffe95125497ba4a6540daa135794d
           RSA_dec_upper96_zero=True, RSA_exact_match=True

=== Counter-Proof on Modified Package (custom_upgrade_loader.pkg) ===
  [3rdA] size=97738752 bytes, patched hdr[0x18:0x1c]=00000000
  hdr_sha256=b2f9faad420094913c771e9d155d2c11badfd675c53ce9279e2c961ac5311e80
  RSA_dec[-32:]=7f8488da5bcdda386be1047c91f8bdb50848600d69ee8878c09db130f8277beb | RSA_exact_match=False (REJECTED BY KERNEL)
```

---

## A.2 Cryptographic Verification of Safe `/3rd_rw/nettv` Deliverable (`evidence/04_upg_container_crypto_proof.txt`)

```text
File: /home/diegooris/tv-firmware-custom/AOC/LE32S5760/build/Autorun.upg (19905 bytes)
  Outer 128B prefix: 'Autorun.upg'
  [PASS] RSA-2048 PKCS#1 v1.5 signature matches SHA256(data[0x80:-256]) = d425f0dc6da71abc9a43a052ddccec23d6f2992423b7b23a506aa032c57a52a4
  [PASS] DLM Header AES-128-CBC (09291094*4): vendor='TPV', magic=b'#DH@FiRm', id='IDTV0801_002224_9_001_23_001_225', model='LE32S5760/20', body_len=19521, flags=0x0
  [PASS] Body MD5 matches MD5(enc_hdr + 0x00*32 + chunks) = b0b05a0e5385873caf37542dcd150775
  [PASS] Chunk 'ixml': flags=0, len=440, magic='reserved mtk inc', sha256=19ebca2599852ad9700ce01d98536734519c0a93bed467ca62cbaf8bf25d6fb7
  [PASS] Chunk 'smth': flags=0, len=18817, magic='reserved mtk inc', sha256=52c7f99fa479c3c81dc6c38b930d72651c3bf1bc9488078cbb0f50af6976a806

--- Decoded 'ixml' Manifest ---
<?xml version="1.0" encoding="UTF-8"?>
<UPGRADE>
  <SYS_INFO>
    <MANUFACTURER>TPV</MANUFACTURER>
    <MODEL>LE32S5760/20</MODEL>
    <SERIAL_NUM>000000</SERIAL_NUM>
    <MODE>UPG</MODE>
    <VERSION>002.001.205.146</VERSION>
  </SYS_INFO>
  <SW>
    <TAG>smth</TAG>
    <METHOD>FILE</METHOD>
    <PATH>/3rd_rw/nettv</PATH>
    <FILE_NAME>smth</FILE_NAME>
    <VERSION>002.001.205.146</VERSION>
    <ENABLE>YES</ENABLE>
  </SW>
</UPGRADE>
  Parsed <SW>: TAG='smth', METHOD='FILE', PATH='/3rd_rw/nettv'

--- Payload Tarball Entries ---
  - root:root   2463 opera_new.ini
  d root:root      0 browser
  d root:root      0 download
  d root:root      0 custom
  - root:root   1906 custom/urlfilter.ini
  - root:root    775 custom/user.css
  d root:root      0 custom/userjs
  - root:root    517 custom/userjs/google.js
  - root:root    506 custom/userjs/iplayer_rider4-45.js
  - root:root   1629 custom/userjs/legacyKeyHandling.js
  - root:root  10338 custom/userjs/load.js
  - root:root  19987 custom/userjs/ooif.js
  - root:root   6074 custom/userjs/spatnav_youtube.js
  - root:root  25421 custom/userjs/user.js
```

---

## A.3 Runtime Engines, BusyBox & Compliance Audit (`evidence/05_runtime_engines_and_busybox_audit.txt`)

```text
=== 1. Proprietary App Engine Fingerprints ===
  [Opera TV (libopera_hbbtv.so)] (15717224 bytes):
    Opera/9.80 -> ['Opera/9.80 (%s%s%s)', 'Opera/9.80 (%s; Opera TV Store/6213%s%s)']
    20140526 -> ['20140526_1239_jenkins_38e', '20140526_1239_jenkins_b91d']
    Enable TLS v1.1 -> ['Enable TLS v1.1']
    Enable TLS v1.2 -> ['Enable TLS v1.2']
    User JavaScript File -> ['User JavaScript File']
  [Netflix (nrd-app/netflix)] (10201088 bytes):
    OpenSSL 1.0. -> ['OpenSSL 1.0.0d 8 Feb 2011']
    20150420 -> ['20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/chilin', '20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/dtv_li', '20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/oss/li']
    Gibbon -> ['Gibbon Configuration!', 'Gibbon DirectFB surface format options', 'Gibbon DiskCachePath must not be empty!']
  [NetTV Launcher (libnettv.so)] (2749744 bytes):
    /3rd_rw/nettv/opera_new.ini -> ['/3rd_rw/nettv/opera_new.ini', '/3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync']
    cp -f /3rd_rw/nettv/opera_new.ini -> ['cp -f /3rd_rw/nettv/opera_new.ini /tmp/opera_home/opera.ini ; sync']
  [Service Init (dtv_svc)] (4255100 bytes):
    /3rd_rw/upgrade/customer_version -> ['/3rd_rw/upgrade/customer_version']
    cp -rf /3rd/nettv/opera/* /3rd_rw/nettv/opera -> ['cp -rf /3rd/nettv/opera/* /3rd_rw/nettv/opera;']

=== 2. BusyBox Applet & Binary Inventory (extracted/appfs1/bin) ===
  Count: 73 Tools: agetty, arping, awk, basename, bash, blkid, blkid.static, busybox, cat, chmod, chrt, cp, date, depmod, df, dibbler-client, dirname, dmesg, dmsetup, du, echo, find, fw_printenv, getopt, grep, gzip, head, hostname, ifconfig, insmod, kill, ln, login, losetup, ls, lsmod, mkdir, mknod, modprobe, mount, mount.static, mountpoint, mv, nice, ping, ping6, ps, pwd, reboot, rm, rmmod, route, sed, sh, sleep, sort, stty, sync, sysctl, tar, top, touch, ubiattach, ubidetach, ubiformat, ubimkvol, ubinfo, udhcpc, umount, umount.static, vi, which, xargs
  Check missing pidof     : present=False
  Check missing pgrep     : present=False
  Check missing renice    : present=False
  Check missing ionice    : present=False
  Check missing chown     : present=False
  Check missing killall   : present=False
  Check missing unzip     : present=False
  Check missing python    : present=False
  Check missing python3   : present=False
  Check missing curl      : present=False

=== 3. SystemManager ELF NEEDED & SMConfig Keys ===
  SM string 'sm_config.ini'                @ 0x250879
  SM string 'tpvlib'                       @ 0x2508b8
  SM string 'dynqml'                       @ 0x2508d8
  SM string 'qrc:/HomeScreen/HSMain.qml'   @ 0x256824
  SM string 'res/HomeScreen/HSMain.qml'    @ 0x256809

=== 4. Custom Payload Validation ===
  [PASS] custom_payload/patches/run.sh: sh -n + BusyBox applet compliance
  [PASS] custom_payload/nettv/user.js: node --check passed
  [PASS] 18 custom QML files validated (Latin-1/ASCII safe, balanced braces)
```

---

## A.4 Full `dm-bht` Merkle Proof, Boot Script Audit & `opera.ini` Diff (`evidence/07_dmbht_and_boot_scripts_audit.txt`)

```text
=== NFSB + SquashFS + dm-bht Verification: 3rdA (97,738,752 bytes) ===
  NFSB Header      : version=2, depth=2, algo='md5', blk_sectors=8 (4096 B)
  Geometry         : fs_off=0x1000 (8 sec), fs_size=0x5cd7000 (190136 sec = 23767 x 4KB)
  Hash Tree Size   : 385024 B (752 sec = 94 pages: 1 parent + 93 leaf)
  SquashFS @ 0x1000 : magic=b'hsqs' v4.0, inodes=3305, blk_sz=131072, comp_id=0x110003, used=97,347,681 B
  Leaf MD5 Match   : True (23,767 / 23,767 4KB blocks verified)
  Level-0 Match    : True (93 leaf pages verified, zero-pad=True)
  Signed Root MD5  : 666e1b26ae2e81a681c4f510bd98bfca
  Computed Root    : 666e1b26ae2e81a681c4f510bd98bfca (EXACT MATCH=True)

=== NFSB + SquashFS + dm-bht Verification: rfsA (51,466,240 bytes) ===
  NFSB Header      : version=2, depth=2, algo='md5', blk_sectors=8 (4096 B)
  Geometry         : fs_off=0x1000 (8 sec), fs_size=0x30e2000 (100112 sec = 12514 x 4KB)
  Hash Tree Size   : 204800 B (400 sec = 50 pages: 1 parent + 49 leaf)
  SquashFS @ 0x1000 : magic=b'hsqs' v4.0, inodes=1329, blk_sz=131072, comp_id=0x110003, used=51,255,766 B
  Leaf MD5 Match   : True (12,514 / 12,514 4KB blocks verified)
  Level-0 Match    : True (49 leaf pages verified, zero-pad=True)
  Signed Root MD5  : 6cc5d821e2e914aec01a1db58fcca389
  Computed Root    : 6cc5d821e2e914aec01a1db58fcca389 (EXACT MATCH=True)

=== Boot Script Excerpt: etc/rc.d/rc.local.partial (19 total lines) ===
  L003: echo "Running rc.local..."
  L005: stty -F /dev/ttyMT3 115200
  L007: mkdir /tmp/mnt
  L008: touch /tmp/resolv.conf
  L009: echo "127.0.0.1 localhost.localdomain localhost" > /tmp/hosts
  L011: ifconfig lo 127.0.0.1
  L015: if [ -f /etc/sysctl.conf ];then
  L016:     sysctl -p /etc/sysctl.conf
  L017: fi
  L018: mkdir -p /tmp/lib/dibbler
  L019: mkdir -p /tmp/dibbler

=== Boot Script Excerpt: etc/scripts/dmverity_mount_3rda.sh (96 total lines) ===
  L077: if [ ! -f /tmp/3rd_mounted ]; then
  L078:     echo "# mount 3rd DMVERITY(SquashFS read-only)"
  L079:     dmsetup -r -j 254 -m 1 create dm-1 --table "0 0 verity /dev/mtdblock9"
  L080:     if $TIME mount -t squashfs /dev/mapper/dm-1 /3rd; then
  L081:         touch /tmp/3rd_mounted
  L082:     else
  L083:         echo "error! 3rd partition can't be mounted!!!"
  L084:         exit -1
  L085:     fi
  L086: else
  L087:     echo "3rd partition is already mounted!!!"
  L088: fi
  L090: if [ -f /3rd/skype/auto_detect_camera.sh ]; then
  L091:     if [ ! -f /tmp/auto_detect_camera_started ]; then
  L092:         /3rd/skype/auto_detect_camera.sh &
  L093:         touch /tmp/auto_detect_camera_started
  L094:     fi
  L095: fi

=== Boot Script Excerpt: etc/scripts/dmverity_mount_3rdb.sh (96 total lines) ===
  L077: if [ ! -f /tmp/3rd_mounted ]; then
  L078:     echo "# mount 3rdb DMVERITY(SquashFS read-only)"
  L079:     dmsetup -r -j 254 -m 1 create dm-1 --table "0 0 verity /dev/mtdblock10"
  L080:     if $TIME mount -t squashfs /dev/mapper/dm-1 /3rd; then
  L081:         touch /tmp/3rd_mounted
  L082:     else
  L083:         echo "error! 3rd partition can't be mounted!!!"
  L084:         exit -1
  L085:     fi
  L086: else
  L087:     echo "3rd partition is already mounted!!!"
  L088: fi
  L090: if [ -f /3rd/skype/auto_detect_camera.sh ]; then
  L091:     if [ ! -f /tmp/auto_detect_camera_started ]; then
  L092:         /3rd/skype/auto_detect_camera.sh &
  L093:         touch /tmp/auto_detect_camera_started
  L094:     fi
  L095: fi

=== Boot Script Excerpt: etc/scripts/ubi_mount_3rd_rw.sh (110 total lines) ===
  L082: if [ ! -f /tmp/3rd_rw_attached ]; then
  L083:     echo "# mount 3rd_rw"
  L084:     if $TIME ubiattach /dev/ubi_ctrl -m 12 -d 4; then
  L085:         touch /tmp/3rd_rw_attached
  L086:     else
  L087:         echo "error! 3rd_rw partition can't be attached!!!"
  L088:         # exit -1
  L089:     fi
  L090: else
  L091:     echo "3rd_rw partition is already attached!!!"
  L092: fi
  L097: if [ -f /tmp/3rd_rw_attached ]; then
  L098:     if [ ! -f /tmp/3rd_rw_mounted ]; then
  L099:             if $TIME mount -t ubifs -o no_chk_data_crc -o bulk_read ubi4:3rd_rw /3rd_rw; then
  L100:                 touch /tmp/3rd_rw_mounted
  L101:             else
  L102:                 echo "error! 3rd_rw partition can't be mounted!!!"
  L103:                 # exit -2
  L104:             fi
  L105:     else
  L106:         echo "3rd_rw partition is already mounted!!!"
  L107:     fi
  L108: fi

=== Boot Script Excerpt: basic/autorun.sh (155 total lines) ===
  L076: echo "1 0 0 1920 1080" > /tmp/am_view_port
  L079: if [ -f /basic/ginga/ginga_totvs ]; then
  L081: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/basic/ginga/lib:/3rd/ginga/lib:/3rd/ginga/cvm/lib:/basic:/basic/lib:/3rd/lib:/3rd/qt/lib:/3rd/qt/plugins/imageformats:/3rd/skype:/3rd/opera/opera_dir/video
  L082: fi
  L084: if [ -f /basic/ginga/ginga_tbr ]; then
  L086: export LD_LIBRARY_PATH=/basic/ginga/lib:/3rd/ginga/lib:/3rd/ginga/lib/ncl/ginga:/3rd/ginga/lib/ncl/ginga/converters:/3rd/ginga/lib/ncl/ginga/dp:/basic:/basic/lib:/3rd/lib:/3rd/qt/lib:/3rd/qt/plugins/imageformats:/3rd/skype:/3rd/opera/opera_dir/video
  L087: fi
  L089: export QTDIR=/3rd/qt
  L090: export HOME=/3rd_rw
  L091: export LD_LIBRARY_PATH=/3rd/nsd/lib:$LD_LIBRARY_PATH
  L093: if [ -f /basic/btusb.ko ]; then
  L094: 	echo "==find BT driver, inserting.....="
  L095: 	insmod /basic/btusb.ko 
  L096: fi
  L098: if [ -f /basic/lib/preloadable_libiconv.so ]; then
  L099:   export LD_PRELOAD=/basic/lib/preloadable_libiconv.so
  L100: fi
  L103: export HOME=/3rd
  L104: export QTDIR=/3rd/qt/
  L105: export PATH=$PATH:$QTDIR:$QTDIR/plugins
  L108: export QWS_DISPLAY=directfb
  L109: export QT_DEBUG_PLUGINS=0
  L110: export QT_PLUGIN_PATH=/3rd/qt/plugins
  L111: export QT_QWS_FONTDIR=/3rd/qt/lib/fonts
  L112: export QWS_MOUSE_PROTO=None
  L114: export PATH=$PATH:/3rd_rw/nettv
  L115: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/3rd_rw/nettv:/3rd/qt/qt_lib
  L118: export FREETYPE_FONT_SET=YES
  L119: export OPERA_DIR=/usr/opera/opera_dir
  L120: export OPERA_HOME=/usr/opera/opera_home
  L121: export OPERA_FONTS=/usr/opera/fonts
  L122: export PATH=$PATH:/usr/opera
  L123: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/3rd/nettv:/basic/nettv
  L124: export LD_RRELOAD=/3rd/nettv/libuvabackend-tpvision.so
  L127: export LD_LIBRARY_PATH=/3rd/dmsapp:$LD_LIBRARY_PATH
  L129: if [ -f /etc/config/core_dump ] || [ -f /etc/config/cli ] || [ -f /etc/config/debug ]; then
  L130: echo /tmp/core_%e_sig%s_pid%p > /proc/sys/kernel/core_pattern
  L131: ulimit -c unlimited
  L132: fi
  L142: if [ -x /basic/app_man -a -f /basic/am_config ]; then
  L143: cd /basic; \
  L144: /basic/app_man -c /basic/am_config -s /basic/am_start.ini -input_fifo &
  L145: /basic/tty_man
  L146: else
  L147: if [ -x /basic/dtv_svc ]; then
  L148: /basic/dtv_svc -input_fifo &
  L149: /basic/tty_man
  L150: if [ -x /basic/mtkapp ]; then
  L151: sleep 3
  L152: /basic/mtkapp &
  L153: fi
  L154: fi
  L155: fi

=== Configuration Delta: stock opera.ini vs custom opera_new.ini ===
  [Network] URL Filter File: stock='$OPERA_HOME/urlfilter.ini'  -->  custom='/3rd_rw/nettv/custom/urlfilter.ini'
  [Security Prefs] Enable TLS v1.1: stock='0'  -->  custom='1'
  [Security Prefs] Enable TLS v1.2: stock='0'  -->  custom='1'
  [User Agent] Spoof UserAgent ID: stock='1'  -->  custom='2'
  [User Prefs] Local CSS File: stock='$OPERA_DIR/styles/user.css'  -->  custom='/3rd_rw/nettv/custom/user.css'
  [User Prefs] User JavaScript File: stock='$OPERA_DIR/userjs'  -->  custom='/3rd_rw/nettv/custom/userjs'
```

---

## A.5 Remediated Reference Delivery Artifacts (`custom_payload/`)

### A.5.1 Complete Delivered `opera_new.ini` (`custom_payload/nettv/opera_new.ini`)

```ini
Opera Preferences version 2.1
; Do not edit this file while Opera is running
; This file is stored in UTF-8 encoding

[Extensions]
Scripting=1
Plugins=1
Frames=1

[File Types Extension]
application/ce-html+xml=,0

[Security Prefs]
Enable SSL v2=0
Enable SSL v3=0
Enable TLS v1.0=1
Enable TLS v1.1=1
Enable TLS v1.2=1
OCSP Validate Certificates=0

[User Prefs]
Warn Insecure Form=0
Warn Security Level=0
Enable Cookies=14
Ask For Cookie Confirmation=0
File URLs Enabled=1
Document Mode=1
Show Images=3
Show ScrollBars=1
Scroll Is Pan=0
Offline Mode=0
Scale=100
WBMP Scale=100
Max Window History Lines=50
Max Global History Lines=200
Ignore Unrequested Popups=0
Ignore Target=0
Retarded Image Loading=0
Home URL=http://devtest.mpsdev.com/blueport_VideoStore_ContentPartner1/
Language File
Local CSS File=/3rd_rw/nettv/custom/user.css
Download Directory=$OPERA_HOME/download/
Plugin Path=$OPERA_HOME/plugins
Console Error Log Enabled=1
Console Error Log=$OPERA_HOME/error.log
User JavaScript File=/3rd_rw/nettv/custom/userjs
User JavaScript=1
Exceptions Have Stacktrace=1
User JavaScript on HTTPS=1
Always Load User JavaScript=1
Max Console Messages=1000
Browser JavaScript=0
SSR Max Width=240
Wand Autosubmit=0
Turbo Mode=1
Synchronous decode=0
Maximum Total Cookies=300
User CSS=1
Automatic RAM Cache=1

[Persistent Storage]
Domain Quota Exceeded Handling For localStorage=0
Domain Quota For localStorage=51200
Global Quota For localStorage=512000

[Network]
URL Filter File=/3rd_rw/nettv/custom/urlfilter.ini
Allow Cross Network Navigation=1
Use Spdy2=0
Use Spdy3=0

[Disk Cache]
Enabled=0
Size=20000
Cache Docs=1
Cache Figs=1
Cache Other=1
Cache HTTPS=1
Multimedia Stream Always=1
Multimedia Stream Size=4096
Multimedia Stream in RAM=1
Empty On Exit=0

[Cache]
Figure=20000
Document=6000
ECMAScript=2000
Cache Docs=1
Cache Figs=1

[Visited Link]

[Link]

[Multimedia]
Show Animation=1
Always load favicon=1

[User Agent]
Spoof UserAgent ID=2
```

### A.5.2 Remediated POSIX/BusyBox Performance Script (`custom_payload/patches/run.sh`) & `sm_config.ini`

```sh
#!/bin/sh
# Remediated BusyBox-compliant boot tuning study script (no pidof/pgrep/renice)
echo 10 > /proc/sys/vm/swappiness 2>/dev/null || true
echo 50 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true
echo 4096 > /proc/sys/vm/min_free_kbytes 2>/dev/null || true
echo 5 > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
echo 10 > /proc/sys/vm/dirty_ratio 2>/dev/null || true
echo 1 > /proc/sys/vm/overcommit_memory 2>/dev/null || true
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

for cpu in /sys/devices/system/cpu/cpu*/cpufreq; do
    if [ -d "$cpu" ]; then
        echo performance > "$cpu/scaling_governor" 2>/dev/null || true
    fi
done

for q in /sys/block/mmcblk*/queue /sys/block/sd*/queue; do
    if [ -d "$q" ]; then
        echo 512 > "$q/read_ahead_kb" 2>/dev/null || true
        echo deadline > "$q/scheduler" 2>/dev/null || true
    fi
done

echo 262144 > /proc/sys/net/core/rmem_max 2>/dev/null || true
echo 262144 > /proc/sys/net/core/wmem_max 2>/dev/null || true
echo "4096 87380 262144" > /proc/sys/net/ipv4/tcp_rmem 2>/dev/null || true
echo "4096 65536 262144" > /proc/sys/net/ipv4/tcp_wmem 2>/dev/null || true

# Idempotent /tmp/hosts guard preventing duplicate blocks across invocations
if [ -f /tmp/hosts ] || [ ! -e /tmp/hosts ]; then
    if ! grep -q "adservice.google.com" /tmp/hosts 2>/dev/null; then
        cat << 'EOF_HOSTS' >> /tmp/hosts 2>/dev/null || true
127.0.0.1 adservice.google.com
127.0.0.1 pagead2.googlesyndication.com
127.0.0.1 googleads.g.doubleclick.net
127.0.0.1 pubads.g.doubleclick.net
127.0.0.1 securepubads.g.doubleclick.net
127.0.0.1 stats.g.doubleclick.net
127.0.0.1 www.google-analytics.com
127.0.0.1 ssl.google-analytics.com
127.0.0.1 smartclip.com
127.0.0.1 smartclip.net
127.0.0.1 delivery.yospace.com
127.0.0.1 ad.doubleclick.net
127.0.0.1 static.doubleclick.net
127.0.0.1 m.doubleclick.net
127.0.0.1 ads.rubiconproject.com
127.0.0.1 ib.adnxs.com
127.0.0.1 secure.adnxs.com
127.0.0.1 fastclick.net
127.0.0.1 media.adfrontiers.com
127.0.0.1 tracking.tpvision.com
127.0.0.1 analytics.tpvision.com
127.0.0.1 ad.tpvision.com
127.0.0.1 ads.tpvision.com
127.0.0.1 ad.nettvservices.com
127.0.0.1 ads.nettvservices.com
127.0.0.1 telemetry.philips.com
EOF_HOSTS
    fi
fi

# FD-detached background cleanup using BusyBox `ps | awk` + `kill -9`
(
    sleep 15
    for p in $(ps 2>/dev/null | awk '/auto_detect_camera\.sh/ && !/awk/ {print $1}'); do
        kill -9 "$p" 2>/dev/null || true
    done
) </dev/null >/dev/null 2>&1 &
```

Corresponding required Qt config (`custom_payload/patches/sm_config.ini`):
```ini
[tpvlib]
dynqml=true
debug=false
```

---

## A.6 Verified Network Filter (`urlfilter.ini`) & Stylesheet (`user.css`) Artifacts

Lines `1–82` preserve MediaTek/TPV's stock filesystem exfiltration guard intact, while lines `84–141` append domain-scoped ad/telemetry blocking using Opera INI semicolon (`;`) comments (`custom_payload/nettv/urlfilter.ini`):

```ini
[prefs]
prioritize excludelist=1

[include]
*

[exclude]    
file://
file:///
file://localhost
file://localhost/
file://dev
file://localhost/dev
file://dev/*
file://localhost/dev/*
file://proc
file://localhost/proc
file://proc/*
file://localhost/proc/*
file://tmp/
file://tmp/*
file://localhost/tmp
file://localhost/tmp/
file://localhost/tmp/*
file://home
file://home/*
file://localhost/home
file://localhost/home/*
*/usr
*/usr/
*/3rd
*/3rd/
*/3rd_ro
*/3rd_ro/
*/3rd_rw
*/3rd_rw/
*/_3rd
*/_3rd/
*/basic
*/basic/
*/bin
*/bin/
*/directfb
*/directfb/
*/etc
*/etc/
*/lib
*/lib/
*/mnt
*/mnt/
*/opt
*/opt/
*/sbin
*/sbin/
*/sys
*/sys/
*/var
*/var/
*/3rd/nettv
*/3rd/nettv/
*/opera/fonts
*/opera/fonts/
*/opera/opera_dir
*/opera/opera_dir/
*/opera/opera_home
*/opera/opera_home/
*/3rd_rw
*/3rd_rw/
*/3rd_rw/nettv/browser
*/3rd_rw/nettv/browser/
*/perm
*/perm/
*/perm/*
*/mnt/browser
*/mnt/browser/
*/3rd_ro/key
*/3rd_ro/key/
*/3rd_ro/vsecure
*/3rd_ro/vsecure/
opera:*
about:*
widget:*

; --- Global Ad-Block Exclusions ---
*doubleclick.net*
*google-analytics.com*
*googlesyndication.com*
*googleadservices.com*
*smartclip.com*
*smartclip.net*
*yospace.com*
*adservice.*
*adserver.*
*adtech*
*spotxchange*
*springserve*
*pubmatic*
*rubiconproject*
*criteo*
*taboola*
*outbrain*
*amazon-adsystem*
*advertising.com*
*scorecardresearch.com*
*gemius.pl*
*imrworldwide.com*
*quantserve.com*
*applovin.com*
*unityads*
*adnxs.com*
*zedo.com*
*adcolony.com*
*flashtalking.com*
*innovid.com*
*tremorhub.com*
*moatads.com*
*serving-sys.com*
*tpv-analytics*
*ad.tpvision.com*
*ads.tpvision.com*
*ad.nettvservices.com*
*ads.nettvservices.com*
*pagead*
*popads.net*
*popcash.net*
*yieldmanager*
*exponential.com*
*infolinks.com*
*adroll.com*
*revcontent.com*
*adblade.com*
*adform.net*
*openx.net*
*casalemedia.com*
*tribalfusion.com*
*contextweb.com*
*stickyadstv.com*
*smartadserver.com*
*adspirit.de*
*lijit.com*
*sovrn.com*
```

Delivered Opera TV remote-navigation glyph rules and strict CSS ad-container rules (`custom_payload/nettv/user.css`):

```css
/* AOC LE32S5760 Custom TV Styles + Safe Ad Selector Hiding */
op[code=VK_ENTER] { content: "OK"; }
op[code=VK_MENU] { content: "OPTIONS"; }
op[code=VK_UP] { content: "\2191"; }
op[code=VK_DOWN] { content: "\2193"; }
op[code=VK_LEFT] { content: "\2190"; }
op[code=VK_RIGHT] { content: "\2192"; }
op[code=VK_BACK] { content: "BACK"; }
op[code=VK_INFO] { content: "INFO"; }

.video-ads,
.ytp-ad-module,
.ytp-ad-overlay-container,
.ytp-ad-player-overlay,
.advertisement,
#ad-banner,
.banner-ad,
.tv-ad-banner,
.smart-ad,
#portal-ad-box,
.nettv-ad-banner,
.ad_unit,
.ad-slot,
.sponsored-post,
.sponsor-box,
[data-ad-slot] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}
```

---

## A.7 Complete ELF32 Dynamic Linkage Output (`evidence/06_systemmanager_and_nettv_disasm.txt`)

```text
=== ELF Audit: SystemManager (9,438,748 bytes) ===
  e_type=2 (ET_EXEC), entry=0x00018d18, soname=None
  RPATH/RUNPATH: /home/mtkvm/qtbuild/osslibrary/451_vfp_ca9/qt-4.8.3-dfb1.4.1/lib
  Sections: .dynsym@0x9ef4(off=0x1ef4,sz=0x3640), .text@0x18d18(off=0x10d18,sz=0x22f348), .rodata@0x248068(off=0x240068,sz=0x6436ac), .dynamic@0x90f248(off=0x8ff248,sz=0x170), .got@0x90f3b8(off=0x8ff3b8,sz=0xcc8), .data@0x910080(off=0x900080,sz=0x18), .bss@0x910098(off=0x900098,sz=0x1500)
  DT_NEEDED (17): libQtDeclarative.so.4, libQtScript.so.4, libQtSql.so.4, libQtXml.so.4, libQtGui.so.4, libdirectfb.so, libpng.so.3, libjpeg.so.62, libfreetype.so.6, libz.so.1, libQtNetwork.so.4, libQtCore.so.4, libpthread.so.0, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6

=== ELF Audit: dtv_svc (4,255,100 bytes) ===
  e_type=2 (ET_EXEC), entry=0x000329d8, soname=None
  Sections: .dynsym@0xd8fc(off=0x58fc,sz=0xbe90), .text@0x329d8(off=0x2a9d8,sz=0x2fe7f0), .rodata@0x3311d0(off=0x3291d0,sz=0x56b3c), .dynamic@0x410f48(off=0x400f48,sz=0x228), .got@0x411170(off=0x401170,sz=0x2760), .data@0x4138d0(off=0x4038d0,sz=0xaeac), .bss@0x41e780(off=0x40e77c,sz=0x9fe90)
  DT_NEEDED (41): libhttplive.so, libsmartfs.so, libdtv_common.so, libpng.so.3, libjpeg.so.62, libfreetype.so.6, libz.so.1, libsecurestorage.so, libmtal.so, libdirectfb.so, librpc_ipc.so, libconfig_parser.so, libpthread.so.0, librt.so.1, libdl.so.2, libnetwork_detect.so, libmw_if2.so, libginga_tbr_pic.so, libcmpb.so, libhandle_app.so, libmtkapp.so, libapp_if.so, libcrypto.so.1.0.0, libssl.so.1.0.0, libcurl.so.4, libcares.so.2, libBasicUsageEnvironment.so, libgroupsock.so, libliveMedia.so, libUsageEnvironment.so, libwfd.so, libhdcp2x.so, libtommath.so, libtomcrypt.so, libexpat.so.1, libmtkdrm.so, libsqlite_3_7_2.so, libnettv_proxy.so, libcursor.so, libgcc_s.so.1, libc.so.6

=== ELF Audit: libnettv.so (2,749,744 bytes) ===
  e_type=3 (ET_DYN), entry=0x000acc10, soname=None
  Sections: .dynsym@0xc89c(off=0xc89c,sz=0x1d160), .text@0xacc10(off=0xacc10,sz=0x181500), .rodata@0x22e118(off=0x22e118,sz=0x3afbe), .dynamic@0x29dd80(off=0x295d80,sz=0x200), .got@0x29df80(off=0x295f80,sz=0x5268), .data@0x2a31e8(off=0x29b1e8,sz=0x3dec), .bss@0x2a6fd8(off=0x29efd4,sz=0xa0a58)
  DT_NEEDED (36): libSSPK.so, libmtkdrm.so, libmarlin.so, libhttplive.so, libexpat.so.1, libcurl.so.4, libssl.so.1.0.0, libcrypto.so.1.0.0, libdirectfb.so, libpthread.so.0, libdl.so.2, libcares.so.2, libsecurestorage.so, libmtal.so, libpng.so.3, libcmpb.so, libdtv_common.so, libhandle_app.so, libapp_if.so, librpc_ipc.so, libapp_if_rpc.so, libjpeg.so.62, libfreetype.so.6, libxml2.so.2, libWVPlaybackAPI.so, libWVStreamControlAPI.so, libmtk_hw_decrypt.so, libz.so.1, libcursor.so, libplayready.so, libPRGlue.so, libuvabackend-mtk.so, libuvadrmbackend-clearkey.so, libuvadrmbackend-playready.so, libgcc_s.so.1, libc.so.6

=== ELF Audit: libopera_hbbtv.so (15,717,224 bytes) ===
  e_type=3 (ET_DYN), entry=0x000b3fa8, soname='libopera_hbbtv.so'
  Sections: .dynsym@0x2458(off=0x2458,sz=0x4d00), .text@0xb3fa8(off=0xb3fa8,sz=0xae21bc), .rodata@0xb96170(off=0xb96170,sz=0xb1af4), .dynamic@0xf038a8(off=0xefb8a8,sz=0x118), .got@0xf039c0(off=0xefb9c0,sz=0xec8), .data@0xf04888(off=0xefc888,sz=0x588), .bss@0xf04e10(off=0xefce10,sz=0x6144)
  DT_NEEDED (7): libpthread.so.0, libdl.so.2, libopera_hbbtv_appman.so, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6

=== ELF Audit: browser.out (803,228 bytes) ===
  e_type=2 (ET_EXEC), entry=0x000118d0, soname=None
  Sections: .dynsym@0x95d0(off=0x15d0,sz=0x3070), .text@0x118d0(off=0x98d0,sz=0x848e8), .rodata@0x961c0(off=0x8e1c0,sz=0x2d2cf), .dynamic@0xd26f8(off=0xc26f8,sz=0x180), .got@0xd2878(off=0xc2878,sz=0x284), .data@0xd2afc(off=0xc2afc,sz=0x111c), .bss@0xd3c18(off=0xc3c18,sz=0x9fa8)
  DT_NEEDED (20): libc.so.6, libm.so.6, librt.so.1, libstdc++.so.6, libdirectfb.so, libjpeg.so.62, libpng.so.3, libz.so.1, libfreetype.so.6, libpng12.so.0, libopera_hbbtv.so, libopera_hbbtv_appman.so, libuva.so, libuvabackend-capi.so, libuvabackend-tpvision.so, libhtvLib.so, libTrace.so, libpthread.so.0, libgcc_s.so.1, libdl.so.2

=== ELF Audit: netflix (10,201,088 bytes) ===
  e_type=2 (ET_EXEC), entry=0x002355c8, soname=None
  RPATH/RUNPATH: $ORIGIN:/release/auto/p4/w/20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/third_party/cust_app/TPV_Vision/TPV/mbtaudio:/release/auto/p4/w/20150420_194932/TPV_linux_REL_PHILIPS_2K14/vm_linux/oss/library/gnuarm-4.5.1_vfp_ca9/c-ares/cares-1.7.4/lib:...
  Sections: .dynsym@0x2e214(off=0x26214,sz=0x58060), .text@0x2355c8(off=0x22d5c8,sz=0x62a580), .rodata@0x85fb50(off=0x857b50,sz=0x411e8), .dynamic@0x9c5520(off=0x9b5520,sz=0x1e0), .got@0x9c5700(off=0x9b5700,sz=0x3840), .data@0x9c8f40(off=0x9b8f40,sz=0x1304), .bss@0x9ca248(off=0x9ba244,sz=0x5a94)
  DT_NEEDED (31): libdl.so.2, librt.so.1, libapp_client.so, libmng.so.1, libwebp.so.4, libpng.so.3, libjpeg.so.62, libJavaScriptCore.so, libWTF.so, libcares.so.2, libfreetype.so.6, libdirectfb.so, libpthread.so.0, libz.so.1, libcurl.so.4, libssl.so.1.0.0, libcrypto.so.1.0.0, libexpat.so.1, libsecurestorage.so, libcmpb.so, librpc_ipc.so, libhandle_app.so, libapp_if.so, libapp_if_rpc.so, libmtal.so, libplayready.so, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6, libdtv_common.so

=== ELF Audit: wrp_leanback (17,740 bytes) ===
  e_type=2 (ET_EXEC), entry=0x00008bec, soname=None
  Sections: .dynsym@0x82d8(off=0x2d8,sz=0x2d0), .text@0x8bec(off=0xbec,sz=0x1d0c), .rodata@0xa900(off=0x2900,sz=0xbf8), .dynamic@0x13604(off=0x3604,sz=0x198), .got@0x1379c(off=0x379c,sz=0x84), .data@0x13820(off=0x3820,sz=0x7a8), .bss@0x13fc8(off=0x3fc8,sz=0x4)
  DT_NEEDED (23): libapp_if.so, libdtv_common.so, libhandle_app.so, librpc_ipc.so, libapp_if_rpc.so, libsecurestorage.so, libmtal.so, libcurl.so.4, libcares.so.2, libssl.so.1.0.0, libcrypto.so.1.0.0, libexpat.so.1, libdirectfb.so, libpng.so.3, libjpeg.so.62, libfreetype.so.6, libz.so.1, libpthread.so.0, librt.so.1, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6

=== ELF Audit: libmtkapp.so (32,794,624 bytes) ===
  e_type=3 (ET_DYN), entry=0x001132f8, soname=None
  Sections: .dynsym@0x1966c(off=0x1966c,sz=0x39c80), .text@0x1132f8(off=0x1132f8,sz=0x43aa84), .rodata@0x54dd88(off=0x54dd88,sz=0x816ec), .dynamic@0x68a8ec(off=0x6828ec,sz=0x188), .got@0x68aa74(off=0x682a74,sz=0xb60c), .data@0x696080(off=0x68e080,sz=0x18b81b9), .bss@0x1f4e240(off=0x1f46239,sz=0x2ed544)
  DT_NEEDED (21): libdtv_common.so, libpng.so.3, libjpeg.so.62, libfreetype.so.6, libz.so.1, libsecurestorage.so, libmtal.so, libdirectfb.so, libapp_if.so, libpthread.so.0, librt.so.1, libdl.so.2, libcmpb.so, libnettv_proxy.so, libcrypto.so.1.0.0, libssl.so.1.0.0, libcurl.so.4, libcares.so.2, libsmartfs.so, libgcc_s.so.1, libc.so.6

=== ELF Audit: libdtv_common.so (2,153,828 bytes) ===
  e_type=3 (ET_DYN), entry=0x0003b420, soname=None
  Sections: .dynsym@0x67d8(off=0x67d8,sz=0xef80), .text@0x3b420(off=0x3b420,sz=0x148f28), .rodata@0x184350(off=0x184350,sz=0x4963c), .dynamic@0x209d58(off=0x201d58,sz=0x158), .got@0x209eb0(off=0x201eb0,sz=0x2720), .data@0x20c5d0(off=0x2045d0,sz=0x91f8), .bss@0x2157c8(off=0x20d7c8,sz=0x5b80c)
  DT_NEEDED (16): libpthread.so.0, libpng.so.3, libjpeg.so.62, libfreetype.so.6, libz.so.1, libdirectfb.so, libstdc++.so.6, libmtal.so, libcrypto.so.1.0.0, libssl.so.1.0.0, libcurl.so.4, libcares.so.2, libsmartfs.so, libsecurestorage.so, libgcc_s.so.1, libc.so.6
```

---

## A.8 Factory StageCraft (`leanback/config.ini`) & `3rd_rw_list.txt` Provenance

```ini
# extracted/rootfs1/leanback/config.ini (verbatim MediaTek StageCraft wrapper config)
[mtkfl]
enable = amclient,dockui,statemachine,system
disable = netdetect,usbdetect

[amclient]
name = stagecraft

[statemachine]
change_state_timeout = 0

[stagecraft]
key_repeat_interval = 800
key_repeat_period = 400
dfb_surface_lock = 1
dfb_double_buffer = 0
termination_timeout = 20000
ignore_key_src_bits = 1
net_action_timeout = 60000
urlstream_retry = 0
urlstream_patch = 1
curl_connection_timeout = 20
log_error = 1
log_warning = 1
log_info = 1
log_trace = 0
ext_image_format = 1

[cmpb]
log_trace_playback = 0
pts_from_pos = 1
```

