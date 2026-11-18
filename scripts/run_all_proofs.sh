#!/bin/sh
set -eu

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WS_DIR="${1:-$(cd "$REPO_DIR/.." && pwd)}"
EV_DIR="$REPO_DIR/evidence"
mkdir -p "$EV_DIR"

python3 "$REPO_DIR/scripts/inspect_pkg_and_nfsb.py" \
  --pkg "$WS_DIR/extracted/upgrade_loader.pkg" \
  --custom-pkg "$WS_DIR/build/custom_upgrade_loader.pkg" \
  --vmlinux "$WS_DIR/scratch/vmlinux.bin" \
  > "$EV_DIR/01_pkg_and_nfsb_proof.txt"

python3 "$REPO_DIR/scripts/disasm_secure_boot_chain.py" \
  --uboot "$WS_DIR/extracted/uboot.bin" \
  --vmlinux "$WS_DIR/scratch/vmlinux.bin" \
  > "$EV_DIR/02_secure_boot_chain_disasm.txt"

python3 "$REPO_DIR/scripts/disasm_upg_installer.py" \
  --libmtkapp "$WS_DIR/extracted/appfs1/basic/libmtkapp.so" \
  --libdtv "$WS_DIR/extracted/appfs1/basic/libdtv_common.so" \
  > "$EV_DIR/03_upg_installer_disasm.txt"

python3 "$REPO_DIR/scripts/verify_upg_container.py" \
  --upg "$WS_DIR/build/Autorun.upg" \
  --pubkey "$WS_DIR/extracted/ro_data_keys/TPV_MTK2K14PLF_LT0_UPG_PubKey_Prod.pem" \
  --aes-key "$WS_DIR/extracted/ro_data_keys/TPV_MTK2K14PLF_LT0_UPG_AES_Prod.key" \
  --aes-iv "$WS_DIR/extracted/ro_data_keys/TPV_MTK2K14PLF_LT0_UPG_AES_Prod.iv" \
  > "$EV_DIR/04_upg_container_crypto_proof.txt"

python3 "$REPO_DIR/scripts/inspect_runtime_engines.py" \
  --workspace "$WS_DIR" \
  --repo "$REPO_DIR" \
  > "$EV_DIR/05_runtime_engines_and_busybox_audit.txt"

python3 "$REPO_DIR/scripts/disasm_systemmanager_and_nettv.py" \
  --workspace "$WS_DIR" \
  > "$EV_DIR/06_systemmanager_and_nettv_disasm.txt"

python3 "$REPO_DIR/scripts/inspect_dmbht_and_boot_scripts.py" \
  --workspace "$WS_DIR" \
  --repo "$REPO_DIR" \
  > "$EV_DIR/07_dmbht_and_boot_scripts_audit.txt"

echo "All proofs executed successfully. Evidence written to $EV_DIR"
ls -lh "$EV_DIR"
