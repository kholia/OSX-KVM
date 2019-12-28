#!/usr/bin/env bash
set -euo pipefail

args=()

# shellcheck disable=SC1091
source ./common-macOS-NG.sh

# shellcheck disable=SC2054,SC2191,SC2034
args+=(
  -netdev user,id=net0 -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
)

qemu-system-x86_64 "${args[@]}"
