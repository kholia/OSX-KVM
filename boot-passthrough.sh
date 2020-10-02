#!/usr/bin/env bash

# Special thanks to:
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt
#
# qemu-img create -f qcow2 mac_hdd_ng.img 128G
#
# echo 1 > /sys/module/kvm/parameters/ignore_msrs (this is required)

############################################################################
# NOTE: Tweak the "MY_OPTIONS" line in case you are having booting problems!
############################################################################

MY_OPTIONS="+pcid,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check"

# This script works for Big Sur, Catalina, Mojave, and High Sierra. Tested with
# macOS 10.15.6, macOS 10.14.6, and macOS 10.13.6

ALLOCATED_RAM="3072" # MiB
CPU_SOCKETS="1"
CPU_CORES="2"
CPU_THREADS="4"

REPO_PATH="./"
OVMF_DIR="."

# Note: This script assumes that you are doing CPU + GPU passthrough. This
# script will need to be modified for your specific needs!
#
# We recommend doing the initial macOS installation without using passthrough
# stuff. In other words, don't use this script for the initial macOS
# installation.

# shellcheck disable=SC2054
args=(
  -enable-kvm -m "$ALLOCATED_RAM" -cpu host,vendor=GenuineIntel,kvm=on,vmware-cpuid-freq=on,+invtsc,+hypervisor
  -machine pc-q35-2.9
  -smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS"
  -vga none
  -device pcie-root-port,bus=pcie.0,multifunction=on,port=1,chassis=1,id=port.1
  -device vfio-pci,host=01:00.0,bus=port.1,multifunction=on
  -device vfio-pci,host=01:00.1,bus=port.1
  -usb -device usb-kbd -device usb-tablet
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
  -drive if=pflash,format=raw,readonly,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd"
  -drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1024x768.fd"
  -smbios type=2
  -drive id=MacHDD,if=none,file=./mac_hdd_ng.img
  -device ide-drive,bus=sata.2,drive=MacHDD
  -drive id=OpenCoreBoot,if=none,snapshot=on,format=qcow2,file="$REPO_PATH/OpenCore-Catalina/OpenCore-Passthrough.qcow2"
  -device ide-hd,bus=sata.3,drive=OpenCoreBoot
  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27
  -monitor stdio
  -display none
)

qemu-system-x86_64 "${args[@]}"
