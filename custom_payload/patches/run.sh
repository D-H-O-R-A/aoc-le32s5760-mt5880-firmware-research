#!/bin/sh
###############################################################################
# AOC LE32S5760 (MT5880) - Deep System Performance & Customization Script
# Executed automatically by /etc/rc.d/rc.local on boot with root privileges
###############################################################################

echo "=========================================================="
echo "[AOC CUSTOM] Executando otimizacoes profundas do sistema..."
echo "=========================================================="

# 1. Linux Virtual Memory & Kernel Performance Tuning
# Eliminate stutter, paging latency, and memory allocation stalls on 512MB RAM
echo 10 > /proc/sys/vm/swappiness 2>/dev/null || true
echo 50 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true
echo 4096 > /proc/sys/vm/min_free_kbytes 2>/dev/null || true
echo 5 > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
echo 10 > /proc/sys/vm/dirty_ratio 2>/dev/null || true
echo 1 > /proc/sys/vm/overcommit_memory 2>/dev/null || true
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# 2. CPU Performance Governor
for cpu in /sys/devices/system/cpu/cpu*/cpufreq; do
    if [ -d "$cpu" ]; then
        echo performance > "$cpu/scaling_governor" 2>/dev/null || true
    fi
done

# 3. Flash Storage / MMC I/O Optimization
for q in /sys/block/mmcblk*/queue /sys/block/sd*/queue; do
    if [ -d "$q" ]; then
        echo 512 > "$q/read_ahead_kb" 2>/dev/null || true
        echo deadline > "$q/scheduler" 2>/dev/null || true
    fi
done

# 4. Network Stack Optimization (Smooth streaming without jitter)
echo 262144 > /proc/sys/net/core/rmem_max 2>/dev/null || true
echo 262144 > /proc/sys/net/core/wmem_max 2>/dev/null || true
echo "4096 87380 262144" > /proc/sys/net/ipv4/tcp_rmem 2>/dev/null || true
echo "4096 65536 262144" > /proc/sys/net/ipv4/tcp_wmem 2>/dev/null || true

# 5. Global Ad & Telemetry Blocking via /tmp/hosts (/etc/hosts symlink, idempotent)
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

# 6. Background Cleanup (BusyBox-compatible; TV BusyBox lacks pidof/pgrep/renice)
(
    sleep 15
    for p in $(ps 2>/dev/null | awk '/auto_detect_camera\.sh/ && !/awk/ {print $1}'); do
        kill -9 "$p" 2>/dev/null || true
    done
) </dev/null >/dev/null 2>&1 &

echo "[AOC CUSTOM] Otimizacoes aplicadas com sucesso!"
exit 0
