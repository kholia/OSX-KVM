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

display_help() {
    echo "USAGE: $(basename "$0") [OPTIONAL ARGS]"
    echo -e "\nThe arguments, in order, are:\n1) The amount of RAM (in MiB)\n2) The number of CPU sockets\n3) The number of CPU cores\n4) The number of CPU threads"
    echo -e "\nThe default values are:\n1) 3072\n2) 1\n3) 2\n4) 4"
}

if [ $# -eq 0 ]; then
    ALLOCATED_RAM="3072" # MiB
    CPU_SOCKETS="1"
    CPU_CORES="2"
    CPU_THREADS="4"
    echo "Please take into account that the default values for the memory and CPU will be used (3 GB RAM, 1 CPU socket, 2 cores, 4 threads)"

    echo -e "\nALLOCATED RAM: $ALLOCATED_RAM MB"
    echo "CPU SOCKETS: $CPU_SOCKETS"
    echo "CPU CORES: $CPU_CORES"
    echo "CPU THREADS: $CPU_THREADS"
elif [ $# -eq 1 ] && [ $1 == "-h" ]; then
    display_help
elif [ $# -eq 4 ]; then
    ALLOCATED_RAM="$1 MB"
    CPU_SOCKETS="$2"
    CPU_CORES="$3"
    CPU_THREADS="$4"

    echo -e "\nALLOCATED RAM: $ALLOCATED_RAM"
    echo "CPU SOCKETS: $CPU_SOCKETS"
    echo "CPU CORES: $CPU_CORES"
    echo "CPU THREADS: $CPU_THREADS"
else
    echo "Please suppy a valid number of arguments! (0 for default values or 4 to specify them yourself. View \"-h\" for more info.)"

fi

REPO_PATH="."
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
