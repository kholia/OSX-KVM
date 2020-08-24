#!/usr/bin/env bash

ALLOCATED_RAM="3072" # MiB
CPU_SOCKETS="1"
CPU_CORES="2"
CPU_THREADS="4"

REPO_PATH="./"
OVMF_DIR="."

# shellcheck disable=SC2054
args=(
  -enable-kvm -m "$ALLOCATED_RAM" -cpu host,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on
  -machine pc-q35-2.9
  -smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS"
  -vga none
  -device pcie-root-port,bus=pcie.0,multifunction=on,port=1,chassis=1,id=port.1
  -device vfio-pci,host=01:00.0,bus=port.1,multifunction=on
  -device vfio-pci,host=01:00.1,bus=port.1
  -usb -device usb-kbd -device usb-tablet
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
  -drive if=pflash,format=raw,readonly,file=OVMF_CODE.fd
  -drive if=pflash,format=raw,file=OVMF_VARS.fd
  -smbios type=2
  -drive id=MacHDD,if=none,file=./mac_hdd.img
  -device ide-drive,bus=sata.2,drive=MacHDD
  -drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file="$REPO_PATH/OpenCore-Catalina/OpenCore-Passthrough.qcow2"
  -device ide-hd,bus=sata.3,drive=OpenCoreBoot
  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -monitor stdio
  -display none
)

qemu-system-x86_64 "${args[@]}"
