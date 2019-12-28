#!/usr/bin/env bash
set -euo pipefail

args=()

# shellcheck disable=SC1091
source ./common-macOS-NG.sh

# shellcheck disable=SC2054,SC2191
args+=(
  # Error: Device 'InstallMedia' is writable but does not support snapshots
  -device ide-hd,bus=sata.3,drive=InstallMedia
  -drive id=InstallMedia,if=none,file=BaseSystem.img,format=raw
)

qemu-img convert ../BaseSystem.dmg -O raw BaseSystem.img
qemu-img create -f qcow2 mac_hdd_ng.img 32G
qemu-img convert -p -f raw ../OVMF_CODE.fd -O qcow2 OVMF_CODE.qcow2
qemu-img convert -p -f raw ../OVMF_VARS-1024x768.fd -O qcow2 OVMF_VARS-1024x768.qcow2
qemu-img convert -p -f qcow2 ../Mojave/CloverNG.qcow2 -O qcow2 CloverNG.qcow2

qemu-system-x86_64 "${args[@]}"
