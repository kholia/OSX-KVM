#!/usr/bin/env bash

# Special thanks to...
# https://github.com/foxlet/macOS-Simple-KVM
# https://github.com/Leoyzen/KVM-Opencore
# https://github.com/thenickdude/KVM-Opencore/
# https://github.com/qemu/qemu/blob/master/docs/usb2.txt

ALLOCATED_RAM="3072" # MiB
CPU_SOCKETS="1"
CPU_CORES="2"
CPU_THREADS="4"

REPO_PATH="./"
OVMF_DIR="."

qemu-system-x86_64 -enable-kvm -m "$ALLOCATED_RAM" -cpu host,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on \
	-machine pc-q35-2.9 -usb \
	-smp "$CPU_THREADS",cores="$CPU_CORES",sockets="$CPU_SOCKETS" \
	-drive if=pflash,format=raw,readonly,file="$REPO_PATH/$OVMF_DIR/OVMF_CODE.fd" \
	-drive if=pflash,format=raw,file="$REPO_PATH/$OVMF_DIR/OVMF_VARS-1024x768.fd" \
	-drive id=MacHDD,if=none,file=$REPO_PATH/mac_hdd.img \
	-smbios type=2 \
	-device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
	-device usb-kbd -device usb-tablet \
	-device pcie-root-port,bus=pcie.0,multifunction=on,port=1,chassis=1,id=port.1 \
	-device vfio-pci,host=01:00.0,bus=port.1,multifunction=on \
	-device vfio-pci,host=01:00.1,bus=port.1 \
	-device ide-drive,bus=ide.2,drive=MacHDD \
	-netdev tap,id=net0,ifname=tap0,script=no,downscript=no -device vmxnet3,netdev=net0,id=net0,mac=52:54:00:c9:18:27 \
	-monitor stdio \
	-vga none -display none
